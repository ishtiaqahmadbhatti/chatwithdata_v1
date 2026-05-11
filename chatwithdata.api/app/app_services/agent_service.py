"""
Agent Service — LangGraph Agentic RAG Pipeline.

Graph flow:
  retrieve → grade_docs → [generate | rewrite_query → retrieve]

Nodes:
  - retrieve     : fetch top-k docs from ChromaDB for the question
  - grade_docs   : LLM checks if retrieved docs are actually relevant
  - generate     : LLM produces final answer from relevant docs
  - rewrite      : LLM rewrites the question if docs were irrelevant (fallback)
"""

import logging
from typing import List, Dict, Any, TypedDict, Literal
import operator

from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, END

from app.app_services.rag_service import get_retriever
from app.app_core.config import settings

logger = logging.getLogger(__name__)

# ── LLM ───────────────────────────────────────────────────────────────────────
def _get_llm(temperature: float = 0.2) -> ChatOllama:
    return ChatOllama(
        model=settings.ollama_llm_model, 
        base_url=settings.ollama_base_url, 
        temperature=temperature
    )


# ── Graph State ───────────────────────────────────────────────────────────────
class AgentState(TypedDict):
    video_id: str
    question: str
    documents: List[Document]
    generation: str
    retries: int


# ── Node: Retrieve ─────────────────────────────────────────────────────────────
def node_retrieve(state: AgentState) -> AgentState:
    """Retrieve top-k relevant docs from ChromaDB."""
    logger.info(f"[RAG] Retrieving for: {state['question']}")
    retriever = get_retriever(state["video_id"], k=6)
    docs = retriever.invoke(state["question"])
    return {**state, "documents": docs}


# ── Node: Generate Answer ──────────────────────────────────────────────────────
_GENERATE_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You are an expert assistant analyzing YouTube video content.\n"
     "Use ONLY the provided context (metadata, transcript, comments) to answer the question.\n"
     "Be concise and accurate. If the context doesn't have enough info, say so clearly.\n\n"
     "Context:\n{context}"),
    ("human", "{question}"),
])

def node_generate(state: AgentState) -> AgentState:
    """Generate final answer using relevant documents."""
    llm = _get_llm(temperature=0.3)
    chain = _GENERATE_PROMPT | llm | StrOutputParser()

    context = "\n\n---\n\n".join(
        f"[{doc.metadata.get('source', 'unknown')}]\n{doc.page_content}"
        for doc in state["documents"]
    )

    answer = chain.invoke({
        "context": context,
        "question": state["question"],
    })
    logger.info(f"[RAG] Generated answer ({len(answer)} chars)")
    return {**state, "generation": answer}


# ── Build Graph ────────────────────────────────────────────────────────────────
def _build_rag_graph() -> StateGraph:
    graph = StateGraph(AgentState)

    graph.add_node("retrieve",    node_retrieve)
    graph.add_node("generate",    node_generate)

    graph.set_entry_point("retrieve")
    graph.add_edge("retrieve", "generate")
    graph.add_edge("generate", END)

    return graph.compile()


# Singleton compiled graph
_rag_graph = None

def get_rag_graph():
    global _rag_graph
    if _rag_graph is None:
        _rag_graph = _build_rag_graph()
    return _rag_graph


# ── Public API ─────────────────────────────────────────────────────────────────
def run_rag_query(video_id: str, question: str) -> Dict:
    """
    Run the full Agentic RAG pipeline for a question about a YouTube video.
    Returns answer + retrieved sources.
    """
    graph = get_rag_graph()

    initial_state: AgentState = {
        "video_id":   video_id,
        "question":   question,
        "documents":  [],
        "generation": "",
        "retries":    0,
    }

    final_state = graph.invoke(initial_state)

    # Build source references
    sources = []
    seen = set()
    for doc in final_state.get("documents", []):
        src = doc.metadata.get("source", "unknown")
        snippet = doc.page_content[:200].replace("\n", " ").strip()
        key = snippet[:60]
        if key not in seen:
            seen.add(key)
            sources.append({"source": src, "snippet": snippet})

    return {
        "video_id":       video_id,
        "question":       final_state["question"],   # may have been rewritten
        "original_question": question,
        "answer":         final_state.get("generation", "No answer could be generated."),
        "sources_used":   sources,
        "docs_retrieved": len(final_state.get("documents", [])),
    }
