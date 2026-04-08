import os
from dotenv import load_dotenv
load_dotenv()

from agents.graph import build_graph
from langchain_core.messages import HumanMessage

def test_graph():
    prompt = "Acme Corp just reported a critical outage. Check their SLA in the CRM, open a highest-priority Jira ticket with the details, and find a 30-minute slot on my calendar today to sync with the support team."
    graph = build_graph()
    
    state = {"messages": [HumanMessage(content=prompt)], "active_context": []}
    
    print("Starting execution...")
    try:
        # We manually step through or just invoke
        for output in graph.stream(state, config={"recursion_limit": 10}):
            for node_name, state_upsert in output.items():
                print(f"\n--- Output from {node_name} ---")
                if "next_agent" in state_upsert:
                    print(f"Next Agent: {state_upsert['next_agent']}")
                if "active_context" in state_upsert:
                    print(f"Active Context: {state_upsert['active_context']}")
                if "messages" in state_upsert:
                    print(f"Messages Appended: {[m.content for m in state_upsert['messages']]}")
                    
    except Exception as e:
        print(f"Exception caught! {e}")

if __name__ == "__main__":
    test_graph()
