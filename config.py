"""
Configuration — loads API keys and settings from environment / .env file.

Copy .env.example → .env and fill in your keys before running.
"""

import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent / ".env")
except ImportError:
    pass  # python-dotenv not installed; rely on shell environment

# ── API keys ──────────────────────────────────────────────────────────────────
ANTHROPIC_API_KEY: str = os.environ.get("ANTHROPIC_API_KEY", "")
OPENAI_API_KEY: str = os.environ.get("OPENAI_API_KEY", "")

# ── ChromaDB ──────────────────────────────────────────────────────────────────
CHROMA_PATH: str = os.environ.get("CHROMA_PATH", "./chroma_db")
COLLECTION_NAME: str = "customer_feedback"

# ── Model names ───────────────────────────────────────────────────────────────
ORCHESTRATOR_MODEL: str = "claude-sonnet-4-6"
DIAGNOSIS_MODEL: str = "claude-sonnet-4-6"
CRITIC_MODEL: str = "claude-sonnet-4-6"
STRATEGY_MODEL: str = "claude-haiku-4-5-20251001"
DATA_INTEL_MODEL: str = "gpt-3.5-turbo"
EMBEDDING_MODEL: str = "text-embedding-3-small"
