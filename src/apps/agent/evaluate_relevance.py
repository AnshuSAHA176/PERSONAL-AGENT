from apps.document.llm import get_model
from pydantic import BaseModel


class EvaluateRelevance(BaseModel):
    relevant : bool
    score : float
    reason:str 


def evaluate_relevance(question:str,chunks:list) ->dict:
    model = get_model('openai/gpt-oss-20b')

    llm = model.with_structured_output(
    EvaluateRelevance,
    method="json_mode"
)
    promt =fprompt = f"""
You are a retrieval relevance evaluator for LifeVault.

Evaluate whether the retrieved chunks contain enough information
to answer the user's question.

USER QUESTION:
{question}

RETRIEVED CHUNKS:
{chunks}

Return your evaluation in JSON format.

The JSON object must contain exactly these fields:
- relevant: boolean
- score: number between 0.0 and 1.0
- reason: short explanation

Rules:
- Set relevant to true only if the chunks sufficiently support
  answering the question.
- Do not use your own knowledge.
- Do not answer the user's question.
- Return only valid JSON, without Markdown.
"""
    result = llm.invoke(promt)

    return {
        "relevant": result.relevant,
        "score": result.score,
        "reason": result.reason,
    }
