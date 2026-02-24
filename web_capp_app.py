"""Web version of CAPP Turning Planner using Streamlit.

Run:
    streamlit run web_capp_app.py
"""

from __future__ import annotations

import json
import os
import re
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import streamlit as st

from capp_turning_planner import (
    generate_turning_plan,
    DEFAULT_MATERIAL_PROFILE,
    DEFAULT_MACHINE_PROFILE,
    TOP_MATERIALS_INDIA,
    TOP_MACHINE_PROFILES_INDIA,
)
from chat_ollama import query_ollama, OllamaError, set_provider


OLLAMA_AI_TIMEOUT = int(os.getenv("OLLAMA_AI_TIMEOUT", "120"))
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
MATERIAL_OPTIONS = TOP_MATERIALS_INDIA
MACHINE_OPTIONS = TOP_MACHINE_PROFILES_INDIA


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


def _detect_step_protocol_from_bytes(file_bytes: bytes) -> Dict[str, str]:
    text = file_bytes[:128 * 1024].decode("latin-1", errors="ignore")
    match = re.search(r"FILE_SCHEMA\s*\(\s*\((.*?)\)\s*\)\s*;", text, re.IGNORECASE | re.DOTALL)
    if not match:
        return {"protocol": "Unknown", "schema": "Unknown", "legacy": "unknown"}

    schema_raw = re.sub(r"[\s'\"()]", "", match.group(1))
    schema_upper = schema_raw.upper()
    if "AP242" in schema_upper or "MANAGED_MODEL_BASED_3D_ENGINEERING" in schema_upper:
        protocol = "AP242"
    elif "AP214" in schema_upper or "AUTOMOTIVE_DESIGN" in schema_upper:
        protocol = "AP214"
    elif "AP203" in schema_upper or "CONFIG_CONTROL_DESIGN" in schema_upper:
        protocol = "AP203"
    else:
        protocol = "Unknown"

    legacy = "yes" if protocol in {"AP203", "AP214"} else "no"
    if protocol == "Unknown":
        legacy = "unknown"
    return {"protocol": protocol, "schema": schema_raw or "Unknown", "legacy": legacy}


