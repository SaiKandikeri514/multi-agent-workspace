import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_vertexai import ChatVertexAI
from langchain_core.messages import AIMessage
from pydantic import BaseModel, Field

class RouterOutput(BaseModel):
    next_agent: str = Field(description="The next agent to route to. Options: 'Support_Worker', 'Schedule_Worker', 'General_Worker', or 'FINISH'.")
    reasoning: str = Field(description="Brief explanation of why you chose this route.")


def create_supervisor_node():
    """Builds the supervisor node logic."""
    
    # Try initializing Vertex AI. If it fails (due to missing creds locally), 
    # we can catch it during execution or provide a direct fallback logic.
    try:
        # GCP Cloud Run automatically provides GOOGLE_CLOUD_PROJECT
        project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", "hackathonx-492420")
        llm = ChatVertexAI(model="gemini-2.5-flash", project=project_id, max_retries=1)
        structured_llm = llm.with_structured_output(RouterOutput)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", 
             "You are the Enterprise Supervisor AI. Analyze the user request and delegate to exactly one worker at a time.\n"
             "Capabilities:\n"
             "- 'Support_Worker': handles Jira tickets, issue lookup, and CRM data.\n"
             "- 'Schedule_Worker': handles calendar bookings and database logging.\n"
             "- 'General_Worker': handles general inquiries, answering questions, or checking time.\n"
             "- 'FINISH': If ALL parts of the user's overarching task are fully completed by the workers.\n"
             "\n"
             "COMPLETED ACTIONS LOG:\n"
             "{active_context}\n"
             "\n"
             "CRITICAL RULE: Review the user request. If a worker has ALREADY executed (see COMPLETED LOG), you MUST NOT route to it again. If all requested actions are fulfilled, you MUST return FINISH."
            ),
            ("placeholder", "{messages}"),
        ])
        
        chain = prompt | structured_llm
        return chain
    except Exception as e:
        # Fallback dummy for UI testing if no GCP creds present yet
        print("Warning: Could not initialize VertexAI. Using Fallback Supervisor.")
        def fallback_chain(state):
            last_msg = str(state['messages'][-1].content).lower()
            if "schedule" in last_msg or "calendar" in last_msg or "book" in last_msg:
                return RouterOutput(next_agent="Schedule_Worker", reasoning="Detected calendar intent.")
            elif "jira" in last_msg or "crm" in last_msg or "ticket" in last_msg or "outage" in last_msg:
                return RouterOutput(next_agent="Support_Worker", reasoning="Detected support intent.")
            elif "time" in last_msg or "date" in last_msg or "hello" in last_msg:
                return RouterOutput(next_agent="General_Worker", reasoning="Detected general/time query intent.")
            return RouterOutput(next_agent="FINISH", reasoning="Task complete or unsupported.")
        return fallback_chain

def supervisor_node(state):
    """The LangGraph node execution function for the supervisor."""
    print("---SUPERVISOR ROUTING---")
    chain = create_supervisor_node()
    
    # Format context cleanly so LLM reads it perfectly
    ctx_list = state.get("active_context", [])
    context_str = "\n".join(ctx_list) if ctx_list else "No actions completed yet."
    
    res = chain.invoke({
        "messages": state["messages"],
        "active_context": context_str
    })
    
    # HARD CIRCUIT BREAKER built on structurally strict completed_workers list
    completed = state.get("completed_workers", [])
    if res.next_agent in completed:
        print(f"--- CIRCUIT BREAKER ACTIVATED for {res.next_agent} ---")
        if res.next_agent == "Support_Worker":
             if "Schedule_Worker" not in completed and "calendar" in state["messages"][0].content.lower():
                 res.next_agent = "Schedule_Worker"
             else:
                 res.next_agent = "FINISH"
        elif res.next_agent == "Schedule_Worker":
             res.next_agent = "FINISH"
             
    # Failsafe if it somehow hallucinates FINISH but then we don't catch it
    if "FINISH" in res.next_agent:
        res.next_agent = "FINISH"
    
    # Add reasoning to context for UI
    ui_context = [f"Supervisor decided to route to {res.next_agent} because: {res.reasoning}"]
    
    return {
        "next_agent": res.next_agent,
        "active_context": ui_context,
        "completed_workers": ["Supervisor"]
    }
