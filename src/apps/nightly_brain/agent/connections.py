
from apps.document.llm import get_model
from pydantic import BaseModel, Field, ConfigDict


class Connection(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    topic_a: str = Field(alias="from")
    topic_b: str = Field(alias="to")
    relationship: str
    confidence: str
    evidence: str = ""


class Connections(BaseModel):
    connection: list[Connection] = Field(
        default_factory=list,
        description="Meaningful relationships between supplied topics."
    )


def get_connections(topics: list[str], chunks: list[str]):
    if not topics or not chunks:
        return []

    llm = get_model("openai/gpt-oss-20b")

    model = llm.with_structured_output(
        Connections,
        method="json_mode",
    )

    source_text = "\n\n".join(
        chunk.strip()
        for chunk in chunks
        if chunk and chunk.strip()
    )[:18000]

    prompt = f"""
    Analyze the topics and source text to identify meaningful
    relationships between distinct topics.

    TOPICS:
    {topics}

    SOURCE TEXT:
    {source_text}

    Return up to 10 evidence-supported connections.

    For each connection, use exactly these JSON keys:
    - from: the first topic
    - to: the second topic
    - relationship: a concise explanation
    - confidence: high, medium, or low
    - evidence: a short supporting quote or source detail

    Preserve original topic names.
    Do not invent relationships or evidence.
    Avoid duplicates and trivial connections.
    Return an empty connection list only if no meaningful
    relationships can be supported.

    Return valid JSON with the key "connection".
    """

    result = model.invoke([
        (
            "system",
            """
            You are a knowledge relationship discovery agent.
            Identify useful relationships grounded in the supplied text.
            Return only valid JSON matching the requested schema.
            """
        ),
        ("human", prompt),
    ])

    connections = result.connection

    print(f"Generated {len(connections)} connections.")

    return connections
