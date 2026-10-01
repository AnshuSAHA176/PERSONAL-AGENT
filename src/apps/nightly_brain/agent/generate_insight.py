from apps.document.llm import get_model
from pydantic import BaseModel, Field
from langchain.messages import SystemMessage, HumanMessage


class Insight(BaseModel):
    title: str
    description: str
    reasoning: str


class Insights(BaseModel):
    insights: list[Insight] = Field(
        default_factory=list,
        description="Meaningful insights derived from the supplied topics and connections."
    )


def get_insights(
    topics: list[str],
    connections: list[dict]
) -> list[Insight]:

    llm = get_model("openai/gpt-oss-20b")

    model = llm.with_structured_output(
        Insights,
        method="json_mode"
    )

    system_prompt = """
    You are an expert knowledge discovery and reasoning agent
    in a personal AI system called Nightly Brain.

    Your task is to analyze the supplied topics and their
    connections to generate meaningful insights.

    Instructions:
    1. Identify deeper patterns, implications, and observations
       that emerge from the topics and their relationships.
    2. Discover insights that are not immediately obvious from
       looking at individual topics in isolation.
    3. Identify potential knowledge gaps, dependencies, shared
       principles, or opportunities revealed by the connections.
    4. Explain why each insight matters and how it follows from
       the supplied information.
    5. Prioritize specific, useful, and informative insights.

    Rules:
    - Use only the supplied topics and connections as evidence.
    - Do not invent facts, relationships, or unsupported conclusions.
    - Do not simply restate topics or paraphrase connections.
    - Avoid redundant, obvious, vague, or repetitive insights.
    - Distinguish supported observations from tentative hypotheses.
    - Do not treat possible relationships as proven causal claims.
    - Return an empty list if there are no meaningful insights.
    - Do not generate recommendations or action plans.
    - Keep each insight concise and focused on one observation.

    For every insight, provide:
    - title: A specific and informative title.
    - description: A clear explanation of the observation.
    - reasoning: How the supplied topics and connections
      support the insight.

    Return the result in the required structured format.
    """

    human_prompt = f"""
    Analyze the following topics and their connections.

    Topics:
    {topics}

    Connections:
    {connections}

    Generate meaningful insights based on this information.
    """

    result = model.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=human_prompt)
    ])

    return result.insights