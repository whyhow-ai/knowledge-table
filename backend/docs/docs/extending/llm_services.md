# Extending LLM Services

This guide explains how to add support for new Language Model (LLM) services.

## Steps to Add a New LLM Service

1. **Create a new LLM service class**

   In `src/app/services/llm/`, create a new file `your_llm_service.py`.

   ```python
   # your_llm_service.py
   from .base import BaseLLMService

   class YourLLMService(BaseLLMService):
       def __init__(self):
           super().__init__()
           # Initialize your LLM client here

       async def generate_response(self, prompt: str) -> str:
           """
           Generate a response using Your LLM.

           Args:
               prompt (str): The prompt to send to the LLM.

           Returns:
               str: The generated response.
           """
           # Implement your LLM interaction logic here
           response = ...  # Replace with actual implementation
           return response
   ```

2. **Update the LLM Factory**

   In `src/app/services/llm/factory.py`, import your new service and update the factory method.

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

3. **Configure the Service**

   In `src/app/core/config.py`, add a configuration option for your LLM.

   ```python
   # config.py
   from pydantic import BaseSettings

   class Settings(BaseSettings):
       LLM_SERVICE: str = "openai"  # Default to OpenAI

   settings = Settings()
   ```

   Update your environment variable or `.env` file accordingly:

   ```
   LLM_SERVICE=your_llm
   ```

4. **Use the New Service**

   The application will now use your LLM service based on the configuration.

## Additional Considerations

- **Authentication**: Ensure you handle any API keys or authentication required by your LLM service.
- **Error Handling**: Implement proper error handling in your service.
- **Testing**: Write unit tests for your new service.
