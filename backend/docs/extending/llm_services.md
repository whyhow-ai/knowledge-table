# Extending LLM Services

This guide explains how to add support for new Language Model (LLM) services to the Knowledge Table backend.

---

## Steps

### **1. Create a New LLM Service Class**

In `src/app/services/llm/`, create a new file, e.g., `your_llm_service.py`.

```python
# your_llm_service.py
from .base import BaseLLMService

class YourLLMService(BaseLLMService):
    def __init__(self):
        super().__init__()
        # Initialize your LLM client here

    async def generate_response(self, prompt: str) -> str:
        # Implement LLM interaction logic here
        response = ...  # Replace with actual implementation
        return response
```

### **2. Update the LLM Factory**

In `src/app/services/llm/factory.py`, import your service and update the factory method.

```python
# factory.py
from .your_llm_service import YourLLMService

class LLMFactory:
    @staticmethod
    def get_llm_service(service_name: str):
        if service_name == "openai":
            return OpenAIService()
        elif service_name == "your_llm":
            return YourLLMService()
        else:
            raise ValueError(f"Unknown LLM service: {service_name}")
```

### **3. Configure the Service**

In `src/app/core/config.py`, add configuration options for the new LLM.

```python
# config.py
from pydantic import BaseSettings

class Settings(BaseSettings):
    LLM_SERVICE: str = "openai"

settings = Settings()
```

Update your environment or `.env` file:

```
LLM_SERVICE=your_llm
```

---

## Considerations

- **Authentication**: Handle any API keys or authentication required by the service.
- **Error Handling**: Ensure robust error handling in your service.
- **Testing**: Write unit tests for your new service.

## Example

Here's an example of how you might implement `generate_response` in `YourLLMService`:

```python
async def generate_response(self, prompt: str) -> str:
    # Call your LLM API client with the prompt
    try:
        response = await self.your_llm_client.generate(
            prompt,
            api_key=self.api_key,
            max_tokens=50
        )
        return response["text"]
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        return "Error in LLM generation"
```
