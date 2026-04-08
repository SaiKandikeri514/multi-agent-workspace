from langchain_core.messages import AIMessage
from tools.system_tools import get_system_time

def general_worker_node(state):
    """General worker handles out-of-scope inquiries like checking system time."""
    print("---GENERAL WORKER EXECUTION---")
    messages = state["messages"]
    last_message = messages[0].content.lower()
    
    outputs = []
    
    if "time" in last_message or "date" in last_message:
        res = get_system_time.invoke({})
        outputs.append(f"System Time Tool Result: {res}")
    else:
        outputs.append("General Worker reviewed the request and determined it is conversational.")
        
    return {
        "active_context": outputs,
        "completed_workers": ["General_Worker"],
        "messages": [AIMessage(content=f"General Worker executed: {'; '.join(outputs)}. Passing to FINISH.")]
    }
