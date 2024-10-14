# Configuration

The Knowledge Table backend uses environment variables for configuration.

## Setting Up Environment Variables

1. **Create a `.env` file**

   Copy the sample file:

   ```bash
   cp .env.sample .env
   ```

2. **Set your OpenAI API key**

   Edit the `.env` file and add your OpenAI API key:

   ```dotenv
   OPENAI_API_KEY=sk-yourkeyhere
   ```

3. **Configure other settings**

   - `UNSTRUCTURED_API_KEY` (optional): If using the Unstructured API.

## Environment Variables Reference

| Variable                | Description                                    |
|-------------------------|------------------------------------------------|
| `OPENAI_API_KEY`        | Your OpenAI API key.                           |
| `UNSTRUCTURED_API_KEY`  | API key for Unstructured.io (optional).        |

[Back to Installation](installation.md)