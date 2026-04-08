from tools.mcp_wrappers import create_calendar_event, get_calendar_availability
from tools.db_tools import log_system_action
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_vertexai import ChatVertexAI
import os
import datetime

def schedule_worker_node(state):
    """Schedule worker handles Calendar and basic DB logs."""
    print("---SCHEDULE WORKER EXECUTION---")
    messages = state["messages"]
    last_message = messages[0].content.lower()
    
    outputs = []
    
    target_iso = None
    event_name = "Scheduled Meeting"
    # Remove rigid keyword gates since Supervisor correctly routed us here
    try:
        from vertexai.generative_models import GenerativeModel
        model = GenerativeModel("gemini-2.5-flash")
        prompt_text = f"Extract the requested meeting title and meeting time from the user text. Output EXACTLY the format 'TITLE|ISO_DATETIME'. For example: 'Team Sync|2026-04-09T15:00:00'. Assume all dates are relative to now (Current local time: {datetime.datetime.now().isoformat()}). If no specific title is requested, create a brief 1-4 word appropriate title. If no specific time is requested, use NONE for the time. Do NOT output markdown formatting like ``` or backticks. \n\nUser Text: {last_message}"
        iso_res = model.generate_content(prompt_text).text.strip()
        print(f"Calendar Extractor returned raw: {iso_res}")
        
        # Strip potential leftover markdown
        iso_res = iso_res.replace('`', '').strip()
        
        if '|' in iso_res:
            parts = iso_res.split('|')
            event_name = parts[0].strip()
            extracted_time = parts[1].strip()
            if extracted_time and extracted_time != "NONE":
                target_iso = extracted_time
        else:
            if iso_res and iso_res != "NONE":
                target_iso = iso_res
    except Exception as e:
        print(f"Extraction failed: {e}")
        
    duration = 30
    res = create_calendar_event(event_name, duration, target_iso)
    outputs.append(res)
    
    # Always log an action
    log_res = log_system_action("Schedule worker processed request.")
    outputs.append(log_res)
    
    from langchain_core.messages import AIMessage
    return {
        "active_context": outputs,
        "completed_workers": ["Schedule_Worker"],
        "messages": [AIMessage(content=f"Schedule Worker executed: {'; '.join(outputs)}. Proceed with the next pending task or FINISH.")]
    }
