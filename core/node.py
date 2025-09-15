from typing import Optional
from core.schema import MessageState, Message
from core.clients import evaluate_answer, summarize_interview,generate_intro,generate_questions

QUESTIONS = [
    "What is the difference between VLOOKUP and INDEX-MATCH?",
    "How would you use a Pivot Table to summarize sales data by region?",
    "What are absolute vs relative references in Excel formulas?",
]

def intro_node(state: MessageState) -> MessageState:
    """Generate intro and set up dynamic questions."""
    state.intro_message = generate_intro()
    if not getattr(state, "questions", None):   # only generate once
        state.questions = generate_questions(n=3)
    return state

def ask_question(state: MessageState) -> MessageState:
    """Append the next question if available."""
    total = len(state.questions)
    if len(state.messages) >= total:
        return state

    if not state.messages or state.messages[-1].answer is not None:
        q = state.questions[len(state.messages)]
        state.messages.append(Message(question=q))
    return state

def record_answer(state: MessageState, answer: Optional[str] = None) -> MessageState:
    """
    Only fill the last message if an answer was passed to the node.
    If answer is None, we do nothing (prevents loops).
    """
    if not state.messages:
        return state
    # only record if answer provided and last message hasn't been answered yet
    if answer is not None:
        msg = state.messages[-1]
        if msg.answer is None:
            msg.answer = answer
            fb, sc = evaluate_answer(msg.question, answer)
            msg.feedback = fb
            msg.score = sc
    return state

def summary_node(state: MessageState) -> MessageState:
    # only run summary once (final_feedback used as guard)
    if state.final_feedback is None:
        final_feedback, final_score, final_recommendation = summarize_interview(state.messages)
        state.final_feedback = final_feedback
        state.final_score = final_score
        state.final_recommendation = final_recommendation
    return state
