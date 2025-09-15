# app.py — manual node driver (recommended)
from core.schema import MessageState
from core.node import intro_node, ask_question, record_answer, summary_node

def run_cli():
    state = MessageState()  # Pydantic state

    # Intro
    state = intro_node(state)
    if state.intro_message:   # ✅ show intro here
        print("\n=== Introduction ===")
        print(state.intro_message)
    
    total_questions = len(state.questions) # keep in sync with core/nodes.QUESTIONS

    # Main loop: append question -> ask user -> record answer -> repeat
    while True:
        # 1) Ask phase: append next question if not yet appended
        state = ask_question(state)

        # If last message exists and has no answer, prompt user
        if state.messages and state.messages[-1].answer is None:
            q = state.messages[-1].question
            ans = input(f"\nQ: {q}\nYour Answer: ").strip()

            # 2) Record phase: pass the answer to record_answer
            state = record_answer(state, ans)

        # If all questions appended and all answered -> break to summary
        appended = len(state.messages)
        answered = sum(1 for m in state.messages if m.answer is not None)
        if appended >= total_questions and answered >= total_questions:
            break

    # Summary
    state = summary_node(state)

    # Print summary
    print("\n=== Interview Summary ===")
    for idx, msg in enumerate(state.messages, start=1):
        print(f"Q{idx}: {msg.question}")
        print(f"A: {msg.answer}")
        print(f"Feedback: {msg.feedback}")
        print(f"Score: {msg.score}\n")

    print("Final Feedback:", state.final_feedback)
    print("Final Score:", state.final_score)
    print("Recommendation:", state.final_recommendation)


if __name__ == "__main__":
    run_cli()
