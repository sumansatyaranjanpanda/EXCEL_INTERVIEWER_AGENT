from langchain.chat_models import ChatOpenAI
from config.settings import OPENAI_API_KEY, MODEL_NAME
from langchain.prompts import ChatPromptTemplate

llm = ChatOpenAI(model=MODEL_NAME, temperature=0.3, openai_api_key=OPENAI_API_KEY)

def evaluate_answer(question: str, answer: str) -> tuple[str, int]:
    """Uses LLM to generate feedback and a score for a given Q/A"""
    prompt = f"""
    You are an Excel interviewer.
    Question: {question}
    Candidate Answer: {answer}
    
    1. Give concise feedback (2-3 sentences).
    2. Give a score from 0 to 5 (0 = wrong, 5 = excellent).
    Respond strictly in JSON format: {{"feedback": "...", "score": int}}
    """
    resp = llm.predict(prompt)
    try:
        import json
        parsed = json.loads(resp)
        return parsed["feedback"], parsed["score"]
    except Exception:
        return "Could not parse feedback, please review manually.", 0

from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain.prompts import ChatPromptTemplate

def summarize_interview(messages):
    qas = "\n".join([f"Q: {m.question}\nA: {m.answer}\nF: {m.feedback} (Score {m.score})" for m in messages])

    response_schemas = [
        ResponseSchema(name="final_feedback", description="Final feedback summary"),
        ResponseSchema(name="final_score", description="Overall numeric score 0-10"),
        ResponseSchema(name="final_recommendation", description="Recommendation: Hire, Needs Improvement, or Reject"),
    ]

    parser = StructuredOutputParser.from_response_schemas(response_schemas)
    format_instructions = parser.get_format_instructions()

    

    prompt = ChatPromptTemplate.from_template(
        "You are an Excel interviewer. Given this transcript:\n{qas}\n\n"
        "Provide final_feedback, final_score, and final_recommendation.\n\n"
        "{format_instructions}"
    )

    _input = prompt.format_messages(qas=qas, format_instructions=format_instructions)
    output = llm.invoke(_input)   # safer than predict
    return parser.parse(output.content)["final_feedback"], parser.parse(output.content)["final_score"], parser.parse(output.content)["final_recommendation"]

def generate_intro() -> str:
    """Generate a dynamic introduction for the Excel mock interview."""
    prompt = """
    You are acting as an Excel Mock Interviewer.
    Generate a short, friendly introduction for a candidate.
    - Greet the candidate
    - Explain that this is a mock Excel interview
    - Mention there will be a few questions
    - Encourage them to relax and do their best
    Keep it within 4 sentences.
    """
    response = llm.predict(prompt)
    return response.strip()


from langchain.prompts import ChatPromptTemplate

def generate_questions(n: int = 3) -> list[str]:
    """
    Use LLM to dynamically generate a list of Excel interview questions.
    n = number of questions to generate.
    """
    prompt = ChatPromptTemplate.from_template(
        "You are an Excel interviewer. Generate {n} unique interview questions "
        "that test different Excel skills (formulas, pivot tables, lookups, references). "
        "Return them as a plain numbered list, without explanations."
    )
    messages_for_llm = prompt.format_messages(n=n)
    output = llm.invoke(messages_for_llm)

    # Parse lines into list of questions
    raw = output.content.strip()
    questions = []
    for line in raw.splitlines():
        q = line.strip(" .-")
        if q:
            # remove numbering if present
            if q[0].isdigit():
                q = q.split(" ", 1)[-1]
            questions.append(q)
    return questions[:n]

