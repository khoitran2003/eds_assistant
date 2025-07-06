"""
Improved callback functions following ADK best practices.
These callbacks implement guardrails, state management, logging, and customer data loading.
"""

from typing import Optional, Dict, Any
from google.genai import types
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools.tool_context import ToolContext

from ..db.crud.customer import get as get_customer
from ..db.base import get_db_session
from ..utils.log_setup import setup_logger

logger = setup_logger(__name__)


class CustomerDataManager:
    """Manages customer data loading and state management"""

    @staticmethod
    def load_customer_info(
        callback_context: CallbackContext,
    ) -> Optional[types.Content]:
        """
        Load customer information into state based on user_id or session context.
        This callback should be used in before_agent_callback.
        """
        try:
            # Check if customer info already loaded
            if "customer_info" in callback_context.state:
                logger.info("Customer info already loaded in state")
                return None

            customer_id = callback_context.state.get("customer_id")

            if not customer_id:
                customer_id = "b0d40da8-054c-4be2-9e87-260de142e86e"
                with next(get_db_session()) as db_session:
                    customer = get_customer(session=db_session, id=customer_id)

                    if customer:
                        customer_info = {
                            "id": customer.id,
                            "name": f"{customer.first_name} {customer.last_name}",
                            "first_name": customer.first_name,
                            "last_name": customer.last_name,
                            "email": customer.email,
                            "phone": customer.phone_number,
                            "gender": (
                                customer.gender.value if customer.gender else None
                            ),
                            "status": (
                                customer.status.value if customer.status else None
                            ),
                        }

                        # Store in state
                        callback_context.state["customer_info"] = customer_info

                        logger.info(f"Loaded customer info for: {customer.email}")

                        # Set context flags for other callbacks
                        callback_context.state["_customer_loaded"] = True
                        print(customer_info)
                    else:
                        logger.warning(f"Customer not found: {customer_id}")
                        callback_context.state["_customer_loaded"] = False
            else:
                # No customer ID available - this might be a new conversation
                logger.info("No customer ID found - treating as anonymous user")
                callback_context.state["_customer_loaded"] = False

        except Exception as e:
            logger.error(f"Error loading customer info: {e}")
            callback_context.state["_customer_load_error"] = str(e)

        return None


class GuardrailManager:
    """Implements safety guardrails and content filtering"""

    FORBIDDEN_KEYWORDS = [
        "medical advice",
        "diagnosis",
        "prescription",
        "treatment",
        "medicine",
        "drug",
        "medication",
        "illness",
        "disease",
    ]

    @staticmethod
    def content_guardrails(
        callback_context: CallbackContext,
    ) -> Optional[types.Content]:
        """
        Check content for safety violations before sending to LLM.
        Returns a response if content should be blocked.
        """
        try:
            # Get the latest user message from state
            content_text = callback_context.state.get("_last_user_message", "").lower()

            if content_text:
                # Check for medical advice requests
                for keyword in GuardrailManager.FORBIDDEN_KEYWORDS:
                    if keyword in content_text:
                        logger.warning(f"Blocked content with keyword: {keyword}")

                        # Log violation in state
                        violations = callback_context.state.get(
                            "_content_violations", []
                        )
                        violations.append(
                            {
                                "keyword": keyword,
                                "timestamp": "now",  # You could use datetime here
                                "action": "blocked",
                            }
                        )
                        callback_context.state["_content_violations"] = violations

                        # Return blocking response
                        return types.Content(
                            parts=[
                                types.Part(
                                    text="I'm a beauty service assistant and cannot provide medical advice. "
                                    "For health-related concerns, please consult with a qualified medical professional. "
                                    "I'd be happy to help with beauty services, appointments, or salon information instead!"
                                )
                            ]
                        )

        except Exception as e:
            logger.error(f"Error in content guardrails: {e}")

        return None


class LoggingManager:
    """Provides comprehensive logging for agent interactions"""

    @staticmethod
    def log_agent_start(callback_context: CallbackContext) -> Optional[types.Content]:
        """Log when agent starts processing"""
        try:
            agent_name = getattr(callback_context, "agent_name", "Unknown")
            customer_info = callback_context.state.get("customer_info", {})
            customer_name = customer_info.get("name", "Anonymous")

            logger.info(f"Agent '{agent_name}' started for customer: {customer_name}")

            # Track conversation metrics
            metrics = callback_context.state.get("_conversation_metrics", {})
            metrics["agent_calls"] = metrics.get("agent_calls", 0) + 1
            metrics["current_agent"] = agent_name
            callback_context.state["_conversation_metrics"] = metrics

        except Exception as e:
            logger.error(f"Error in agent start logging: {e}")

        return None

    @staticmethod
    def log_tool_usage(tool_context: ToolContext) -> Optional[Dict[str, Any]]:
        """Log tool usage for monitoring"""
        try:
            tool_name = getattr(tool_context, "tool_name", "Unknown")
            customer_info = tool_context.state.get("customer_info", {})
            customer_name = customer_info.get("name", "Anonymous")

            logger.info(f"Tool '{tool_name}' called by customer: {customer_name}")

            # Track tool usage
            tool_usage = tool_context.state.get("_tool_usage", {})
            tool_usage[tool_name] = tool_usage.get(tool_name, 0) + 1
            tool_context.state["_tool_usage"] = tool_usage

        except Exception as e:
            logger.error(f"Error in tool usage logging: {e}")

        return None


class StateManager:
    """Manages state consistency and cleanup"""

    @staticmethod
    def cleanup_temp_state(
        callback_context: CallbackContext,
    ) -> Optional[types.Content]:
        """Clean up temporary state variables after agent completion"""
        try:
            # Use state.to_dict() to safely access all keys
            current_state = callback_context.state.to_dict()
            temp_keys = [
                key for key in current_state.keys() if key.startswith("_temp_")
            ]

            # Clean up temporary keys by setting them to None
            for key in temp_keys:
                callback_context.state[key] = None

            if temp_keys:
                logger.info(f"Cleaned up {len(temp_keys)} temporary state variables")

        except Exception as e:
            logger.error(f"Error in state cleanup: {e}")

        return None


# Pre-configured callback combinations for different use cases
def create_customer_service_callbacks():
    """Create callback set optimized for customer service agents"""
    return {
        "before_agent_callback": CustomerDataManager.load_customer_info,
        "before_model_callback": GuardrailManager.content_guardrails,
        "after_agent_callback": StateManager.cleanup_temp_state,
    }


def create_information_agent_callbacks():
    """Create callback set for information-focused agents"""
    return {
        "before_agent_callback": LoggingManager.log_agent_start,
        "before_tool_callback": LoggingManager.log_tool_usage,
    }


def create_booking_agent_callbacks():
    """Create callback set for booking agents with enhanced logging"""
    return {
        "before_agent_callback": CustomerDataManager.load_customer_info,
        "before_model_callback": GuardrailManager.content_guardrails,
        "before_tool_callback": LoggingManager.log_tool_usage,
        "after_agent_callback": StateManager.cleanup_temp_state,
    }


if __name__ == "__main__":
    callbacks = create_customer_service_callbacks()
    print(callbacks)