import os
from unittest.mock import patch
from app import llm


def test_agent_model_routing():
    with patch.dict(os.environ, {"LLM_PROVIDER": "anthropic", "ANTHROPIC_API_KEY": "test"}):
        with patch("app.llm._call_anthropic") as mock_call:
            mock_call.return_value = ({"status": "ok"}, 768)
            llm.call_json("sys", "usr", agent_name="profiler")
            mock_call.assert_called_once()
            args, _ = mock_call.call_args
            # Verify the routed model for profiler under anthropic is claude-haiku-3-5
            assert args[2] == "claude-haiku-3-5"
