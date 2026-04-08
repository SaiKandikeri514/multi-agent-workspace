import os
from langchain_core.messages import ToolMessage
from tools.mcp_wrappers import create_jira_issue, search_jira_issues, close_jira_issue
from tools.db_tools import search_crm_customer, upsert_crm_status

# In langgraph, workers typically use LLMs paired with exact tools.
# For demo purposes, we will execute a lightweight tool-calling loop or just use native python logic if LLM is unavailable.

from langchain_core.tools import tool
from langchain_google_vertexai import ChatVertexAI

@tool
def _handle_jira_ticket(summary: str, description: str, issue_type: str):
    """Creates a Support Jira Ticket."""
    return create_jira_issue("MDP", summary, description, issue_type)

@tool
def _close_jira_ticket(issue_key: str):
    """Closes an existing Jira Ticket."""
    return close_jira_issue(issue_key)

@tool
def _check_crm(company_name: str):
    """Checks the CRM for a company record."""
    return search_crm_customer(company_name)

SUPPORT_TOOLS = [_handle_jira_ticket, _close_jira_ticket, _check_crm]

def support_worker_node(state):
    """Support worker handles Jira and CRM requests."""
    print("---SUPPORT WORKER EXECUTION---")
    messages = state["messages"]
    last_message = messages[0].content.lower()
    
    outputs = []
    
    # 1. Use GenAI to orchestrate and extract intent/metadata
    try:
        from vertexai.generative_models import GenerativeModel
        import json
        model = GenerativeModel("gemini-2.5-flash")
        prompt = (
            f"You are a professional support orchestration layer. Analyze the user's text and extract a structured JSON. \n"
            f"REQUIRED KEYS:\n"
            f"- 'action': exactly either 'create', 'close', or 'none'.\n"
            f"- 'company_name': the name of the company mentioned (if any).\n"
            f"- 'issue_type': 'Bug', 'Task', or 'Epic' (default to 'Bug' for tickets).\n"
            f"- 'summary': professional subject line for a ticket.\n"
            f"- 'description': the original core issue or context.\n"
            f"- 'issue_key': if closing, provide the key like 'MDP-8'.\n"
            f"Return ONLY raw valid JSON and no markdown formatting.\n\n"
            f"User text: {last_message}"
        )
        res = model.generate_content(prompt).text.strip()
        res = res.replace('```json', '').replace('```', '').strip()
        data = json.loads(res)
        
        action = data.get('action', 'none').lower()
        comp_name = data.get('company_name')
        
        # 2. Automatically sync with CRM if a company is mentioned
        crm_context = ""
        if comp_name:
            # Handle potential partial matches or common aliases
            crm_res = _check_crm.invoke({"company_name": comp_name})
            if "Company:" in crm_res:
                outputs.append(f"CRM Sync: Successfully retrieved context for {comp_name}.")
                crm_context = f"\n\n[CRM CONTEXT: {crm_res.replace('Company:', '').strip()}]"
                # Update status to alert if it was an outage
                if "outage" in last_message:
                    upsert_crm_status(comp_name, "Critical Outage Reported")

        # 3. Handle Jira Logic
        if action == 'close' and 'issue_key' in data:
            res_jira = _close_jira_ticket.invoke({"issue_key": data['issue_key']})
            outputs.append(f"Jira Action: {res_jira}")
        
        elif action == 'create':
            summary_ext = data.get('summary', 'Support Ticket')
            # ENRICH DESCRIPTION WITH CRM CONTEXT
            desc_ext = data.get('description', 'Reported via AI.') + crm_context
            itype_ext = data.get('issue_type', 'Bug').capitalize()
            
            res_jira = _handle_jira_ticket.invoke({"summary": summary_ext, "description": desc_ext, "issue_type": itype_ext})
            outputs.append(f"Jira Action: {res_jira}")

    except Exception as e:
        outputs.append(f"Support Extraction Error: {e}")
        # Final fallback for basic ticket creation if AI pipeline fails
        if "ticket" in last_message or "jira" in last_message:
            res_jira = _handle_jira_ticket.invoke({"summary": "System Alert", "description": last_message, "issue_type": "Bug"})
            outputs.append(f"Fallback Jira Action: {res_jira}")
        
    if not outputs:
        # default response
        outputs.append("Support Worker reviewed request but took no specific Jira/CRM action.")
        
    # Return UI context and append to messages for the Supervisor
    from langchain_core.messages import AIMessage
    return {
        "active_context": outputs,
        "completed_workers": ["Support_Worker"],
        "messages": [AIMessage(content=f"Support Worker executed: {'; '.join(outputs)}. Proceed with the next pending task or FINISH.")]
    }
