import os
import yaml
from enum import Enum
from typing import Optional, Dict, Any, Union
from pydantic import BaseModel, Field, ConfigDict
from pydantic_settings import BaseSettings, SettingsConfigDict

from ...utils.log_setup import setup_logger

logger = setup_logger(__name__)

# Define default config path
_DEFAULT_CONFIG_PATH = "app/core/configs/yaml/_default_agent.yaml"


def load_agent_config_yaml(path: str = _DEFAULT_CONFIG_PATH) -> dict:
    """
    Load agent configuration from a YAML file.

    Args:
        path (str): Path to the YAML configuration file.

    Returns:
        dict: Loaded configuration as a dictionary.
    """
    with open(path, "r") as file:
        config = yaml.safe_load(file)
    return config


config = load_agent_config_yaml()


# Define the AI provider enum
class AIProvider(str, Enum):
    """Enum for supported AI providers"""

    GOOGLE = "google"
    OPENAI = "openai"
    QWEN = "qwen"
    ANTHROPIC = "anthropic"


class ProviderConfig(BaseModel):
    """Configuration for a specific AI provider"""

    api_key: Optional[str] = None
    model: str = ""
    endpoint: Optional[str] = None
    additional_params: Dict[str, Any] = Field(default_factory=dict)
    enabled: bool = False

    model_config = ConfigDict(arbitrary_types_allowed=True)


class AgentModel(BaseModel):
    """Base agent model parameters"""

    name: str = Field(default=config["agent"]["name"])
    version: str = Field(default=config["agent"]["version"])
    description: str = Field(default=config["agent"]["description"])
    instructions: str = Field(default="")
    default_provider: AIProvider = Field(default=AIProvider.GOOGLE)
    providers: Dict[AIProvider, ProviderConfig] = Field(default_factory=dict)

    # Provider model names from YAML config
    google_model: str = Field(
        default=config.get("models", {}).get("google", "gemini-1.5-pro")
    )
    openai_model: str = Field(default=config.get("models", {}).get("openai", "gpt-4o"))
    qwen_model: str = Field(default=config.get("models", {}).get("qwen", "qwen-max"))
    anthropic_model: str = Field(
        default=config.get("models", {}).get("anthropic", "claude-3-7-sonnet")
    )


class AgentConfig(BaseSettings):
    """Main configuration class with support for multiple AI providers"""

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../.env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Base settings
    agent_settings: AgentModel = Field(default=AgentModel())

    # Google AI settings
    GOOGLE_CLOUD_PROJECT: str = Field(default="my_project")
    GOOGLE_CLOUD_LOCATION: str = Field(default="us-central1")
    GOOGLE_GENAI_USE_VERTEXAI: str = Field(default="1")
    GOOGLE_API_KEY: Optional[str] = Field(
        default=None, json_schema_extra={"env": "GOOGLE_API_KEY"}
    )

    # OpenAI settings
    OPENAI_API_KEY: Optional[str] = Field(
        default=None, json_schema_extra={"env": "OPENAI_API_KEY"}
    )
    OPENAI_ORG_ID: Optional[str] = Field(
        default=None, json_schema_extra={"env": "OPENAI_ORG_ID"}
    )

    # Qwen settings
    QWEN_API_KEY: Optional[str] = Field(
        default=None, json_schema_extra={"env": "QWEN_API_KEY"}
    )
    QWEN_API_ENDPOINT: Optional[str] = Field(
        default=None, json_schema_extra={"env": "QWEN_API_ENDPOINT"}
    )

    # Anthropic settings
    ANTHROPIC_API_KEY: Optional[str] = Field(
        default=None, json_schema_extra={"env": "ANTHROPIC_API_KEY"}
    )


