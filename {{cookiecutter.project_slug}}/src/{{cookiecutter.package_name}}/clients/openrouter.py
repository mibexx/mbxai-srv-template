import logging
import asyncio
import json
from typing import (
    Any,
    Optional,
)

from openai import (
    AsyncOpenAI,
    OpenAIError,
)
from openai._types import NOT_GIVEN

from ..config import get_openrouter_api_config
from .models import OpenRouterModel


logger = logging.getLogger(__name__)


class OpenRouterApiClient:
    def __init__(
        self,
        model: OpenRouterModel = OpenRouterModel.GPT_41,
        max_retries: int = 3,
        retry_delay: int = 2,
    ) -> None:
        """
        Initializes the OpenRouterApiClient with the specified model.

        Args:
            model (OpenRouterModel): The model to use for API calls, defaults to GPT_41.
            max_retries (int): Maximum number of retry attempts for failed API calls, defaults to 3.
            retry_delay (int): Base delay between retries in seconds, defaults to 2.
        """
        openrouter_config = get_openrouter_api_config()

        logger.info(f"Initializing OpenRouter client with base URL: {openrouter_config.base_url}")
        self._client = AsyncOpenAI(
            base_url=openrouter_config.base_url,
            api_key=openrouter_config.api_key,
            timeout=90.0,
        )
        self.default_model = model
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    async def _execute_with_retry(
        self, operation_name: str, operation_func, *args, **kwargs
    ):
        """
        Execute an operation with retry logic.

        Args:
            operation_name: Name of the operation for logging
            operation_func: Async function to execute
            *args, **kwargs: Arguments to pass to the function

        Returns:
            The result of the operation or None if all retries failed
        """
        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(
                    f"Executing {operation_name} (attempt {attempt}/{self.max_retries})"
                )

                # Use asyncio.wait_for to implement timeout
                result = await asyncio.wait_for(
                    operation_func(*args, **kwargs), timeout=90.0
                )

                return result

            except asyncio.TimeoutError:
                logger.warning(
                    f"{operation_name} timed out after 30 seconds (attempt {attempt}/{self.max_retries})"
                )
                if attempt == self.max_retries:
                    logger.error(
                        f"All {self.max_retries} attempts for {operation_name} timed out"
                    )
                    return None

            except json.JSONDecodeError as e:
                logger.warning(
                    f"JSON parsing error in {operation_name}: {e} (attempt {attempt}/{self.max_retries})"
                )
                if attempt == self.max_retries:
                    logger.error(
                        f"All {self.max_retries} attempts for {operation_name} failed with JSON parsing errors"
                    )
                    return None

            except OpenAIError as e:
                logger.warning(
                    f"OpenAI API Error in {operation_name}: {e} (attempt {attempt}/{self.max_retries})"
                )
                if attempt == self.max_retries:
                    logger.error(
                        f"All {self.max_retries} attempts for {operation_name} failed with OpenAI API errors"
                    )
                    return None

            except Exception as e:
                logger.warning(
                    f"Unexpected error in {operation_name}: {e} (attempt {attempt}/{self.max_retries})"
                )
                if attempt == self.max_retries:
                    logger.error(
                        f"All {self.max_retries} attempts for {operation_name} failed with unexpected errors"
                    )
                    return None

            # Wait before retrying
            await asyncio.sleep(self.retry_delay * attempt)  # Exponential backoff
            logger.info(f"Retrying {operation_name}...")

    async def _execute_chat_parse(
        self, model_value, messages, structured_output, extra_headers
    ):
        """Private method to execute chat parse API call."""
        completion = await self._client.beta.chat.completions.parse(
            model=model_value,
            messages=messages,
            response_format=structured_output,
            extra_headers=extra_headers,
        )
        return completion.choices[0].message.parsed

    async def _execute_chat_completion(
        self, model_value, messages, extra_headers, response_format
    ):
        """Private method to execute chat completion API call."""
        response = await self._client.chat.completions.create(
            extra_headers=extra_headers,
            model=model_value,
            messages=messages,
            response_format=response_format,
        )
        if not response.choices:
            raise Exception(response.error or "No choices returned")
        return response.choices[0].message.content

    async def chat_parse(
        self,
        messages: list[dict[str, str]],
        structured_output: object,
        model: Optional[OpenRouterModel] = None,
        extra_headers: Optional[dict[str, str]] = None,
    ) -> object | None:
        """
        Sends a chat completion request to the API and returns the structured response content.

        Args:
            messages (list[dict[str, str]]): A list of messages to send to the chat.
            structured_output (object): The schema defining the structure of the response.
            model (Optional[OpenRouterModel]): The model to use for this request, defaults to the instance's default model.
            extra_headers (Optional[dict[str, str]]): Additional headers to include in the API request.

        Returns:
            object | None: The parsed structured response from the API, or None if an error occurs.
        """
        model = model or self.default_model
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            **(extra_headers or {}),
        }

        return await self._execute_with_retry(
            "chat_parse",
            self._execute_chat_parse,
            model.value,
            messages,
            structured_output,
            headers,
        )

    async def chat_completion(
        self,
        messages: list[dict[str, str]],
        model: Optional[OpenRouterModel] = None,
        extra_headers: Optional[dict[str, str]] = None,
        structured_output: Optional[dict[str, Any]] = None,
    ) -> str:
        """
        Sends a chat completion request to the API and returns the response content.

        Args:
            messages (list[dict[str, str]]): A list of messages to send to the chat.
            model (Optional[OpenRouterModel]): The model to use for this request, defaults to the instance's default
            model.
            extra_headers (Optional[dict[str, str]]): Additional headers to include in the API request, defaults to
            an empty dict.
            structured_output (Optional[dict[str, Any]]): Specifies the desired structure of the response,
            defaults to NOT_GIVEN.

        Returns:
            str: The content of the response message from the chat API.
        """
        model = model or self.default_model
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            **(extra_headers or {}),
        }
        response_format = structured_output or NOT_GIVEN

        result = await self._execute_with_retry(
            "chat_completion",
            self._execute_chat_completion,
            model.value,
            messages,
            headers,
            response_format,
        )
        return result or "" 