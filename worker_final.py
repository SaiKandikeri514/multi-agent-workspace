import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_vertexai import ChatVertexAI
from langchain_core.messages import AIMessage

def final_reporter_node(state):
    """Generates a final natural language summary of all actions."""
    print("---FINAL REPORTER EXECUTION---")
    
    # Format context cleanly
    ctx_list = state.get("active_context", [])
    # We only want the actual worker logs, so omit supervisor router logic if possible, or leave it all
    context_str = "\n".join(ctx_list) if ctx_list else "No actions taken."
    
    # Get the original human request
    messages = state.get("messages", [])
    original_request = messages[0].content if messages else "No original request found."
    
    try:
        import datetime
        current_time_str = datetime.datetime.now().strftime("%I:%M %p on %b %d, %Y")
        
        if context_str == "No actions taken.":
            prompt_text = f"You are a helpful Enterprise AI Assistant. The user has asked a general question or made a conversational statement without triggering any backend worker agents. Answer them directly, naturally, and politely using your baseline intelligence.\nIf they ask for the datetime, use this system injection: {current_time_str}\n\nUser Request: {original_request}"
        else:
            prompt_text = f"You are a highly efficient Executive AI agent. You have just completed a complex multi-tool workflow.\n\nOriginal User Request:\n{original_request}\n\nExact Actions Logged by Sub-Agents:\n{context_str}\n\nBased STRICTLY on the logs above, write a concise, professional summary directly to the user detailing exactly what you accomplished. Do not greet or say 'Here is a summary'. Just state the facts of what was done."
        
        from vertexai.generative_models import GenerativeModel
        model = GenerativeModel("gemini-2.5-flash")
        res = model.generate_content(prompt_text)
        final_msg = res.text
        
    except Exception as e:
        final_msg = f"Workflow complete. (Note: Could not generate AI summary due to error: {e})"
        
    return {
        "messages": [AIMessage(content=final_msg)],
        "completed_workers": ["Final_Reporter"]
    }
