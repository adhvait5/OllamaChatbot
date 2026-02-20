"""Launch the LLM Tracker Streamlit app. Run from repo root: python run.py"""
import streamlit.web.cli as stcli
import sys
from pathlib import Path

if __name__ == "__main__":
    script_dir = Path(__file__).resolve().parent
    app_path = script_dir / "llm_tracker" / "app.py"
    sys.argv = ["streamlit", "run", str(app_path)] + sys.argv[1:]
    sys.exit(stcli.main())
