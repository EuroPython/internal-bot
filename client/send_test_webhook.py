import os
from pprint import pprint as pp

import httpx

INTERNAL_WEBHOOK_TOKEN = os.environ["INTERNAL_WEBHOOK_TOKEN"]


def send_test_webhook():
    url = "http://localhost:4672/webhook/internal/"
    response = httpx.post(
        url,
        json={"event": "test webhook"},
        headers={"Authorization": INTERNAL_WEBHOOK_TOKEN},
    )

    print(response)
    print(response.content)
    # pp(response.json())


if __name__ == "__main__":
    send_test_webhook()
