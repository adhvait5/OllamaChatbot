"""Streamlit app: LLM Experiment Tracking Platform."""
import streamlit as st
import pandas as pd

from llm_tracker.llm_chain import get_llm_chain
from llm_tracker.services.project_service import get_all_projects, create_project
from llm_tracker.services.run_service import create_run, get_runs_by_project
from llm_tracker.utils.timing import measure_latency

# Available Ollama models (already downloaded)
AVAILABLE_MODELS = ["mistral", "llama3"]

# Session state defaults
if "context" not in st.session_state:
    st.session_state.context = ""
if "selected_project_id" not in st.session_state:
    st.session_state.selected_project_id = None
if "project_options" not in st.session_state:
    st.session_state.project_options = {}
if "selected_model" not in st.session_state:
    st.session_state.selected_model = AVAILABLE_MODELS[0]

# Ensure we have at least one project
def ensure_projects():
    projects = get_all_projects()
    if not projects:
        new_project = create_project("Default Project")
        if new_project:
            projects = [new_project]
    if projects and st.session_state.selected_project_id is None:
        st.session_state.selected_project_id = str(projects[0]["id"])
    # Build id -> name map for dropdown
    st.session_state.project_options = {str(p["id"]): p["name"] for p in projects}
    return projects

# Sidebar
st.sidebar.markdown("## Ollama Experiment Tracker")
st.sidebar.markdown("---")

try:
    ensure_projects()
except Exception as e:
    err_str = str(e)
    if "PGRST205" in err_str or "could not find the table" in err_str.lower():
        st.sidebar.error("Tables missing in Supabase. Create them first:")
        st.sidebar.markdown("1. Open [Supabase Dashboard](https://supabase.com/dashboard) → your project")
        st.sidebar.markdown("2. Go to **SQL Editor**, paste and run the contents of `supabase_schema.sql`")
        st.sidebar.code(err_str, language=None)
    else:
        st.sidebar.error("Database not configured. Set SUPABASE_URL and SUPABASE_KEY in .env")
        st.sidebar.code(err_str, language=None)
    st.stop()

projects = get_all_projects()
if not projects:
    st.sidebar.warning("No projects yet. Create one below.")
else:
    options = st.session_state.project_options
    selected_id = st.session_state.selected_project_id
    choice = st.sidebar.selectbox(
        "Project",
        options=list(options.keys()),
        format_func=lambda k: options.get(k, k),
        index=list(options.keys()).index(selected_id) if selected_id in options else 0,
    )
    if choice:
        st.session_state.selected_project_id = choice

st.sidebar.markdown("---")
with st.sidebar.expander("Create new project"):
    new_name = st.text_input("Project name", key="new_project_name")
    if st.button("Create project"):
        if new_name and new_name.strip():
            try:
                created = create_project(new_name.strip())
                if created:
                    st.session_state.project_options[str(created["id"])] = created["name"]
                    st.session_state.selected_project_id = str(created["id"])
                    st.rerun()
            except Exception as e:
                st.error(str(e))
        else:
            st.warning("Enter a name.")

st.sidebar.markdown("**Model**")
st.session_state.selected_model = st.sidebar.selectbox(
    "Choose model",
    options=AVAILABLE_MODELS,
    index=AVAILABLE_MODELS.index(st.session_state.selected_model) if st.session_state.selected_model in AVAILABLE_MODELS else 0,
    label_visibility="collapsed",
)
st.sidebar.markdown("---")
if st.sidebar.button("Clear conversation"):
    st.session_state.context = ""
    st.rerun()

st.sidebar.markdown("---")

# Main: Chat
st.title("Chat")
user_input = st.chat_input("Ask me anything")

if user_input:
    chain = get_llm_chain(model_name=st.session_state.selected_model)
    context = st.session_state.context
    with st.spinner("Generating..."):
        result, latency_sec = measure_latency(
            lambda: chain.invoke({"context": context, "question": user_input})
        )
    response_text = result if isinstance(result, str) else str(result)

    st.chat_message("user").write(user_input)
    st.chat_message("assistant").write(response_text)

    st.session_state.context += f"\nUser: {user_input}\nAI: {response_text}"

    # Log run (only prompt + response, not full context)
    project_id = st.session_state.selected_project_id
    if project_id:
        try:
            create_run(
                project_id=project_id,
                model_name=st.session_state.selected_model,
                prompt=user_input,
                response=response_text,
                latency=round(latency_sec, 4),
            )
        except Exception as e:
            st.warning(f"Run not logged: {e}")
    st.rerun()

# Show existing conversation in main area (from session state)
if st.session_state.context.strip():
    st.markdown("#### Conversation history")
    st.text_area("Context", st.session_state.context, height=120, disabled=True)

# Dashboard section
st.markdown("---")
st.markdown("## Dashboard")

project_id = st.session_state.selected_project_id
if not project_id:
    st.info("Select a project in the sidebar to see runs.")
else:
    try:
        runs = get_runs_by_project(project_id)
    except Exception as e:
        st.error(f"Could not load runs: {e}")
        runs = []

    if not runs:
        st.info("No runs yet for this project. Send a message above to log one.")
    else:
        # Metrics
        total = len(runs)
        latencies = [r["latency"] for r in runs if r.get("latency") is not None]
        avg_lat = sum(latencies) / len(latencies) if latencies else 0
        fastest = min(latencies) if latencies else 0
        slowest = max(latencies) if latencies else 0

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total runs", total)
        col2.metric("Avg latency (s)", f"{avg_lat:.3f}")
        col3.metric("Fastest (s)", f"{fastest:.3f}")
        col4.metric("Slowest (s)", f"{slowest:.3f}")

        # Line chart: latency over time (reverse so oldest left, newest right)
        chart_data = pd.DataFrame(
            [
                {"run": i + 1, "latency": r["latency"], "created_at": r.get("created_at", "")}
                for i, r in enumerate(reversed(runs))
            ]
        )
        if not chart_data.empty:
            st.line_chart(chart_data.set_index("run")[["latency"]])

        # Table with expandable prompt/response
        st.markdown("#### Recent runs")
        for r in runs[:20]:
            created = r.get("created_at", "")[:19] if r.get("created_at") else ""
            snippet = (r.get("prompt") or "")[:60] + ("..." if len(r.get("prompt") or "") > 60 else "")
            with st.expander(f"{created} | {r.get('model_name', '')} | {r.get('latency', 0):.2f}s | {snippet}"):
                st.markdown("**Prompt**")
                st.text(r.get("prompt") or "")
                st.markdown("**Response**")
                st.text(r.get("response") or "")
