import os

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_groq import ChatGroq

from reviewer.prompt import SYSTEM_PROMPT
from reviewer.schemas import ReviewResult

load_dotenv()

MAX_DIFF_CHARS = 12000


def get_llm():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("API_KEY not found")
    model = os.getenv("GROQ_MODEL")
    return ChatGroq(
        api_key=api_key,
        model=model,
        temperature=0.1,
        model_kwargs={"response_format": {"type": "json_object"}},
    )


def review_diff(diff_text: str, max_attempts: int = 2) -> ReviewResult:
    llm = get_llm()

    if len(diff_text) > MAX_DIFF_CHARS:
        diff_text = diff_text[:MAX_DIFF_CHARS] + "\n... (diff truncated)"

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"Review this pull request diff:\n{diff_text}"),
    ]

    last_error = None
    for _ in range(max_attempts):
        response = llm.invoke(messages)
        raw = response.content

        try:
            return ReviewResult.model_validate_json(raw)
        except ValueError as error:
            last_error = error
            messages.append(AIMessage(content=raw))
            messages.append(
                HumanMessage(
                    content=f"Your JSON was invalid: {error}. "
                    "Return corrected JSON only, in the exact shape requested."
                )
            )

    raise RuntimeError(
        f"Model did not return valid JSON after {max_attempts} attempts: {last_error}"
    )