def load_agent_config(
    provider: Optional[Union[AIProvider, str]] = None,
    config_path: Optional[str] = _DEFAULT_CONFIG_PATH,
) -> AgentConfig:
    """
    Load and configure the intention agent with the specified AI provider.
    API keys are automatically loaded from environment variables.
    Model names are loaded from YAML configuration file.

    Args:
        provider: The AI provider to use (google, openai, qwen, etc.)
        config_path: Path to the YAML configuration file. Defaults to _DEFAULT_CONFIG_PATH.

    Returns:
        Configured IntentionAgentConfig instance
    """
    try:
        logger.info(f"Loading agent configuration from: {config_path}")

        # Load the default config
        config = AgentConfig()
        yaml_config = load_agent_config_yaml(config_path or _DEFAULT_CONFIG_PATH)

        if yaml_config and "agent" in yaml_config:
            config.agent_settings.name = yaml_config["agent"].get(
                "name", config.agent_settings.name
            )
            config.agent_settings.version = yaml_config["agent"].get(
                "version", config.agent_settings.version
            )
            config.agent_settings.description = yaml_config["agent"].get(
                "description", config.agent_settings.description
            )

        if yaml_config and "models" in yaml_config:
            config.agent_settings.google_model = yaml_config["models"].get(
                "google", config.agent_settings.google_model
            )
            config.agent_settings.openai_model = yaml_config["models"].get(
                "openai", config.agent_settings.openai_model
            )
            config.agent_settings.qwen_model = yaml_config["models"].get(
                "qwen", config.agent_settings.qwen_model
            )
            config.agent_settings.anthropic_model = yaml_config["models"].get(
                "anthropic", config.agent_settings.anthropic_model
            )

        if not config.agent_settings.providers:
            config.agent_settings.providers = {p: ProviderConfig() for p in AIProvider}

        # Set up Google provider config
        google_config = config.agent_settings.providers[AIProvider.GOOGLE]
        google_config.api_key = config.GOOGLE_API_KEY
        google_config.model = config.agent_settings.google_model
        google_config.additional_params = {
            "project": config.GOOGLE_CLOUD_PROJECT,
            "location": config.GOOGLE_CLOUD_LOCATION,
            "use_vertexai": config.GOOGLE_GENAI_USE_VERTEXAI == "1",
        }
        google_config.enabled = bool(config.GOOGLE_API_KEY)

        # Set up OpenAI provider config
        openai_config = config.agent_settings.providers[AIProvider.OPENAI]
        openai_config.api_key = config.OPENAI_API_KEY
        openai_config.model = config.agent_settings.openai_model
        openai_config.additional_params = (
            {"org_id": config.OPENAI_ORG_ID} if config.OPENAI_ORG_ID else {}
        )
        openai_config.enabled = bool(config.OPENAI_API_KEY)

        # Set up Qwen provider config
        qwen_config = config.agent_settings.providers[AIProvider.QWEN]
        qwen_config.api_key = config.QWEN_API_KEY
        qwen_config.model = config.agent_settings.qwen_model
        qwen_config.endpoint = config.QWEN_API_ENDPOINT
        qwen_config.enabled = bool(config.QWEN_API_KEY)

        # Set up Anthropic provider config
        anthropic_config = config.agent_settings.providers[AIProvider.ANTHROPIC]
        anthropic_config.api_key = config.ANTHROPIC_API_KEY
        anthropic_config.model = config.agent_settings.anthropic_model
        anthropic_config.enabled = bool(config.ANTHROPIC_API_KEY)

        # Set provider if specified
        if provider:
            # Convert string to enum if needed
            if isinstance(provider, str):
                provider = AIProvider(provider.lower())

            # Set as default provider
            config.agent_settings.default_provider = provider

            # Check if the selected provider is configured properly
            provider_config = config.agent_settings.providers[provider]
            if not provider_config.api_key:
                logger.warning(
                    f"No API key found for {provider}. Check your environment variables."
                )
            else:
                logger.info(
                    f"Using {provider} as the AI provider with model {provider_config.model}"
                )
                provider_config.enabled = True

        # Validate default provider is enabled
        default_provider = config.agent_settings.default_provider
        if not config.agent_settings.providers[default_provider].enabled:
            # Find first enabled provider as fallback
            enabled_providers = [
                p for p in AIProvider if config.agent_settings.providers[p].enabled
            ]
            if enabled_providers:
                config.agent_settings.default_provider = enabled_providers[0]
                logger.warning(
                    f"Default provider {default_provider} not configured properly. Using {enabled_providers[0]} instead."
                )
            else:
                logger.warning(
                    "No properly configured AI providers found. Check your environment variables."
                )

        logger.info(
            f"Agent config loaded with {config.agent_settings.default_provider} as default provider"
        )
        return config

    except Exception as e:
        logger.error(f"Error loading agent config: {e}")
        raise e


def get_active_provider_config(
    config: AgentConfig,
) -> tuple[AIProvider, ProviderConfig]:
    """Get the active provider and its configuration"""
    provider = config.agent_settings.default_provider
    provider_config = config.agent_settings.providers[provider]
    return provider, provider_config
