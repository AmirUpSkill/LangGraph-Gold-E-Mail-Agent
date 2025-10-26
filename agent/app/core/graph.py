from typing import List 
from langgraph.graph import StateGraph , START , END 
from langgraph.graph.message import add_messages 
from operator import add 
from app.core.schemas import EmailState 
# --- Later we implement factory --- 
from app.services.llm_factory import build_groq_llm , build_gemini_llm 
# --- Get the Prompts Templates --- 
from app.prompts.templates import (
    AGENT_SYSTEM_PROMPT,
    AGENT_USER_PROMPT,
    AGGREGATOR_SYSTEM_PROMPT,
    AGGREGATOR_USER_PROMPT,
)
# --- Build Agent Nodes --- 
def _agent_node_impl(
    state: EmailState,
    *,
    agent_name: str,
    model_str: str,
    llm
) -> dict:
    """
        Shared implementation for every parallel agent . 
        Returns "only" the delta to merge into State :  
    """
    from langchain_core.prompts import ChatPromptTemplate 
    from datetime import datetime 
    # --- Build the Prompt Template --- 
    prompt = ChatPromptTemplate.from_messages([
        ("system",AGENT_SYSTEM_PROMPT),
        ("user",AGENT_USER_PROMPT),
    ])
    chain = prompt | llm 
    # --- Compute the time --- 
    t0 = datetime.now()
    # --- Invoke the LLM --- 
    output = chain.invoke({
        "resume_text":state["resume_text"],
        "job_description":state["job_description"],
    })
    # --- Compute duration --- 
    t1 = datetime.now()
    duration_ms = (t1 - t0).total_seconds() * 1000 
    draft_text = output.content.strip()
    return {
        "agent_responses": [{
            "agent_name": agent_name,
            "model": model_str,
            "draft": draft_text,
            "status": "complete",
            "metadata": {
                "word_count": len(draft_text.split()),
                "generation_time_ms": duration_ms,
                "temperature": llm.temperature
            },
            "ui_metadata": _ui_meta(agent_name)
        }]
    }

# --- Define the First Node Agent ---
def kimi_node(state: EmailState) -> dict:
    # --- Use moonshotai/kimi-k2 --- 
    llm = build_groq_llm("moonshotai/kimi-k2-instruct-0905",temperature=0.7)
    return _agent_node_impl(
        state,
        agent_name="kimi",
        model_str="moonshotai/kimi-k2-instruct-0905",
        llm=llm,
    )
# --- Define the Second Qwen Agent --- 
def qwen_node(state: EmailState) -> dict:
    # --- Use qwen/qwen-32b --- 
    llm = build_groq_llm("qwen/qwen-32b",temperature=0.7)
    return _agent_node_impl(
        state,
        agent_name="qwen",
        model_str="qwen/qwen-32b",
        llm=llm,
    )
# --- Define Open AI Oss Agent --- 
def openai_oss_node(state: EmailState) -> dict:
    # --- Use openai-oss/gpt-oos-120b --- 
    llm = build_groq_llm("openai-oss/gpt-oos-120b",temperature=0.7)
    return _agent_node_impl(
        state,
        agent_name="openai-oss",
        model_str="openai-oss/gpt-oos-120b",
        llm=llm,
    )
# --- Aggregator Node --- 
def aggregator_node(state: EmailState) -> dict:
    """
    Aggregator Node:
    - Analyzes 3 parallel agent drafts
    - Synthesizes the best final email
    - Provides reasoning and attribution
    """
    from langchain_core.prompts import ChatPromptTemplate
    from datetime import datetime
    import json

    # --- Build Gemini aggregator (lower temp for consistency) ---
    aggregator_llm = build_gemini_llm("gemini-2.5-pro", temperature=0.3)

    # --- Format all drafts for the prompt ---
    drafts_text = "\n\n" + ("=" * 50 + "\n\n").join([
        f"DRAFT {i+1} (from {resp['agent_name']} using {resp['model']}):\n{resp['draft']}"
        for i, resp in enumerate(state["agent_responses"])
    ])

    # --- Build prompt ---
    prompt = ChatPromptTemplate.from_messages([
        ("system", AGGREGATOR_SYSTEM_PROMPT),
        ("user", AGGREGATOR_USER_PROMPT),
    ])

    chain = prompt | aggregator_llm

    # --- Invoke with properly formatted input ---
    t0 = datetime.now()
    output = chain.invoke({
        "drafts": drafts_text,
        "resume_text": state["resume_text"],
        "job_description": state["job_description"],
    })
    t1 = datetime.now()

    duration_ms = int((t1 - t0).total_seconds() * 1000)
    final_text = output.content.strip()

    # --- Parse structured output (if LLM returns JSON) ---
    # If your prompt asks for JSON with final_email, reasoning, source_breakdown:
    try:
        parsed = json.loads(final_text)
        final_email = parsed.get("final_email", final_text)
        reasoning = parsed.get("reasoning", "Synthesis completed")
        source_breakdown = parsed.get("source_breakdown", {
            "subject": "kimi",
            "opening": "kimi", 
            "body": "qwen",
            "closing": "openai_oss"
        })
    except json.JSONDecodeError:
        # Fallback if LLM doesn't return JSON
        final_email = final_text
        reasoning = "Combined best elements from all three drafts"
        source_breakdown = {
            "subject": "kimi",
            "opening": "kimi",
            "body": "qwen", 
            "closing": "openai_oss"
        }

    # --- Return keys that match EmailState ---
    return {
        "final_email": final_email,
        "reasoning": reasoning,
        "source_breakdown": source_breakdown,
    }
# --- Util Function --- 
def _ui_meta(agent: str) -> dict:
    palette = {
        "kimi": {"color": "#60A5FA", "position": "left", "emoji": "⚡"},
        "qwen": {"color": "#34D399", "position": "center", "emoji": "🎯"},
        "openai_oss": {"color": "#F472B6", "position": "right", "emoji": "🚀"}
    }
    return palette[agent]

# --- Assemble the Graph --- 
def assemble_graph() -> StateGraph:
    # --- Build the Graph from the State --- 
    builder = StateGraph(EmailState)
    # --- Nodes --- 
    builder.add_node("kimi", kimi_node)
    builder.add_node("qwen", qwen_node)
    builder.add_node("openai_oss", openai_oss_node)
    builder.add_node("aggregator", aggregator_node)
    # --- Fan-Out : START -> All Agents (parallel) --- 
    builder.add_edge(START, "kimi")
    builder.add_edge(START, "qwen")
    builder.add_edge(START, "openai_oss")
    # --- Fan-In : All Agents -> Aggregator (serial) --- 
    builder.add_edge("kimi", "aggregator")
    builder.add_edge("qwen", "aggregator")
    builder.add_edge("openai_oss", "aggregator")
    # --- End : Aggregator -> END --- 
    builder.add_edge("aggregator", END)
    # --- Compile the Graph --- 
    graph = builder.compile()
    return graph
# --- Singleton Export --- 
email_graph = assemble_graph()
