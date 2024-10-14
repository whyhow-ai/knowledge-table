# Native Deployment

This guide explains how to deploy Knowledge Table natively on your system.

## Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.10+
- Bun (for frontend)

## Deployment Steps

### Backend Deployment

1. **Clone the Repository**

   ```sh
   git clone https://github.com/yourusername/knowledge-table.git
   cd knowledge-table/backend
   ```

2. **Set Up a Virtual Environment**

   ```sh
   python3 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies**

   ```sh
   pip install .
   ```

4. **Environment Setup**

   Copy the sample environment file and edit it with your settings:

   ```sh
   cp .env.sample .env
   ```

   Open `.env` in a text editor and add your OpenAI API key:

   ```
   OPENAI_API_KEY=your_api_key_here
   ```

5. **Start the Backend Server**

   ```sh
   cd src
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

   The backend will be available at `http://localhost:8000`.

### Frontend Deployment

1. **Navigate to the Frontend Directory**

   ```sh
   cd ../../frontend
   ```

2. **Install Bun** (if not already installed)

   ```sh
   curl https://bun.sh/install | bash
   ```

3. **Install Dependencies**

   ```sh
   bun install
   ```

4. **Build the Frontend**

   ```sh
   bun run build