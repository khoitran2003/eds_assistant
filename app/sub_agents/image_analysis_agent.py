import os
from typing import List
from pydantic import BaseModel, Field

from google.adk.agents import LlmAgent, SequentialAgent

from ..core.configs.utils import load_agent_config, AIProvider
from .prompts.image_analysis_prompt import INSTRUCTIONS

from .consulting_agent import consult_agent

config = load_agent_config(
    provider=AIProvider.GOOGLE, config_path="app/core/configs/yaml/image_analysis.yaml"
)

if config.GOOGLE_API_KEY is not None:
    os.environ["GOOGLE_API_KEY"] = config.GOOGLE_API_KEY
else:
    raise ValueError("GOOGLE_API_KEY is not set in the configuration.")

class ImageAnalysisOutput(BaseModel):
    image_analysis_output_key: str = Field(description="The response from the agent")

image_analysis_agent = LlmAgent(
    name=config.agent_settings.name,
    description=config.agent_settings.description,
    instruction=INSTRUCTIONS,
    model=config.agent_settings.google_model,
    output_schema=ImageAnalysisOutput,
    output_key="image_analysis_output_key",
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
)

image_agent_flow = SequentialAgent(
    name="Image_Analysis_Agent_Flow",
    description="Image Analysis Agent Flow",
    sub_agents=[image_analysis_agent, consult_agent],
)
