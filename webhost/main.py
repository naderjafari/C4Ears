import logging
import uuid
from functools import wraps

import pika
from flask import Flask, request, jsonify

from config import (
    SECRET_TOKEN,
    RABBITMQ_HOST,
    RABBITMQ_PORT,
    RABBITMQ_PASSWORD,
    RABBITMQ_USER,
    LOG_FILE,
)
from models import Request, init_db, SessionLocal
from schemas import TaskRequest, ResultRequest

app = Flask(__name__)
logger = logging.getLogger("webhost_api")


# Dependency for database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database error: {e}")
        raise
    finally:
        db.close()


# Authentication decorator
def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get("Authorization")
        if token != f"Bearer {SECRET_TOKEN}":
            logger.warning("Unauthorized access attempt")
            return jsonify({"error": "Unauthorized"}), 403
        return f(*args, **kwargs)

    return decorated_function


@app.route("/submit-request", methods=["POST"])
@token_required
def submit_request():
    data = request.json
    try:
        task_data = TaskRequest(**data)
    except Exception as e:
        logger.error(f"Validation error: {e}")
        return jsonify({"error": str(e)}), 400

    request_id = str(uuid.uuid4())

    try:
        db = next(get_db())
        new_request = Request(id=request_id, task=task_data.task, status="processing")
        db.add(new_request)
        db.commit()

        # Enqueue the task for processing
        connection, channel = get_rabbitmq_channel()
        channel.basic_publish(
            exchange="",
            routing_key="task_queue",
            body=request_id + ":" + task_data.task,
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            ),
        )
        connection.close()
    except Exception as e:
        logger.error(f"Failed to submit request: {e}")
        return jsonify({"error": "Failed to submit request"}), 500

    logger.info(f"Request {request_id} submitted successfully")
    return jsonify({"request_id": request_id}), 200


@app.route("/submit-result", methods=["POST"])
@token_required
def submit_result():
    data = request.json
    try:
        result_data = ResultRequest(**data)
    except Exception as e:
        logger.error(f"Validation error: {e}")
        return jsonify({"error": str(e)}), 400

    try:
        db = next(get_db())
        db_request = (
            db.query(Request).filter(Request.id == result_data.request_id).first()
        )
        if not db_request:
            logger.error(f"Invalid request_id: {result_data.request_id}")
            return jsonify({"error": "Invalid request_id"}), 400

        db_request.status = "completed"
        db_request.result = result_data.result
        db.commit()
    except Exception as e:
        logger.error(f"Failed to submit result: {e}")
        return jsonify({"error": "Failed to submit result"}), 500

    logger.info(f"Result for request {result_data.request_id} submitted successfully")
    return jsonify({"message": "Result submitted"}), 200


@app.route("/get-result/<request_id>", methods=["GET"])
@token_required
def get_result(request_id):
    try:
        db = next(get_db())
        db_request = db.query(Request).filter(Request.id == request_id).first()

        if not db_request:
            logger.error(f"Invalid request_id: {request_id}")
            return jsonify({"error": "Invalid request_id"}), 400
    except Exception as e:
        logger.error(f"Failed to fetch result: {e}")
        return jsonify({"error": "Failed to fetch result"}), 500

    return jsonify({"status": db_request.status, "result": db_request.result}), 200


@app.route("/logs", methods=["GET"])
@token_required
def get_logs():
    try:
        with open(LOG_FILE, "r") as f:
            logs = f.readlines()
        return jsonify({"logs": logs[-100:]}), 200  # Return the last 100 log lines
    except Exception as e:
        logger.error(f"Failed to retrieve logs: {e}")
        return jsonify({"error": "Failed to retrieve logs"}), 500


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy"}), 200


def get_rabbitmq_channel():
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=RABBITMQ_HOST,
                port=RABBITMQ_PORT,
                virtual_host="/",
                credentials=pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD),
            )
        )
        channel = connection.channel()
        channel.queue_declare(queue="task_queue", durable=True)
        return connection, channel
    except Exception as e:
        logger.error(f"Failed to connect to RabbitMQ: {e}")
        raise


if __name__ == "__main__":
    init_db()
    app.run(port=5000, host="0.0.0.0", ssl_context=("cert.pem", "key.pem"))
