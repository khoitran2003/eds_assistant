import os
from pydantic import BaseModel, Field

from google.adk.agents import LlmAgent

# from .sub_agents import RAGAgent, SQLAgent
from ..core.configs.utils import load_agent_config, AIProvider
from .prompts.info_prompt import INSTRUCTIONS_V2

config = load_agent_config(
    provider=AIProvider.GOOGLE, config_path="app/core/configs/yaml/information.yaml"
)

if config.GOOGLE_API_KEY is not None:
    os.environ["GOOGLE_API_KEY"] = config.GOOGLE_API_KEY
else:
    raise ValueError("GOOGLE_API_KEY is not set in the configuration.")


class InfoInput(BaseModel):
    query: str = Field(description="The user's query")


info_agent = LlmAgent(
    name=config.agent_settings.name,
    description=config.agent_settings.description,
    instruction=INSTRUCTIONS_V2,
    model=config.agent_settings.google_model,
    input_schema=InfoInput,
    output_key="info_output_key",
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
)
