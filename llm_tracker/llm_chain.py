"""LLM chain built from template and Ollama model."""
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

from llm_tracker.config import MODEL_NAME

TEMPLATE = """
Answer the question below.

Here is the conversation history: {context}

Question: {question}

Answer:
"""


def get_llm_chain(model_name=None):
    """Return the prompt | model chain. Expects 'context' and 'question' inputs.
    Uses model_name if provided, otherwise MODEL_NAME from config."""
    name = model_name if model_name else MODEL_NAME
    model = OllamaLLM(model=name)
    prompt = ChatPromptTemplate.from_template(TEMPLATE)
    return prompt | model
