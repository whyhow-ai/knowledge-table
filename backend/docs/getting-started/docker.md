# Docker Deployment

This guide explains how to deploy Knowledge Table using Docker.

> ## Prerequisites
>
> - Docker & Docker Compose installed

## Steps

> **Step 1:** Clone the Repository

```sh
git clone https://github.com/yourusername/knowledge-table.git
cd knowledge-table
```

> **Step 2:** Set Up Environment

```sh
cp .env.sample .env
```

Open `.env`, add your OpenAI API key:

```
OPENAI_API_KEY=your_api_key_here
```

> **Step 3:** Build and Start Containers

```sh
docker-compose up -d --build
```

- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000`

> **Step 4:** Stop the Application

```sh
docker-compose down
```

## Troubleshooting

- Check container logs with:
  ```sh
  docker-compose logs
  ```
- Verify all required variables in `.env`.

## Updating

> **Step 1:** Pull the latest changes

```sh
git pull origin main
```

> **Step 2:** Rebuild and restart:

```sh
docker-compose up -d --build
```
