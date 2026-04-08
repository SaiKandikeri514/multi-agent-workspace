from langgraph.graph import StateGraph, START, END
from agents.graph_state import AgentState
from agents.supervisor import supervisor_node
from agents.worker_support import support_worker_node
from agents.worker_schedule import schedule_worker_node
from agents.worker_final import final_reporter_node
from agents.worker_general import general_worker_node

def build_graph():
    builder = StateGraph(AgentState)
    builder.add_node("Supervisor", supervisor_node)
    builder.add_node("Support_Worker", support_worker_node)
    builder.add_node("Schedule_Worker", schedule_worker_node)
    builder.add_node("General_Worker", general_worker_node)
    builder.add_node("Final_Reporter", final_reporter_node)
    
    builder.add_edge(START, "Supervisor")
    
    def router(state):
        next_val = state.get("next_agent", "FINISH")
        if next_val == "FINISH":
            return "Final_Reporter"
        elif next_val == "Support_Worker":
            return "Support_Worker"
        elif next_val == "Schedule_Worker":
            return "Schedule_Worker"
        elif next_val == "General_Worker":
            return "General_Worker"
        # Emergency catch
        return "Final_Reporter"
        
    builder.add_conditional_edges("Supervisor", router)
    
    # After workers, loop back to the supervisor
    builder.add_edge("Support_Worker", "Supervisor")
    builder.add_edge("Schedule_Worker", "Supervisor")
    builder.add_edge("General_Worker", "Supervisor")
    builder.add_edge("Final_Reporter", END)
    
    graph = builder.compile()
    return graph
