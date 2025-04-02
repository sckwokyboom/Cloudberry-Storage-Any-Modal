from pathlib import Path
from unittest.mock import Mock

import grpc
import numpy as np
import pytest

import src.generated.proto.cloudberry_storage_pb2 as pb2
import src.generated.proto.cloudberry_storage_pb2_grpc as pb2_grpc
from src.cloudberry_storage import CloudberryStorage
from src.model_registry import ModelRegistry

TEST_BUCKET_UUID_0 = "550e8400-e29b-41d4-a716-446655440000"
TEST_BUCKET_UUID_1 = "550e8400-e29b-41d4-a716-446655440001"

FAKE_TICKET_UUID_0 = "550e8400-e29b-41d4-a716-fake-ticket-00"
FAKE_TICKET_UUID_1 = "550e8400-e29b-41d4-a716-fake-ticket-01"
FAKE_TICKET_UUID_2 = "550e8400-e29b-41d4-a716-fake-ticket-02"
FAKE_TICKET_UUID_3 = "550e8400-e29b-41d4-a716-fake-ticket-03"
FAKE_TICKET_UUID_4 = "550e8400-e29b-41d4-a716-fake-ticket-04"
EXAMPLE_IMAGE_PATH = "C:\\Users\\sckwo\\PycharmProjects\\cloudberry-storage\\ru\\nai\\cloudberry_storage\\test.png"


def get_stub(channel: grpc.Channel) -> pb2_grpc.CloudberryStorageStub:
    return pb2_grpc.CloudberryStorageStub(channel)


def test_init_bucket(stub: pb2_grpc.CloudberryStorageStub):
    context = Mock()
    request = pb2.InitBucketRequest(bucket_uuid=TEST_BUCKET_UUID_0)
    response = stub.InitBucket(request)
    print("[✓] InitBucket", response)


def test_put_entry_with_real_image(stub: pb2_grpc.CloudberryStorageStub, image_path: str):
    image_data = Path(image_path).read_bytes()

    ticket = pb2.TicketEntry(
        title=pb2.TextEntry(content="Test title"),
        description=pb2.TextEntry(content="Test description"),
        attachments=[
            pb2.ImageEntry(content=image_data, content_type=pb2.PNG),
            pb2.ImageEntry(content=image_data, content_type=pb2.PNG),
        ],
    )

    request = pb2.PutEntryRequest(
        external_ticket_id=FAKE_TICKET_UUID_0,
        bucket_uuid=TEST_BUCKET_UUID_0,
        ticket=ticket,
    )

    response = stub.PutEntry(request)
    print("[✓] PutEntry", response)


def test_find(stub: pb2_grpc.CloudberryStorageStub):
    request = pb2.FindRequest(
        query=pb2.TextEntry(content="test search query"),
        images=[],  # можно добавить pb2.ImageEntry, как выше
        bucket_uuid=TEST_BUCKET_UUID_0,
        top_k=5
    )
    response = stub.Find(request)
    print("[✓] Find Response")
    for entry in response.entries:
        print(" ->", entry.external_id)


def test_remove_entry(stub: pb2_grpc.CloudberryStorageStub):
    request = pb2.RemoveEntryRequest(
        bucket_uuid=TEST_BUCKET_UUID_0,
        external_ticket_id=FAKE_TICKET_UUID_1,
    )
    response = stub.RemoveEntry(request)
    print("[✓] RemoveEntry", response)


def test_destroy_bucket(stub: pb2_grpc.CloudberryStorageStub):
    request = pb2.DestroyBucketRequest(bucket_uuid=TEST_BUCKET_UUID_0)
    response = stub.DestroyBucket(request)
    print("[✓] DestroyBucket", response)


@pytest.fixture
def mocked_service():
    text_embedder = Mock()
    text_embedder.encode.return_value = np.ones(384)

    image_embedder = Mock()
    image_embedder.encode_image.return_value = np.ones(1536)
    image_embedder.encode_text.return_value = np.ones(1536)

    qdrant_client = Mock()
    qdrant_client.get_collection.side_effect = Exception("Not found")
    qdrant_client.create_collection.return_value = None
    qdrant_client.upsert.return_value = None
    qdrant_client.query_points.return_value = Mock(points=[])
    qdrant_client.delete_collection.return_value = None
    qdrant_client.delete.return_value = None

    registry = ModelRegistry(
        text_embedder=text_embedder,
        one_peace_embedder=image_embedder,
        qdrant_client=qdrant_client,
    )
    return CloudberryStorage(registry)


if __name__ == "__main__":
    with grpc.insecure_channel("localhost:50051") as channel:
        stub = get_stub(channel)

        # test_init_bucket(stub)
        # test_put_entry_with_real_image(stub, EXAMPLE_IMAGE_PATH)
        # test_find(stub)
        # test_remove_entry(stub)
        # test_destroy_bucket(stub)
