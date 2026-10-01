from langchain.messages import SystemMessage,HumanMessage

from apps.document.llm import get_model
from pydantic import BaseModel


class Topic(BaseModel):
    topic :list


def get_extract_topics(chunks:list)->list:

    llm = get_model('openai/gpt-oss-20b')
