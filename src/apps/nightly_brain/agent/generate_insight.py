
from apps.document.llm import get_model
from pydantic import BaseModel, Field
from langchain_core.messages import SystemMessage, HumanMessage


class Insight(BaseModel):
    title: str = Field(description="A specific, informative insight title.")
    description: str = Field(description="A concise explanation of the insight.")
    reasoning: str = Field(description="Evidence-based reasoning supporting the insight.")


class Insights(BaseModel):
    insights: list[Insight] = Field(
        default_factory=list,
        description="Meaningful insights derived from supplied topics and connections."
    )


def get_insight(
    topics: list[str],
    connections: list,
) -> list[Insight]:

    if not topics or not connections:
        print("Skipping insight generation: topics or connections are empty.")
        return []

    # Support both Pydantic objects and dictionaries.
    connections_data = [
        item.model_dump() if isinstance(item, BaseModel) else item
        for item in connections
    ]

    llm = get_model("openai/gpt-oss-20b")

    model = llm.with_structured_output(
        Insights,
        method="json_mode",
    )

    system_prompt = """
    You are an expert knowledge discovery and reasoning agent
    in a personal AI system called Nightly Brain.

    Analyze the supplied topics and connections to identify
    meaningful, non-obvious insights.

    Focus on:
    - Deeper patterns and implications.
    - Knowledge gaps and dependencies.
    - Shared principles and opportunities.
    - Observations that emerge from multiple relationships.

    Rules:
    - Use only the supplied topics and connections.
    - Do not invent facts or unsupported conclusions.
    - Do not merely restate topics or connections.
    - Avoid redundant, obvious, vague, or repetitive insights.
    - Distinguish supported observations from tentative hypotheses.
    - Never present possible relationships as proven causal claims.
    - Do not generate recommendations or action plans.
    - Generate at most 5 concise insights.
    - Return an empty list only when no meaningful insight can be derived.

    Each insight must contain:
    - title
    - description
    - reasoning

    Return valid JSON with the key "insights", matching the schema.
    """

    human_prompt = f"""
    Analyze the following knowledge data.

    TOPICS:
    {topics}

    CONNECTIONS:
    {connections_data}

    Identify deeper observations supported by these connections.
    Generate valid JSON with the required "insights" key.
    """

    result = model.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=human_prompt),
    ])

    insights = result.insights

    print(f"Generated {len(insights)} insights.")
    for insight in insights:
        print(f"Insight: {insight.title}")

    return insights
