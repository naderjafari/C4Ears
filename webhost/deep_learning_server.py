import logging

import pika
import requests

from config import (
    SECRET_TOKEN,
    RABBITMQ_HOST,
    RABBITMQ_PORT,
    RABBITMQ_PASSWORD,
    RABBITMQ_USER,
    WEB_HOST_URL,
)

logger = logging.getLogger("deep_learning_server")


def get_rabbitmq_channel():
    # try:
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
    # except Exception as e:
    #     logger.error(f"Failed to connect to RabbitMQ: {e}")
    #     raise


def process_task(task):
    try:
        # Simulate deep learning processing
        result = f"Processed: {task}"
        return result
    except Exception as e:
        logger.error(f"Task processing failed: {e}")
        return "Error processing task"


def callback(ch, method, properties, body):
    message = body.decode()
    request_id, task = message.split(":", 1)

    logger.info(f"Processing task for request {request_id}")

    # Process the task
    result = process_task(task)

    try:
        # Submit result back to the webhost API
        response = requests.post(
            f"{WEB_HOST_URL}/submit-result",
            json={"request_id": request_id, "result": result},
            headers={"Authorization": f"Bearer {SECRET_TOKEN}"},
            verify=False,  # Disable SSL verification for simplicity in this example
        )
        logger.info(
            f"Result submitted for request {request_id}: {response.status_code}"
        )
    except Exception as e:
        logger.error(f"Failed to submit result for request {request_id}: {e}")

    ch.basic_ack(delivery_tag=method.delivery_tag)


if __name__ == "__main__":
    connection, channel = get_rabbitmq_channel()
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue="task_queue", on_message_callback=callback)
    logger.info("Deep learning server is waiting for tasks")
    channel.start_consuming()
