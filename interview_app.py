import streamlit as st
from core.schema import MessageState, Message
from core.node import intro_node, ask_question, record_answer, summary_node

# Helper: read/save state in session_state as plain dict
STATE_KEY = "interview_state"

def get_state() -> MessageState:
    """Return a MessageState (hydrated) from session_state, or a new one."""
    if STATE_KEY not in st.session_state:
        st.session_state[STATE_KEY] = MessageState().model_dump()  # pydantic v2: model_dump, fallback .dict() if v1
    # hydrate
    try:
        return MessageState(**st.session_state[STATE_KEY])
    except Exception:
        # fallback: construct fresh state if hydration fails
        st.session_state[STATE_KEY] = MessageState().model_dump()
        return MessageState(**st.session_state[STATE_KEY])

def save_state(state: MessageState):
    """Save MessageState to session_state as dict."""
    try:
        st.session_state[STATE_KEY] = state.model_dump()
    except Exception:
        st.session_state[STATE_KEY] = state.dict()  # fallback for pydantic v1

def reset_state():
    st.session_state[STATE_KEY] = MessageState().model_dump()

# UI layout
st.set_page_config(page_title="Excel Mock Interviewer", layout="centered")
st.title("AI Excel Mock Interviewer")

# Sidebar controls
with st.sidebar:
    st.header("Controls")
    if st.button("Start New Interview"):
        reset_state()
        st.rerun()
    st.write("Tip: Answers can be short or long. LLM will evaluate and summarize at the end.")

# Load current state
state = get_state()

# If intro not set, show start button (or auto-generate intro on demand)
if not state.intro_message:
    st.info("Click 'Begin Interview' to generate a short introduction and first question.")
    if st.button("Begin Interview"):
        with st.spinner("Generating intro and questions..."):
            state = intro_node(state)           # generate intro + questions (if implemented)
            state = ask_question(state)         # append first question
            save_state(state)
        st.rerun()
    st.stop()

# Show Intro
st.subheader("Introduction")
st.write(state.intro_message)

# Show progress
total_questions = len(state.questions) if getattr(state, "questions", None) else 0
appended = len(state.messages)
answered = sum(1 for m in state.messages if m.answer is not None)
st.markdown(f"**Progress:** {answered}/{total_questions} answered")

# Show history
if state.messages:
    st.subheader("History")
    for i, m in enumerate(state.messages, start=1):
        st.markdown(f"**Q{i}:** {m.question}")
        if m.answer is not None:
            st.markdown(f"- **A:** {m.answer}")
            st.markdown(f"- **Feedback:** {m.feedback}")
            st.markdown(f"- **Score:** {m.score}")
        else:
            st.markdown("- *Not answered yet*")

st.markdown("---")

# If there's an unanswered current question, show the answer input
if state.messages and state.messages[-1].answer is None:
    st.subheader("Current Question")
    current_q = state.messages[-1].question
    st.write(current_q)

    with st.form(key="answer_form"):
        answer = st.text_area("Your answer", value="", height=140)
        submit = st.form_submit_button("Submit Answer")
        if submit:
            # call record_answer then append next question (if any)
            with st.spinner("Evaluating answer..."):
                state = record_answer(state, answer)
                # Try to append next question if available
                state = ask_question(state)
                save_state(state)
            st.rerun()
else:
    # No unanswered question currently
    # If there are more questions to append, show button to get next question
    if appended < total_questions:
        if st.button("Next Question"):
            with st.spinner("Fetching next question..."):
                state = ask_question(state)
                save_state(state)
            st.rerun()
    else:
        # All questions appended; ensure all are answered or show summary
        if answered >= total_questions:
            # Run summary (only once)
            if not state.final_feedback:
                with st.spinner("Generating final summary..."):
                    state = summary_node(state)
                    save_state(state)
                    st.rerun()
            else:
                st.success("Interview complete — see final summary below.")

# Final summary/outro (if present)
if state.final_feedback:
    st.markdown("---")
    st.subheader("Final Summary")
    st.write(state.final_feedback)
    st.write(f"**Final Score:** {state.final_score}")
    st.write(f"**Recommendation:** {state.final_recommendation}")
    if getattr(state, "outro_message", None):
        st.markdown("---")
        st.write(state.outro_message)
