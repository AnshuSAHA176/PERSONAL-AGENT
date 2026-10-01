from apps.document.llm import get_model
from pydantic import BaseModel, Field


class Connection(BaseModel):
    topic_a: str
    topic_b: str
    relationship: str
    confidence: str


class Connections(BaseModel):
    connection: list[Connection] = Field(
        default_factory=list,
        description="Meaningful relationships between the supplied topics."
    )


def get_connections(topics: list[str]) -> list[Connection]:
    llm = get_model("openai/gpt-oss-20b")

    model = llm.with_structured_output(
        Connections,
        method="json_mode"
    )

    prompt = f"""
    Analyze these topics and find meaningful relationships
    between them.

    Topics:
    {topics}
    """

    result = model.invoke([
        ("system", """You are an expert knowledge graph and
        relationship discovery agent in Nightly Brain.

        Identify meaningful relationships between the supplied topics.

        Rules:
        - Preserve the original topic names.
        - Find conceptual, functional, causal, or technical relationships.
        - Avoid trivial, duplicate, or unsupported connections.
        - Do not invent facts or dependencies.
        - Return an empty list if no meaningful connections exist.
        - Include a concise relationship and qualitative confidence
          for each connection.
        """),
        ("human", prompt)
    ])

    return result.connection