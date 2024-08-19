import aiohttp
import asyncio
import time

AUTH_TOKEN = "nader1234"
NUM_REQUESTS = 1000  # Number of concurrent requests
CONCURRENT_REQUESTS = 50  # Number of requests to send concurrently
API_URL = "https://localhost:5000/submit-request"
TASK_DATA = {"task": "Classify this image"}


async def send_request(session, url, headers, data):
    async with session.post(url, json=data, headers=headers, ssl=False) as response:
        return await response.json()


async def load_test():
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {AUTH_TOKEN}",
    }

    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(NUM_REQUESTS):
            task = send_request(session, API_URL, headers, TASK_DATA)
            tasks.append(task)

            if len(tasks) >= CONCURRENT_REQUESTS:
                responses = await asyncio.gather(*tasks)
                for response in responses:
                    if response.get("request_id"):
                        print(f"Request ID: {response['request_id']}")
                    else:
                        print(f"Failed to submit request: {response}")
                tasks = []

        # Ensure remaining tasks are also completed
        if tasks:
            responses = await asyncio.gather(*tasks)
            for response in responses:
                if response.get("request_id"):
                    print(f"Request ID: {response['request_id']}")
                else:
                    print(f"Failed to submit request: {response}")


if __name__ == "__main__":
    start_time = time.time()
    asyncio.run(load_test())
    end_time = time.time()
    print(f"Completed {NUM_REQUESTS} requests in {end_time - start_time} seconds.")
