import logging
import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configurations from environment variables
SECRET_TOKEN = os.getenv("SECRET_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = os.getenv("RABBITMQ_PORT", "5672")
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "guest")
WEB_HOST_URL = os.getenv("WEB_HOST_URL", "http://localhost:5000")


# Logging configuration
LOG_FILE = os.getenv("LOG_FILE", "system.log")

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
