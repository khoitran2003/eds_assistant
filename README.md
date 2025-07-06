# EDS Assistant - AI Chatbot

This project is an AI-powered chatbot for Eye Design Salon, built using FastAPI, SQLModel, and Google ADK. It leverages Docker for easy setup and deployment.

## Prerequisites

- [Docker](https://www.docker.com/get-started) and Docker Compose
- Python 3.11+
- `git`

## Getting Started

Follow these steps to get the project running on your local machine.

### 1. Clone the Repository

```bash
git clone https://github.com/khoitran2003/eds_assistant.git
cd eds_assistant
```

### 2. Download the MCP Toolbox

The project requires the `toolbox` executable from the MCP Toolbox for Databases project.

1.  Go to the [latest release page](https://github.com/googleapis/genai-toolbox/releases/latest).
2.  Download the appropriate binary for your operating system (e.g., `toolbox-linux-amd64` for Linux).
3.  Rename the downloaded file to `toolbox` (or `toolbox.exe` on Windows).
4.  Place the `toolbox` executable in the root directory of this project.

**Note:** The `toolbox` file is intentionally ignored by Git (via `.gitignore`) and should not be committed to the repository.

### 3. Configure Environment Variables

Create a `.env` file in the root directory of the project by copying the example below. This file contains necessary credentials for the database and other services.

```env
# Database Configuration
DB_HOST= <<host>>
DB_USER= <<user>>
DB_PASSWORD= <<password>>
DB_PORT= <<port>>
BOOKING_CHATBOT_DB=booking_chatbot_db

# Google API Key (if needed for ADK)
GOOGLE_API_KEY=your_google_api_key_here
```

### 4. Build and Run with Docker

With Docker running, use Docker Compose to build the images and start the services:

```bash
docker compose up --build
```

The application will be available at `http://localhost:8000`. This will also start the ADK Dev UI.

### 5. Accessing Services

- **Application / ADK Dev UI**: `http://localhost:8000`
- **Database (MySQL)**: Connect using a client like DBeaver or TablePlus on `localhost` at port `3307`.

## Development

### Running the application

To start the application:

```bash
docker compose up
```

To run in detached mode:

```bash
docker compose up -d
```

To stop the application:

```bash
docker compose down
```

### Updating code

- If you only change Python code (`.py` files), the changes will be reflected automatically thanks to the volume mount. Simply restart the `app` service: `docker compose restart app`.
- If you change dependencies (`requirements.txt`) or the `Dockerfile`, you need to rebuild the image: `docker compose up --build`.
- If you change the `docker-compose.yml` file, you need to bring the services down and up again to apply changes: `docker compose up -d`.
