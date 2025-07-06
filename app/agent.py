from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool
from google.adk.agents.callback_context import CallbackContext
from google.genai import types

from .core.configs.utils import AIProvider, load_agent_config
from .core.callbacks import CustomerDataManager
from .sub_agents.consulting_agent import consult_agent
from .sub_agents.information_agent import info_agent
from .sub_agents.booking_agent import booking_agent
from .sub_agents.image_analysis_agent import image_agent_flow
from .execution_prompt import get_execution_instructions

import os
from typing import Optional

config = load_agent_config(
    provider=AIProvider.GOOGLE, config_path="app/core/configs/yaml/execution.yaml"
)

if config.GOOGLE_API_KEY is not None:
    os.environ["GOOGLE_API_KEY"] = config.GOOGLE_API_KEY
else:
    raise ValueError("GOOGLE_API_KEY is not set in the configuration.")


def setup_before_agent_callback(
    callback_context: CallbackContext,
) -> Optional[types.Content] | None:
    """Loads customer information into state before the agent runs."""
    CustomerDataManager.load_customer_info(callback_context)
    return None


execution_agent = LlmAgent(
    name=config.agent_settings.name,
    description=config.agent_settings.description,
    instruction=get_execution_instructions,
    model=config.agent_settings.google_model,
    output_key="execution_output_key",
    before_agent_callback=setup_before_agent_callback,
    disallow_transfer_to_parent=False,
    disallow_transfer_to_peers=True,
    tools=[
        AgentTool(agent=consult_agent),
        AgentTool(agent=info_agent),
        AgentTool(agent=booking_agent),
        AgentTool(agent=image_agent_flow),
    ],
)   

root_agent = execution_agent
