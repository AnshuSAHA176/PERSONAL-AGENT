
import json
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel, Field, ValidationError

from apps.document.llm import get_model


class Topic(BaseModel):
    topics: list[str] = Field(
        description="Unique, meaningful topics extracted from the text."
    )


def get_extract_topics(chunks: list[str]) -> list[str]:
    if not chunks:
        return []

    llm = get_model("openai/gpt-oss-20b")

    messages = [
        SystemMessage(
            content="""
            You are an expert knowledge extraction agent in Nightly Brain.

            Extract meaningful topics, concepts, technologies, methods,
            and ideas explicitly supported by the text.

            Rules:
            - Extract only topics supported by the text.
            - Prefer specific concepts over generic keywords.
            - Preserve technical terminology.
            - Merge duplicate or equivalent topics.
            - Ignore filler and irrelevant content.
            - Do not generate summaries or recommendations.

            Return only a valid JSON object in this exact format:
            {"topics": ["topic 1", "topic 2"]}

            If no meaningful topics exist, return:
            {"topics": []}
            """
        ),
        HumanMessage(
            content="Extract topics from these text chunks:\n\n"
            + "\n\n".join(chunks)
        )
    ]

    response = llm.invoke(messages)

    print("Response content:", repr(response.content))
    print("Additional kwargs:", response.additional_kwargs)
    print("Response metadata:", response.response_metadata)

    content = response.content

    if not content:
        raise ValueError(
            f"Empty model response. "
            f"Metadata: {response.response_metadata}, "
            f"Additional kwargs: {response.additional_kwargs}"
        )

    if isinstance(content, list):
            content = "".join(
        block.get("text", "")
        for block in content
        if isinstance(block, dict)
    )

    if not isinstance(content, str):
        raise ValueError("The model returned a non-text response.")

    # Handle JSON wrapped in Markdown code fences.
    content = content.strip()
    if content.startswith("```"):
        content = content.removeprefix("```json").removeprefix("```")
        content = content.removesuffix("```").strip()

    try:
        data = json.loads(content)
        result = Topic.model_validate(data)
    except (json.JSONDecodeError, ValidationError) as exc:
        raise ValueError(
            f"Invalid topic extraction response: {content}"
        ) from exc

    # Remove empty values and duplicates.
    return list(dict.fromkeys(
        topic.strip()
        for topic in result.topics
        if topic.strip()
    ))
