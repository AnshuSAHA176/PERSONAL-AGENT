from langgraph.graph import START, END, StateGraph
from pydantic import BaseModel, Field

from .extracttopic import get_extract_topics
from .connections import get_connections
from generate_insight import get_insights
from .validate_instace import get_validate_insights
from ..models import Discovery


class State(BaseModel):
    chunks: list[str] = Field(default_factory=list)
    topics: list[str] = Field(default_factory=list)
    connections: list = Field(default_factory=list)
    insights: list = Field(default_factory=list)
    validate_insight: list = Field(default_factory=list)


def extract_topics(state: State):
    result = get_extract_topics(chunks=state.chunks)

    return {"topics": result}


def find_connection(state: State):
    result = get_connections(topics=state.topics)
    return {"connections": result}


def generate_insights(state: State):
    result = get_insights(topics=state.topics, connections=state.connections)
    return {"insights": result}


def validate_insights(state:State):
    return {"validate_insight":get_validate_insights(chunks=state.chunks,insights=state.insights)}

def save_discoveries(state: State) -> dict:
    validated_insights = state.validated_insights
    session = state.session

    saved_ids = []

    for insight in validated_insights:
        if not insight.supported:
            continue

        discovery = Discovery.objects.create(
            session=session,
            type="INSIGHT",
            title=insight.title,
            description=insight.description,
            source_refs=[
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

    return {"saved_discovery_ids": saved_ids}

def get_discover_agent():
    graph_builder = StateGraph(State)

    graph_builder.add_node("extract_topics", extract_topics)

    graph_builder.add_node("find_connection",find_connection)
    graph_builder.add_node("generate_insights",generate_insights)
    graph_builder.add_node("validate_insights",validate_insights)
    graph_builder.add_node("save_discoveries",save_discoveries)



    graph_builder.add_edge(START, "extract_topics")
    graph_builder.add_edge("extract_topics", "find_connection")
    graph_builder.add_edge("find_connection","generate_insights")
    graph_builder.add_edge("generate_insights","validate_insights")
    graph_builder.add_edge("validate_insights","save_discoveries")
    graph_builder.add_edge("save_discoveries",END)

    graph = graph_builder.compile()
