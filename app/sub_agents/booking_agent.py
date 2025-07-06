import os
from pydantic import BaseModel, Field

from google.adk.agents import LlmAgent

from ..core.configs.utils import load_agent_config, AIProvider
from ..utils.log_setup import setup_logger
from .prompts.booking_prompt import INSTRUCTIONS

logger = setup_logger(__name__)

config = load_agent_config(
    provider=AIProvider.GOOGLE, config_path="app/core/configs/yaml/booking.yaml"
)

if config.GOOGLE_API_KEY is not None:
    os.environ["GOOGLE_API_KEY"] = config.GOOGLE_API_KEY
else:
    logger.warning("GOOGLE_API_KEY is None and was not set in environment variables.")


class BookingInput(BaseModel):
    query: str = Field(description="The user's query")


booking_agent = LlmAgent(
    name=config.agent_settings.name,
    description=config.agent_settings.description,
    instruction=INSTRUCTIONS,
    model=config.agent_settings.google_model,
    input_schema=BookingInput,
    # output_schema=BookingOutput,
    output_key="booking_output_key",
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
    tools=[],
)