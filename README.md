# Deep Learning Microservice

This project is a secure request processing system that simulates interactions between a client, a web host API, and a deep learning server. The system uses Flask, SQLAlchemy, RabbitMQ, and SQLite, and includes a React frontend for client interactions.

## Features

- Token-based authentication
- Request submission and result retrieval
- RabbitMQ for task queuing
- Deep learning server for task processing
- SQLite for storing request metadata and status
- Detailed logging with log retrieval endpoint
- Dockerized for easy deployment

## Prerequisites

Before you begin, ensure you have the following installed:

- Docker and Docker Compose
- Python 3.8+
- Node.js and npm

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/naderjafari/C4Ears.git
cd C4Ears
```

### 2. Set Up Environment Variables

Create a .env file in the project root directory with the following content:

```bash
SECRET_TOKEN=mysecret123456
DATABASE_URL=sqlite:///app.db
RABBITMQ_HOST=rabbitmq
WEB_HOST_URL=https://webhost:5000
LOAD_TEST_API_URL=https://localhost:5000/submit-request
```


### 3. Build and Start Services

Use Docker Compose to build and start the services:

```bash
docker-compose up --build -d
```

This command will build the Docker images and start the web host API, deep learning server, RabbitMQ, and React frontend.


### 4. View logs

You can access log files in data directory


### 5. Run Load Test

```bash
pip install -r .\webhost\requirements.txt 
python .\webhost\load_test.py
```


## Endpoints

### `/submit-request`

- **Method:** `POST`
- **Description:** Accepts a task submission from the client.
- **Body:** JSON containing the task (e.g., `{"task": "Sample task"}`).
- **Response:** JSON with the request ID.

### `/fetch-requests`

- **Method:** `GET`
- **Description:** Fetches the latest queued request for processing by the deep learning server.

### `/submit-result`

- **Method:** `POST`
- **Description:** Submits the processed result for a request.
- **Body:** JSON containing the `request_id` and `result`.

### `/get-result/<request_id>`

- **Method:** `GET`
- **Description:** Retrieves the result of a specific request.
- **Response:** JSON with the status and result of the request.

### `/logs`

- **Method:** `GET`
- **Description:** Retrieves the last 100 lines of logs.
