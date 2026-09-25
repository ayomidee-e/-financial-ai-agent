from langgraph.graph import StateGraph, END
from typing import TypedDict, List
from src.guardrails.input_guard import check_input
from src.agent.critic import audit_analysis
from src.agent.graph import agent_executor

class AgentState(TypedDict):
    query: str
    response: str
    source_docs: str
    audit_passed: bool
    retry_count: int

def input_node(state: AgentState):
    if not check_input(state["query"]):
        return {"response": "Security Alert: Query violates financial compliance policies.", "audit_passed": True}
    return {}

def analyst_node(state: AgentState):
    # Run the main agent
    result = agent_executor.invoke({"messages": [("user", state["query"])]})
    return {"response": result["messages"][-1].content, "source_docs": "..."} # populate docs

def auditor_node(state: AgentState):
    if state.get("audit_passed"): return {}
    
    critique = audit_analysis(state["response"], state["source_docs"])
    if critique.is_accurate:
        return {"audit_passed": True}
    else:
        # Loop back to analyst with feedback
        return {
            "query": f"Original Query: {state['query']}\n\nPrevious Error: {critique.feedback}\n\nFix the report.",
            "retry_count": state.get("retry_count", 0) + 1
        }

# Build Graph
workflow = StateGraph(AgentState)
workflow.add_node("input_guard", input_node)
workflow.add_node("analyst", analyst_node)
workflow.add_node("auditor", auditor_node)

workflow.set_entry_point("input_guard")
workflow.add_conditional_edges("input_guard", lambda x: "analyst" if "response" not in x else END)
workflow.add_edge("analyst", "auditor")
workflow.add_conditional_edges("auditor", lambda x: END if x.get("audit_passed") or x.get("retry_count", 0) > 2 else "analyst")

app = workflow.compile()