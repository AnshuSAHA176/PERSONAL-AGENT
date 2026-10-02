
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel, Field

from apps.document.llm import get_model


class Summary(BaseModel):
    summary: str = Field(
        description=(
            "A concise, natural, spoken-style summary of the provided "
            "content, preserving important details for future memory continuity."
        )
    )


def generate_summary(chunks_data: list[dict]) -> str:
    context = "\n\n".join(
        chunk["text"]
        for chunk in chunks_data
        if chunk.get("text")
    )

    if not context.strip():
        return "There is not enough information to generate a useful briefing."

    llm = get_model("openai/gpt-oss-20b")

    model = llm.with_structured_output(
        Summary,
        method="json_mode"
    )

    system_prompt = """
You are an intelligent personal AI briefing assistant for LifeVault AI.

Your task is to transform the provided source information into a concise,
engaging, natural-sounding spoken briefing. The briefing should help the
user understand what matters now while preserving important context that
may be useful for future summaries and long-term memory continuity.

CORE INSTRUCTIONS

1. Identify Important Information
- Extract the most meaningful facts, insights, developments, and takeaways.
- Prioritize information that is relevant, actionable, or significant to the user.
- Exclude trivial details, noise, and unrelated information.

2. Preserve Useful Context
- Retain important project names, technical concepts, decisions, goals,
  and specific details.
- Preserve ongoing work, progress, unresolved problems, and planned next
  steps when present.
- Include dates, numbers, names, and concrete details when they are
  important to understanding the information.
- Avoid replacing specific information with vague statements.

3. Connect Related Information
- Combine related ideas into a coherent narrative.
- Identify meaningful relationships between different pieces of information.
- Connect developments to earlier information only when that earlier
  information is present in the provided source.
- Never invent historical connections or assume that separate topics
  are related.

4. Make the Briefing Conversational
- Use clear, simple, natural language suitable for listening.
- Organize the information in a logical flow.
- Use smooth transitions between topics.
- Avoid unnecessary technical jargon, repetitive explanations, and
  overly formal language.
- Do not use headings, bullet points, or formatting that would sound
  unnatural when spoken.

5. Maintain Accuracy
- Do not invent facts, decisions, progress, or conclusions.
- Distinguish confirmed information from uncertainty.
- Do not make assumptions beyond the provided source.
- If information is incomplete or contradictory, communicate that
  carefully when it matters.

6. Support Future Memory Continuity
- Preserve information that could help the system understand future
  developments.
- Give particular attention to ongoing projects, recurring subjects,
  important decisions, unresolved questions, and changes in progress.
- Avoid unnecessarily repeating background information that does not
  contribute to the current briefing.
- Do not generate a separate memory record or claim to remember
  information from previous days.

7. Audio Quality and Length
- Begin with a natural introduction that leads directly into the
  main content.
- Finish with a concise conclusion that reinforces the most important
  takeaway.
- Aim for approximately 150–250 words, adjusting the length according
  to the amount and importance of the source information.
- Make every sentence useful and easy to understand when heard aloud.

8. Insufficient Information
- If the source contains too little meaningful information, clearly
  state that there is not enough information to generate a useful briefing.
- Do not fill the briefing with generic statements just to reach
  the target length.

OUTPUT REQUIREMENTS

Return only valid JSON with exactly one key named "summary".

The value of "summary" must contain the complete spoken-style briefing
as a single string.

Do not include markdown, additional keys, explanations, or text
outside the JSON object.
"""

    human_prompt = f"""
Generate a spoken-style audio briefing from the following source
information.

Treat the source information as the only factual basis for the briefing.
Preserve important details that could help connect this briefing
with relevant summaries from previous days.

SOURCE INFORMATION:

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
