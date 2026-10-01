
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel, Field

from apps.document.llm import get_model


class Summary(BaseModel):
    summary: str = Field(
        description="A concise, natural, spoken-style summary of the provided content."
    )


def generate_summary(chunks_data: list[dict]) -> str:
    context = "\n\n".join(
        chunk["text"]
        for chunk in chunks_data
        if chunk.get("text")
    )

    if not context.strip():
        return "There is not enough information to generate a briefing."

    llm = get_model("openai/gpt-oss-20b")

    model = llm.with_structured_output(
        Summary,
        method="json_mode"
    )

    system_prompt = """
You are an intelligent personal briefing assistant.

Your task is to turn the provided information into a clear,
engaging, and easy-to-listen-to audio briefing.

Instructions:
- Identify the most important information and key takeaways.
- Connect related ideas only when the provided content supports it.
- Use simple, conversational language suitable for speaking aloud.
- Organize the information into a logical flow.
- Avoid unnecessary technical jargon and repetitive details.
- Do not invent facts or make assumptions beyond the provided content.
- Do not mention chunks, documents, embeddings, or internal processing.
- Start with a natural introduction and finish with a brief conclusion.
- Keep the briefing concise, ideally around 150–200 words.
- If the input contains insufficient information, clearly state that.
- Focus on the main subject and exclude unrelated incidental facts.

Return only valid JSON with exactly one key named "summary".
The value of "summary" must contain the complete briefing.
Do not use "briefing" or any other key.
"""

    human_prompt = f"""
Generate a spoken-style audio briefing from the following
source information.

Source information:
{context}

Return valid JSON in this exact format:
{{
    "summary": "Your complete briefing here"
}}
"""

    result = model.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=human_prompt)
    ])

    return result.summary
