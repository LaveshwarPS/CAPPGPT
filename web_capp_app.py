"""Web version of CAPP Turning Planner using Streamlit.

Run:
    streamlit run web_capp_app.py
"""

from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import streamlit as st

from capp_turning_planner import generate_turning_plan
from chat_ollama import query_ollama, OllamaError, get_provider


OLLAMA_AI_TIMEOUT = int(os.getenv("OLLAMA_AI_TIMEOUT", "120"))


def _init_state() -> None:
    if "analysis_result" not in st.session_state:
        st.session_state.analysis_result = None
    if "uploaded_name" not in st.session_state:
        st.session_state.uploaded_name = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []


def _save_uploaded_step(uploaded_file) -> str:
    suffix = Path(uploaded_file.name).suffix or ".step"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.getvalue())
        return tmp.name


def _summary_text(result: Dict, selected_name: str) -> str:
    operations = result.get("operations", [])
    tools = result.get("tools", [])
    total_time = sum(op.get("estimated_time", 0) for op in operations)
    return (
        "TURNING PROCESS PLAN SUMMARY\n\n"
        f"File: {selected_name}\n"
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        f"Turning score: {result.get('turning_score', 'N/A')}/100\n"
        f"Suitable for turning: {'YES' if result.get('success') else 'NO'}\n\n"
        f"Operations: {len(operations)}\n"
        f"Tools: {len(tools)}\n"
        f"Total machining time: {total_time:.1f} min\n"
    )


def _build_chat_context(result: Dict) -> str:
    operations = result.get("operations", [])
    tools = result.get("tools", [])
    top_ops = "\n".join(
        f"- {op.get('name')} | {op.get('type')} | {op.get('spindle_speed')} RPM | {op.get('feed_rate')} mm/rev"
        for op in operations[:6]
    )
    top_tools = "\n".join(
        f"- {tool.get('name')} ({tool.get('type')})"
        for tool in tools[:6]
    )
    return (
        "You are a CAPP turning assistant. Use this plan context:\n"
        f"Turning score: {result.get('turning_score')}\n"
        f"Operations:\n{top_ops}\n"
        f"Tools:\n{top_tools}\n"
    )


def main() -> None:
    st.set_page_config(
        page_title="CAPP Turning Planner - Web",
        page_icon="🛠️",
        layout="wide",
    )
    _init_state()

    st.title("🛠️ CAPP Turning Process Planner")
    st.caption("Upload STEP files and generate optimized turning process plans.")

    with st.sidebar:
        st.header("File & Options")
        uploaded = st.file_uploader("Select STEP file", type=["step", "stp"])
        with_ai = st.checkbox("Include AI Optimization", value=True)
        save_json = st.checkbox("Prepare JSON Export", value=True)
        model = st.selectbox("AI Model", ["phi", "llama2", "neural-chat"], index=0)
        st.markdown(f"Provider: `{get_provider()}`")
        analyze = st.button("Analyze & Generate Plan", use_container_width=True, type="primary")

    if analyze:
        if not uploaded:
            st.error("Please upload a STEP file first.")
        else:
            st.session_state.uploaded_name = uploaded.name
            temp_path = _save_uploaded_step(uploaded)
            with st.spinner("Analyzing STEP file and generating process plan..."):
                result = generate_turning_plan(
                    temp_path,
                    model=model,
                    with_ai=with_ai,
                    save_json=save_json,
                )
            st.session_state.analysis_result = result
            st.session_state.chat_history = []
            if result.get("success"):
                st.success(f"Completed: {uploaded.name}")
            else:
                st.error(result.get("error", "Analysis failed"))

    result = st.session_state.analysis_result
    selected_name = st.session_state.uploaded_name or "N/A"

    tab_ops, tab_tools, tab_summary, tab_ai, tab_chat = st.tabs(
        ["Operations", "Tools", "Summary", "AI Recommendations", "Chat with AI"]
    )

    with tab_ops:
        if result and result.get("operations"):
            # st.table avoids AG Grid frontend module loading issues on some browsers.
            st.table(result["operations"])
        else:
            st.info("Run analysis to see operations.")

    with tab_tools:
        if result and result.get("tools"):
            st.table(result["tools"])
        else:
            st.info("Run analysis to see required tools.")

    with tab_summary:
        if result:
            text = _summary_text(result, selected_name)
            st.text_area("Summary", value=text, height=260)
            if result.get("json_file") and Path(result["json_file"]).exists():
                with open(result["json_file"], "rb") as f:
                    st.download_button(
                        "Download JSON",
                        data=f.read(),
                        file_name=Path(result["json_file"]).name,
                        mime="application/json",
                    )
            elif result.get("success"):
                payload = json.dumps(result, indent=2, default=str).encode("utf-8")
                st.download_button(
                    "Download JSON",
                    data=payload,
                    file_name=f"{Path(selected_name).stem}_turning_plan.json",
                    mime="application/json",
                )
        else:
            st.info("Run analysis to see summary.")

    with tab_ai:
        if result:
            ai_text = (
                result.get("ai_recommendations", {}).get("optimizations")
                or "No AI recommendations available."
            )
            st.text_area("AI Optimization", value=ai_text, height=420)
        else:
            st.info("Run analysis to get AI recommendations.")

    with tab_chat:
        st.caption("Ask about process planning, tools, speeds/feeds, or improvements.")
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        question = st.chat_input("Ask about this model/process plan...")
        if question:
            st.session_state.chat_history.append({"role": "user", "content": question})
            with st.chat_message("user"):
                st.markdown(question)

            if not result:
                answer = "Upload and analyze a STEP file first, then I can answer with context."
            else:
                prompt = (
                    _build_chat_context(result)
                    + "\nUser question:\n"
                    + question
                    + "\nRespond briefly with practical machining guidance."
                )
                try:
                    answer = query_ollama(prompt, model=model, timeout=OLLAMA_AI_TIMEOUT)
                    if not answer.strip():
                        answer = "I got an empty response. Please try again."
                except OllamaError as e:
                    answer = f"Error: {e}"

            st.session_state.chat_history.append({"role": "assistant", "content": answer})
            with st.chat_message("assistant"):
                st.markdown(answer)


if __name__ == "__main__":
    main()
