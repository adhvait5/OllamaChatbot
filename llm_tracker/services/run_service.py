"""Run logging and retrieval via Supabase."""
from llm_tracker.database import get_supabase_client


def create_run(project_id: str, model_name: str, prompt: str, response: str, latency: float):
    """Insert one run and return the created row."""
    client = get_supabase_client()
    response_data = (
        client.table("runs")
        .insert(
            {
                "project_id": project_id,
                "model_name": model_name,
                "prompt": prompt,
                "response": response,
                "latency": latency,
            }
        )
        .execute()
    )
    data = response_data.data
    return data[0] if data else None


def get_runs_by_project(project_id: str):
    """Fetch runs for a project, ordered by created_at DESC."""
    client = get_supabase_client()
    response = (
        client.table("runs")
        .select("*")
        .eq("project_id", project_id)
        .order("created_at", desc=True)
        .execute()
    )
    return response.data or []
