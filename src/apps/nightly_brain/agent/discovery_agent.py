
from langgraph.graph import START, END, StateGraph
from pydantic import BaseModel, Field

from .extracttopic import get_extract_topics
from .connections import get_connections
from .generate_insight import get_insight
from .validate_instace import get_validate_insights
from ..models import Discovery


class State(BaseModel):
    chunks: list[str] = Field(default_factory=list)
    topics: list[str] = Field(default_factory=list)
    connections: list = Field(default_factory=list)
    insights: list = Field(default_factory=list)
    validate_insight: list = Field(default_factory=list)
    session: object = None
    saved_discovery_ids: list[int] = Field(default_factory=list)


def extract_topics(state: State):
    print("Running topic extraction...")

    result = get_extract_topics(chunks=state.chunks)

    print("Extracted topics:", result)
    return {"topics": result or []}


def find_connection(state: State):
    print("Running connection generation...")

    if not state.topics:
        print("No topics found. Skipping connections.")
        return {"connections": []}

    # Pass both topics and source text for richer context.
    result = get_connections(
        topics=state.topics,
        chunks=state.chunks,
    )

    print("Generated connections:", result)
    return {"connections": result or []}


def generate_insights(state: State):
    print("Running insight generation...")

    if not state.connections:
        print("No connections found. Skipping insight generation.")
        return {"insights": []}

    result = get_insight(
        topics=state.topics,
        connections=state.connections,
    )

    print("Generated insights:", result)
    return {"insights": result or []}


def validate_insights(state: State):
    print("Running insight validation...")

    if not state.insights:
        print("No insights found. Skipping validation.")
        return {"validate_insight": []}

    result = get_validate_insights(
        chunks=state.chunks,
        insights=state.insights,
    )

    print("Validated insights:", result)
    return {"validate_insight": result or []}


def save_discoveries(state: State) -> dict:
    session = state.session

    if session is None:
        raise ValueError(
            "A session is required to save discoveries."
        )

    saved_ids = []

    for insight in state.validate_insight:
        if not insight.supported:
            continue

        discovery = Discovery.objects.create(
            session=session,
            discovery_type=Discovery.DiscoveryType.INSIGHT,
            title=insight.title,
            description=insight.description,
            source_references=[
                evidence.chunk_id
                for evidence in insight.evidence
            ],
            metadata={
                "reasoning": insight.reasoning,
                "evidence": [
                    evidence.model_dump()
                    for evidence in insight.evidence
                ],
                "validation_reason": insight.validation_reason,
            },
        )

        saved_ids.append(discovery.id)

    print(f"Saved {len(saved_ids)} discoveries.")

    return {"saved_discovery_ids": saved_ids}


def get_discover_agent():
    graph_builder = StateGraph(State)

    graph_builder.add_node("extract_topics", extract_topics)
    graph_builder.add_node("find_connection", find_connection)
    graph_builder.add_node("generate_insights", generate_insights)
    graph_builder.add_node("validate_insights", validate_insights)
    graph_builder.add_node("save_discoveries", save_discoveries)

    graph_builder.add_edge(START, "extract_topics")
    graph_builder.add_edge("extract_topics", "find_connection")
    graph_builder.add_edge("find_connection", "generate_insights")
    graph_builder.add_edge("generate_insights", "validate_insights")
    graph_builder.add_edge("validate_insights", "save_discoveries")
    graph_builder.add_edge("save_discoveries", END)

    return graph_builder.compile()