def _summary_text(result: Dict, selected_name: str) -> str:
    operations = result.get("operations", [])
    tools = result.get("tools", [])
    total_time = sum(op.get("estimated_time", 0) for op in operations)
    return (
        "TURNING PROCESS PLAN SUMMARY\n\n"
        f"File: {selected_name}\n"
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        f"STEP protocol: {result.get('step_protocol', 'Unknown')}\n"
        f"STEP schema: {result.get('step_schema', 'Unknown')}\n\n"
        f"Material profile: {result.get('material_profile', DEFAULT_MATERIAL_PROFILE)}\n"
        f"Machine profile: {result.get('machine_profile', DEFAULT_MACHINE_PROFILE)}\n\n"
        f"Tolerance target: {result.get('tolerance_mm') if result.get('tolerance_mm') is not None else 'Not specified'} mm\n"
        f"Surface target: {result.get('surface_roughness_ra') if result.get('surface_roughness_ra') is not None else 'Not specified'} um Ra\n\n"
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


def _operations_table_rows(result: Dict) -> List[Dict]:
    rows: List[Dict] = []
    for op in result.get("operations", []):
        rows.append(
            {
                "Op #": op.get("operation_id"),
                "Operation": op.get("name", ""),
                "Description": op.get("description", ""),
                "Type": op.get("type", ""),
                "Tool": op.get("tool", ""),
                "RPM": op.get("spindle_speed"),
                "Feed (mm/rev)": op.get("feed_rate"),
                "DOC (mm)": op.get("depth_of_cut"),
                "Coolant": op.get("coolant", ""),
                "Time (min)": op.get("estimated_time"),
                "Thread": op.get("thread_spec", ""),
            }
        )
    return rows


def _tools_table_rows(result: Dict) -> List[Dict]:
    rows: List[Dict] = []
    for tool in result.get("tools", []):
        rows.append(
            {
                "Tool #": tool.get("tool_id"),
                "Name": tool.get("name", ""),
                "Type": tool.get("type", ""),
                "Material": tool.get("material", ""),
                "Coating": tool.get("coating", ""),
                "Description": tool.get("description", ""),
            }
        )
    return rows


def _render_turning_limits_tab(result: Dict) -> None:
    scope = result.get("turning_scope", "none")
    strict_turnable = bool(result.get("strict_turnable", False))
    partial_turnable = bool(result.get("partial_turnable", False))
    recommended = result.get("recommended_process")
    alternatives = result.get("alternative_processes", [])
    limit_reasons = result.get("turning_limitations", [])
    gate_reasons = result.get("turning_gate_reasons", [])

    if scope == "full" and strict_turnable:
        st.success("CAPP scope: FULL TURNING")
        st.write("Model is fully turnable under the current strict gate.")
    elif scope == "partial" and partial_turnable:
        st.warning("CAPP scope: PARTIAL TURNING")
        st.write("CAPP is generated only for turnable operations. Non-turnable features are excluded.")
    else:
        st.error("CAPP scope: NO TURNING")
        st.write("This model is not suitable for turning CAPP under current rules.")

    if recommended:
        st.info(f"Best primary process for excluded features: {str(recommended).replace('_', ' ').upper()}")
    if alternatives:
        pretty = ", ".join(str(p).replace("_", " ").upper() for p in alternatives)
        st.write(f"Other process options: {pretty}")

    if limit_reasons:
        st.write("Turning limitations:")
        for r in limit_reasons:
            st.write(f"- {r}")

    if gate_reasons:
        with st.expander("Detailed gate reasoning"):
            for reason in gate_reasons:
                st.write(f"- {reason}")


def _render_validation_dialog(result: Dict) -> None:
    validation = result.get("validation") or {}
    status = validation.get("status", "pass")
    messages = validation.get("messages", [])
    features = validation.get("feature_detection", {})
    metrics = features.get("metrics", {})

    def _render_content() -> None:
        if status == "fail":
            st.error("Validation status: FAIL")
        elif status == "warn":
            st.warning("Validation status: WARN")
        else:
            st.success("Validation status: PASS")

        for msg in messages:
            level = msg.get("level", "pass").upper()
            st.write(f"[{level}] {msg.get('title', '')}: {msg.get('detail', '')}")

        st.caption(
            "Geometry metrics: "
            f"edge/face={metrics.get('edge_face_ratio', 'n/a')}, "
            f"cylinder={metrics.get('cylinder_surfaces', 'n/a')}, "
            f"cone={metrics.get('cone_surfaces', 'n/a')}, "
            f"torus={metrics.get('torus_surfaces', 'n/a')}"
        )

    if hasattr(st, "popover"):
        with st.popover("Validation"):
            _render_content()
    else:
        with st.expander("Validation"):
            _render_content()


def main() -> None:
    # Keep web app provider fixed to Gemini.
    set_provider("gemini")

    st.set_page_config(
        page_title="CAPP Turning Planner - Web",
        page_icon="ðŸ› ï¸",
        layout="wide",
    )
    _init_state()
    st.markdown("### CAPP Turning")
    st.markdown(
        """
        <style>
            .block-container {
                padding-top: 0.75rem;
                padding-bottom: 1rem;
            }
            [data-testid="stDataFrame"] thead th div {
                white-space: nowrap;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.header("File & Options")
        uploaded = st.file_uploader("Select STEP file", type=["step", "stp"])
        uploaded_step_info = None
        continue_with_legacy = True
        if uploaded is not None:
            uploaded_step_info = _detect_step_protocol_from_bytes(uploaded.getvalue())
            st.caption(
                f"STEP schema: {uploaded_step_info.get('protocol', 'Unknown')} "
                f"({uploaded_step_info.get('schema', 'Unknown')})"
            )
            if uploaded_step_info.get("protocol") in {"AP203", "AP214"}:
                st.warning(
                    "This file uses an older STEP schema. If possible, export and upload AP242 for better feature fidelity."
                )
                continue_with_legacy = st.checkbox(
                    "Continue with this older STEP version",
                    value=False,
                    key=f"continue_legacy_{uploaded.name}",
                )
        with_ai = st.checkbox("Include AI Optimization", value=True)
        save_json = st.checkbox("Prepare JSON Export", value=True)
        material_profile = st.selectbox(
            "Workpiece Material",
            MATERIAL_OPTIONS,
            index=MATERIAL_OPTIONS.index(DEFAULT_MATERIAL_PROFILE),
        )
        machine_profile = st.selectbox(
            "Lathe Machine",
            MACHINE_OPTIONS,
            index=MACHINE_OPTIONS.index(DEFAULT_MACHINE_PROFILE),
        )
        tolerance_mm = st.number_input(
            "Tolerance (+/- mm)",
            min_value=0.005,
            max_value=1.0,
            value=0.10,
            step=0.005,
            format="%.3f",
        )
        surface_roughness_ra = st.number_input(
            "Surface Finish (Ra um)",
            min_value=0.2,
            max_value=12.5,
            value=3.2,
            step=0.1,
            format="%.2f",
        )
        model = GEMINI_MODEL
        analyze = st.button("Analyze & Generate Plan", use_container_width=True, type="primary")

    if analyze:
        if not uploaded:
            st.error("Please upload a STEP file first.")
        elif uploaded_step_info and uploaded_step_info.get("protocol") in {"AP203", "AP214"} and not continue_with_legacy:
            st.error("Please confirm continue for AP203/AP214, or upload an AP242 STEP file.")
        else:
            st.session_state.uploaded_name = uploaded.name
            temp_path = _save_uploaded_step(uploaded)
            with st.spinner("Analyzing STEP file and generating process plan..."):
                result = generate_turning_plan(
                    temp_path,
                    model=model,
                    with_ai=with_ai,
                    save_json=save_json,
                    material_profile=material_profile,
                    machine_profile=machine_profile,
                    tolerance_mm=tolerance_mm,
                    surface_roughness_ra=surface_roughness_ra,
                )
            st.session_state.analysis_result = result
            st.session_state.chat_history = []
            if result.get("success"):
                st.success(f"Completed: {uploaded.name}")
                if result.get("turning_scope") == "partial":
                    st.warning("Generated limited CAPP: only turnable portion included.")
            else:
                st.error(result.get("error", "Analysis failed"))
                recommended = result.get("recommended_process")
                alternatives = result.get("alternative_processes", [])
                gate_reasons = result.get("turning_gate_reasons", [])
                if recommended:
                    st.warning(f"Recommended machining type: {recommended.replace('_', ' ').upper()}")
                if alternatives:
                    pretty = ", ".join(p.replace("_", " ").upper() for p in alternatives)
                    st.info(f"Other viable process options: {pretty}")
                if gate_reasons:
                    with st.expander("Why turning was rejected"):
                        for reason in gate_reasons:
                            st.write(f"- {reason}")

    result = st.session_state.analysis_result
    selected_name = st.session_state.uploaded_name or "N/A"

    tab_ops, tab_tools, tab_summary, tab_ai, tab_limits, tab_chat = st.tabs(
        ["Operations", "Tools", "Summary", "AI Recommendations", "Turning Limits", "Chat with AI"]
    )

    with tab_ops:
        if result and result.get("operations"):
            _render_validation_dialog(result)
            st.dataframe(
                _operations_table_rows(result),
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Description": st.column_config.TextColumn(width="large"),
                    "Tool": st.column_config.TextColumn(width="medium"),
                    "Operation": st.column_config.TextColumn(width="medium"),
                    "Type": st.column_config.TextColumn(width="small"),
                    "Thread": st.column_config.TextColumn(width="medium"),
                },
            )
        else:
            st.info("Run analysis to see operations.")

    with tab_tools:
        if result and result.get("tools"):
            st.dataframe(
                _tools_table_rows(result),
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Description": st.column_config.TextColumn(width="large"),
                    "Name": st.column_config.TextColumn(width="medium"),
                    "Type": st.column_config.TextColumn(width="medium"),
                },
            )
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
            st.markdown(ai_text)
        else:
            st.info("Run analysis to get AI recommendations.")

    with tab_limits:
        if result:
            _render_turning_limits_tab(result)
        else:
            st.info("Run analysis to see turning limitations and process guidance.")

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


