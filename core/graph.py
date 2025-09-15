from langgraph.graph import StateGraph, END
from core.schema import MessageState
from core.node import intro_node, ask_question, record_answer, summary_node

def build_graph(total_questions: int = 3) -> StateGraph:
    graph = StateGraph(MessageState)

    # register nodes
    graph.add_node("intro", intro_node)
    graph.add_node("ask", ask_question)
    graph.add_node("record", record_answer)
    graph.add_node("summary", summary_node)

    # flow: intro -> ask
    graph.set_entry_point("intro")
    graph.add_edge("intro", "ask")

    # after record, go back to ask
    graph.add_edge("record", "ask")

    # conditional routing after ask:
    def route_after_ask(state: MessageState):
        # count how many answers already filled
        answered = sum(1 for m in state.messages if m.answer is not None)
        appended = len(state.messages)  # how many questions appended

        # If there is an unanswered appended question, go to record to capture answer
        if appended > answered:
            return "record"

        # If fewer questions appended than total, need to append next question (ask will append then return record)
        if appended < total_questions:
            return "record"

        # All questions appended and answered -> summary
        return "summary"

    graph.add_conditional_edges("ask", route_after_ask)
    graph.add_edge("summary", END)

    return graph
