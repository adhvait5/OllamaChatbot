"""Load and expose environment configuration."""
import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from OllamaChatbot directory so it works regardless of cwd
# Try .env first, then .env.example if .env is missing
_root = Path(__file__).resolve().parent.parent
_env_path = _root / ".env"
_env_example_path = _root / ".env.example"
if _env_path.exists():
    load_dotenv(dotenv_path=_env_path)
elif _env_example_path.exists():
    load_dotenv(dotenv_path=_env_example_path)

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
MODEL_NAME = os.getenv("OLLAMA_MODEL", "mistral")
