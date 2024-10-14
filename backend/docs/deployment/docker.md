# Docker Deployment

This guide explains how to deploy Knowledge Table using Docker.

## Prerequisites

Before you begin, ensure you have the following installed on your system:

- Docker
- Docker Compose

## Deployment Steps

1. **Clone the Repository**

   ```sh
   git clone https://github.com/yourusername/knowledge-table.git
   cd knowledge-table
   ```

2. **Environment Setup**

   Copy the sample environment file and edit it with your settings:

   ```sh
   cp .env.sample .env
   ```

   Open `.env` in a text editor and add your OpenAI API key:

   ```
   OPENAI_API_KEY=your_api_key_here
   ```

3. **Build and Start the Containers**

   Use Docker Compose to build and start the containers:

   ```sh
   docker-compose up -d --build
   ```

   This command builds the images (if they don't exist) and starts the containers in detached mode.

4. **Accessing the Application**

   Once the containers are up and running, you can access:
   - The frontend at `http://localhost:3000`
   - The backend at `http://localhost:8000`

5. **Stopping the Application**

   To stop the containers, run:

   ```sh
   docker-compose down
   ```

## Troubleshooting

- If you encounter any issues, check the logs of the containers:

  ```sh
  docker-compose logs
  ```

- Ensure all required environment variables are set in your `.env` file.

## Updating

To update to the latest version:

1. Pull the latest changes from the repository:

   ```sh
   git pull origin main
   ```

2. Rebuild and restart the containers:

   ```sh
   docker-compose up -d --build
   ```

This will ensure you're running the latest version of Knowledge Table.