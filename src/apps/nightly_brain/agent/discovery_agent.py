from langgraph.graph import START,END,StateGraph
from pydantic import BaseModel
from apps.document.llm import get_model


class State(BaseModel):
    chunks : list
    extract_topics : list
    generate_insights : str



graph_builder = StateGraph(State)

def extract_topics(state:State):
    


