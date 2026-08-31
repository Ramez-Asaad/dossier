"""Entrypoint: `uvicorn main:app --reload` from the backend/ directory."""

from dotenv import load_dotenv

load_dotenv()

from app.api.routes import create_app  # noqa: E402 (must load .env first)

app = create_app()
