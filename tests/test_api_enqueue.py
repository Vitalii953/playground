import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app


class DummyChannel:
    def __init__(self):
        self.published = []

    class Exchange:
        def __init__(self, parent):
            self.parent = parent

        async def publish(self, message, routing_key=None):
            # record the message body and routing key for assertions
            self.parent.published.append((message.body, routing_key))

    @property
    def default_exchange(self):
        return DummyChannel.Exchange(self)


@pytest.fixture(autouse=True)
def override_mq():
    dummy = DummyChannel()
    app.state.mq_channel = dummy
    return dummy


def test_post_item(override_mq):
    client = TestClient(app)
    payload = {"name": "test", "value": 123}

    response = client.post("/items", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "queued"

    published = override_mq.published
    assert len(published) == 1
    body, routing_key = published[0]
    assert routing_key == settings.task_queue
    assert b"test" in body
