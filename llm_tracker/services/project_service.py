"""Project CRUD via Supabase."""
from llm_tracker.database import get_supabase_client


def get_all_projects():
    """Fetch all projects, ordered by created_at ascending."""
    client = get_supabase_client()
    response = client.table("projects").select("*").order("created_at").execute()
    return response.data or []


def create_project(name: str):
    """Insert a project and return the created row."""
    client = get_supabase_client()
    response = client.table("projects").insert({"name": name}).execute()
    data = response.data
    return data[0] if data else None
