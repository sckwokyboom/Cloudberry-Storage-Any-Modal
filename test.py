import grpc

import cloudberry_storage_pb2 as pb2
import cloudberry_storage_pb2_grpc as pb2_grpc

TEST_BUCKET_UUID_0 = "550e8400-e29b-41d4-a716-446655440000"
TEST_BUCKET_UUID_1 = "550e8400-e29b-41d4-a716-446655440001"

FAKE_TICKET_UUID_0 = "550e8400-e29b-41d4-a716-fake-ticket-00"
FAKE_TICKET_UUID_1 = "550e8400-e29b-41d4-a716-fake-ticket-01"
FAKE_TICKET_UUID_2 = "550e8400-e29b-41d4-a716-fake-ticket-02"
FAKE_TICKET_UUID_3 = "550e8400-e29b-41d4-a716-fake-ticket-03"
FAKE_TICKET_UUID_4 = "550e8400-e29b-41d4-a716-fake-ticket-04"



def test_init_bucket(channel: grpc.Channel):
    stub: pb2_grpc.CloudberryStorageStub = pb2_grpc.CloudberryStorageStub(channel)
    request: pb2.InitBucketRequest = pb2.InitBucketRequest(p_bucket_uuid=TEST_BUCKET_UUID_1)
    response = stub.InitBucket(request)
    print("InitBucket Response:", response)


def test_put_entry(channel: grpc.Channel, bucket_id: str, ticket_id: str):
    stub: pb2_grpc.CloudberryStorageStub = pb2_grpc.CloudberryStorageStub(channel)
    fake_ticket: pb2.TicketEntry = pb2.TicketEntry(
        title=pb2.TextEntry(content="Some ticket blablabla"),
        description=pb2.TextEntry(content="Some description hard porn"),
        attachments=[
            pb2.ImageEntry(content="porno_bytes".encode("utf-8"), content_type=pb2.JPEG),
            pb2.ImageEntry(content="small_vanilla_bytes".encode("utf-8"), content_type=pb2.PNG)]
    )
    request: pb2.PutEntryRequest = pb2.PutEntryRequest(
        external_ticket_id=ticket_id,
        bucket_uuid=bucket_id,
        ticket=fake_ticket,
    )
    response = stub.PutEntry(request)
    print("PutEntry Response:", response)


def test_put_entry_with_real_image(channel: grpc.Channel, bucket_id: str, ticket_id: str, image_path: str):
    stub: pb2_grpc.CloudberryStorageStub = pb2_grpc.CloudberryStorageStub(channel)

    # Читаем реальное изображение из файла
    with open(image_path, "rb") as image_file:
        image_data: bytes = image_file.read()

    stub: pb2_grpc.CloudberryStorageStub = pb2_grpc.CloudberryStorageStub(channel)
    fake_ticket: pb2.TicketEntry = pb2.TicketEntry(
        title=pb2.TextEntry(content="Some ticket blablabla"),
        description=pb2.TextEntry(content="Some description hard porn"),
        attachments=[
            pb2.ImageEntry(content=image_data, content_type=pb2.PNG),
            pb2.ImageEntry(content=image_data, content_type=pb2.PNG)]
    )
    request: pb2.PutEntryRequest = pb2.PutEntryRequest(
        external_ticket_id=ticket_id,
        bucket_uuid=bucket_id,
        ticket=fake_ticket,
    )
    response = stub.PutEntry(request)
    print("PutEntry Response:", response)


# def test_find(channel):
#     stub = pb2_grpc.CloudberryStorageStub(channel)
#     query = pb2.FindRequest(
#         p_bucket_uuid=TEST_BUCKET_UUID_0,
#         p_query="Graphic plot Aknowledge",
#         p_parameters=[Coefficient(p_parameter=Parameter.SEMANTIC_ONE_PEACE_SIMILARITY, p_value=0.9),
#                       Coefficient(p_parameter=Parameter.RECOGNIZED_TEXT_SIMILARITY, p_value=0.1)],
#         p_count=5
#     )
#     response = stub.Find(query)
#     print("Find Response:")
#     for entry in response.p_entries:
#         print(entry)


# def test_remove_entry(channel, bucket_id, content_id):
#     stub = pb2_grpc.CloudberryStorageStub(channel)
#     request = pb2.RemoveEntryRequest(
#         p_bucket_uuid=bucket_id,
#         p_content_uuid=content_id
#     )
#
#     try:
#         response = stub.RemoveEntry(request)
#         print(f"RemoveEntry Response: Успешно удалена запись {content_id} из коллекции {bucket_id}.")
#     except grpc.RpcError as e:
#         print(f"RemoveEntry Error: {e.details()} (code: {e.code()})")


def test_remove_bucket(channel: grpc.Channel, bucket_id: str):
    stub: pb2_grpc.CloudberryStorageStub = pb2_grpc.CloudberryStorageStub(channel)
    request = pb2.DestroyBucketRequest(
        p_bucket_uuid=bucket_id
    )

    try:
        response = stub.DestroyBucket(request)
        print(f"RemoveBucket Response: Успешно удалена коллекция {bucket_id}.")
    except grpc.RpcError as e:
        print(f"RemoveBucket Error: {e}")


if __name__ == "__main__":
    with grpc.insecure_channel("localhost:50051") as channel:
        # print("Testing InitBucket...")
        # test_init_bucket(channel)

        # test_put_entry(channel, TEST_BUCKET_UUID_0, FAKE_TICKET_UUID_1)
        test_put_entry_with_real_image(channel, TEST_BUCKET_UUID_0, FAKE_TICKET_UUID_0,"C:\\Users\\sckwo\\PycharmProjects\\cloudberry-storage\\ru\\nai\\cloudberry_storage\\test.png")

        # print("\nTesting Find...")
        # test_find(channel)

        # print("\nTesting RemoveEntry...")
        # test_remove_entry(channel, TEST_BUCKET_UUID, TEST_CONTENT_UUID)

        # print("\nTesting RemoveBucket...")
        # test_remove_bucket(channel, TEST_BUCKET_UUID_0)
