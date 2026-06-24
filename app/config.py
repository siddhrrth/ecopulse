import os
import sys
from pathlib import Path
from dataclasses import dataclass
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "False")

@dataclass
class AgentConfig:
    # Reads model from environment GEMINI_MODEL. Default gemini-2.5-flash (the 1.5 family is retired and returns 404). Use gemini-2.5-flash-lite for tighter free-tier quota.
    model: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    mcp_server_port: int = 8090
    max_iterations: int = 3
    pii_redaction_enabled: bool = True
    injection_detection_enabled: bool = True

import sys
config = AgentConfig()
print(f"CONFIG LOADED: GEMINI_MODEL={config.model}", file=sys.stderr, flush=True)
