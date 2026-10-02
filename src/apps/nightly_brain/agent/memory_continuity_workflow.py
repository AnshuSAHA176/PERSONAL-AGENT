
from langgraph.graph import StateGraph, START, END

from apps.document.RAG.embedding import generate_embedding
from pgvector.django import CosineDistance
from apps.document.models import DocumentChunk
from django.utils import timezone
from django.db.models import Q
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from apps.document.llm import get_model


class State(BaseModel):
    user_id: int
    summary: str
    related_chunks: list[dict] = Field(default_factory=list)
    memory_summary: str = ""


def retrive_summarys(state: State):
    embeddings = generate_embedding(state.summary)
    today = timezone.localdate()

    history_summarys = (
        DocumentChunk.objects
        .filter(
            document__user_id=state.user_id,
            created_at__date__lt=today,
            embedding__isnull=False,
        )
        .annotate(
            distance=CosineDistance("embedding", embeddings)
        )
        .values("text", "created_at", "distance")
        .order_by("distance")[:5]
    )

    return {
        "related_chunks": list(history_summarys)
    }




class MemoryOutput(BaseModel):
    memory_summary: str = Field(
        description="A concise continuity summary connecting today's activity "
                    "with relevant historical information."
    )


def memory_generator(state: State):
    if not state.related_chunks:
        return {
            "memery_summary": (
                "No relevant historical information was found "
                "to establish memory continuity."
            )
        }

    historical_context = "\n\n".join(
        f"Historical information:\n{chunk['text']}"
        for chunk in state.related_chunks
    )

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """
            You are a personal memory continuity assistant.

            Your task is to connect the user's current daily summary
            with relevant historical information.

            Identify:
            - Connections between current and past activities.
            - Progress on previously discussed projects or tasks.
            - Unresolved topics that remain relevant.
            - Important new developments.

            Rules:
            - Use only the supplied information.
            - Never invent events, decisions, or progress.
            - Do not claim that a task is completed unless the
              information explicitly supports it.
            - If there is no meaningful connection, say so.
            - Avoid repeating the daily summary unnecessarily.
            - Write a concise, natural-language memory summary.
            """
        ),
        (
            "human",
            """
            Today's summary:
            {today_summary}

            Relevant historical information:
            {historical_context}

            Generate the memory continuity summary.
            """
        )
    ])

    model = get_model("openai/gpt-oss-20b")
    structured_model = model.with_structured_output(
        MemoryOutput,
        method="json_mode",
    )

    chain = prompt | structured_model

    result = chain.invoke({
        "today_summary": state.summary,
        "historical_context": historical_context,
    })

    return {
        "memery_summary": result.memory_summary
    }


def memery_containely_agent():

    graph = StateGraph(State)

    graph.add_node("retrieve", retrive_summarys)
    graph.add_node("generate_memory", memory_generator)

    graph.add_edge(START, "retrieve")
    graph.add_edge("retrieve", "generate_memory")
    graph.add_edge("generate_memory", END)

    return graph.compile()