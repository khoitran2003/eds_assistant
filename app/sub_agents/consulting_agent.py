import os
from typing import Any
from pydantic import BaseModel, Field

from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool
from ..core.configs.utils import load_agent_config, AIProvider
from .prompts.consult_prompt import INSTRUCTIONS


config = load_agent_config(
    provider=AIProvider.GOOGLE, config_path="app/core/configs/yaml/consulting.yaml"
)

if config.GOOGLE_API_KEY is not None:
    os.environ["GOOGLE_API_KEY"] = config.GOOGLE_API_KEY
else:
    raise ValueError("GOOGLE_API_KEY is not set in the configuration.")


class ConsultInput(BaseModel):
    query: str = Field(description="The user's query")


class ConsultOutput(BaseModel):
    consult_output_key: Any = Field(description="The response from the agent")

consult_agent = LlmAgent(
    name=config.agent_settings.name,
    description=config.agent_settings.description,
    instruction=INSTRUCTIONS,
    model=config.agent_settings.google_model,
    input_schema=ConsultInput,
    output_key="consult_output_key",
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
)