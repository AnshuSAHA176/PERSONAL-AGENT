from langchain.messages import SystemMessage, HumanMessage
from pydantic import BaseModel, Field

from apps.document.llm import get_model


class Topic(BaseModel):
    topics: list[str] = Field(
        description="Unique, meaningful topics extracted from the text."
    )


def get_extract_topics(chunks: list[str]) -> list[str]:
    llm = get_model("openai/gpt-oss-20b")

    model = llm.with_structured_output(
        Topic,
        method="json_mode"
    )

    messages = [
        SystemMessage(content="""You are an expert knowledge extraction
agent in Nightly Brain.

Extract meaningful topics, concepts, technologies, methods, and ideas
from the provided text chunks.

Rules:
- Extract only topics explicitly supported by the text.
- Prefer specific concepts over generic keywords.
- Preserve technical terminology.
- Merge duplicate or semantically equivalent topics.
- Ignore filler and irrelevant content.
- Do not generate summaries, connections, or recommendations.
- Return an empty list if no meaningful topics are found.

Return the result in the required structured format."""),
        HumanMessage(
            content=f"Extract topics from these text chunks:\n\n{chunks}"
        )
    ]

    result = model.invoke(messages)

    return result.topics