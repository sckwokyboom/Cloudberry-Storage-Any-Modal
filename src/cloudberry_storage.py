import logging
import uuid
from concurrent import futures
from io import BytesIO

import grpc
import pytesseract
from PIL import Image
from deep_translator import GoogleTranslator
from google.protobuf.internal.containers import RepeatedCompositeFieldContainer
from grpc import ServicerContext
from torchvision import transforms
from qdrant_client import models, QdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse
from qdrant_client.models import Distance, VectorParams

from embedders.sbert_embedder import SBERTEmbedder
from model_registry import ModelRegistry
import cloudberry_storage_pb2 as pb2
import cloudberry_storage_pb2_grpc as pb2_grpc
from cloudberry_storage_pb2 import InitBucketRequest, DestroyBucketRequest, Empty, FindRequest, \
    RemoveEntryRequest, PutEntryRequest, ImageEntry, FindResponse, FindResponseEntry

from sentence_transformers import SentenceTransformer
from torchvision import transforms

from embedders.one_peace_client import OnePeaceClient

# Constants
ONE_PEACE_VECTOR_SIZE = 1536
SBERT_VECTOR_SIZE = 384

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CloudberryStorage")


def is_valid_uuid(value):
    try:
        uuid.UUID(value)
        return True
    except ValueError:
        return False


class CloudberryStorage(pb2_grpc.CloudberryStorageServicer):
    def __init__(self, registry: ModelRegistry):
        self.models_registry: ModelRegistry = registry

    def create_collection_if_not_exists(self, collection_name: str) -> None:
        try:
            self.models_registry.qdrant_client.get_collection(collection_name)
            logger.info(f"Коллекция {collection_name} уже существует.")
        except:
            self.models_registry.qdrant_client.create_collection(
                collection_name=collection_name,
                vectors_config={
                    "one_peace_embedding": VectorParams(size=ONE_PEACE_VECTOR_SIZE, distance=Distance.COSINE),
                    "ocr_text_sbert_embedding": VectorParams(size=SBERT_VECTOR_SIZE, distance=Distance.COSINE),
                    "description_sbert_embedding": VectorParams(size=SBERT_VECTOR_SIZE, distance=Distance.COSINE),
                    "title_sbert_embedding": VectorParams(size=SBERT_VECTOR_SIZE, distance=Distance.COSINE),
                }
            )
            logger.info(f"Создана новая коллекция {collection_name} с несколькими векторами.")

    def InitBucket(self, request: InitBucketRequest, context: ServicerContext) -> Empty:
        logger.info(f"Пришёл запрос на инициализацию bucket с UUID: {request.bucket_uuid}.")
        bucket_uuid: str = request.bucket_uuid
        try:
            self.create_collection_if_not_exists(bucket_uuid)
            logger.info(f"Коллекция успешно проинициализирована.")
        except Exception as e:
            logger.error(f"Ошибка при регистрации bucket'а {bucket_uuid}: {e}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error creating Qdrant collection: {e}")
            return Empty()
        return Empty()

    def DestroyBucket(self, request: DestroyBucketRequest, context: ServicerContext) -> Empty:
        logger.info(f"Запрос на уничтожение коллекции с bucket_uuid: {request.bucket_uuid}.")
        bucket_uuid: str = request.bucket_uuid
        try:
            self.models_registry.qdrant_client.get_collection(bucket_uuid)
            logger.info(f"Коллекция успешно найдена.")
        except UnexpectedResponse:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Bucket collection {bucket_uuid} not found.")
            logger.error(f"Коллекция не найдена.")
            return pb2.Empty()

        try:
            self.models_registry.qdrant_client.delete_collection(bucket_uuid)
            print(f"Deleted collection for bucket: {bucket_uuid}")
            logger.info(f"Коллекция успешно удалена.")
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error deleting Qdrant collection: {e}")
            logger.error(f"Коллекция не уничтожена из-за ошибки: {e}.")
            return pb2.Empty()
        return pb2.Empty()

    def PutEntry(self, request: PutEntryRequest, context: ServicerContext) -> Empty:
        bucket_uuid: str = request.bucket_uuid
        external_id: str = request.external_ticket_id
        title: str = request.ticket.title.content
        description: str = request.ticket.description.content
        attachments: RepeatedCompositeFieldContainer[ImageEntry] = request.ticket.attachments
        logger.info(f"Получен тикет {external_id}")

        try:
            points = []
            payload_base = {
                "ticket_id": external_id,
                "title": title,
                "description": description,
            }

            title_vec = self.models_registry.text_embedder.encode_text(title).tolist()
            # title_vec = np.ones(SBERT_VECTOR_SIZE).tolist()
            # desc_vec = models_registry.sbert.encode(description).tolist()
            # desc_vec = np.ones(SBERT_VECTOR_SIZE).tolist()
            desc_vec = self.models_registry.text_embedder.encode_text(description).tolist()

            # --- Точка: title ---
            points.append(models.PointStruct(
                id=str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{external_id}_title")),
                vector={"title_sbert_embedding": title_vec},
                payload={**payload_base, "type": "title"}
            ))
            logger.info(f"Точка с ID {external_id}_title добавлена в коллекцию {bucket_uuid}.")

            # --- Точка: description ---
            points.append(models.PointStruct(
                id=str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{external_id}_desc")),
                vector={"description_sbert_embedding": desc_vec},
                payload={**payload_base, "type": "description"}
            ))
            logger.info(f"Точка с ID {external_id}_desc добавлена в коллекцию {bucket_uuid}.")

            # --- Точки: изображения ---
            for idx, img in enumerate(attachments):
                image: Image = Image.open(BytesIO(img.content)).convert("RGB")
                image_vec = self.models_registry.one_peace_client.encode_image(image, img.content_type)
                # image_vec = np.ones(ONE_PEACE_VECTOR_SIZE).tolist()

                # ocr_text = pytesseract.image_to_string(image, lang='eng+rus').strip()
                ocr_text = "HELLO! Это распознанный текст"
                ocr_vec = self.models_registry.text_embedder.encode_text(ocr_text).tolist()
                # ocr_vec = (
                #     # models_registry.sbert.encode(ocr_text).tolist()
                #     np.ones(SBERT_VECTOR_SIZE).tolist()
                #     if ocr_text else np.zeros(SBERT_VECTOR_SIZE).tolist()
                # )

                point = models.PointStruct(
                    id=str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{external_id}_img_{idx}")),
                    vector={
                        "one_peace_embedding": image_vec,
                        "ocr_text_sbert_embedding": ocr_vec
                    },
                    payload={
                        **payload_base,
                        "ocr_text": ocr_text,
                        "img_idx": idx,
                        "type": "image"
                    }
                )
                points.append(point)
                logger.info(f"Точка с ID {external_id}_img_{idx} добавлена в коллекцию {bucket_uuid}.")

            # --- Вставка в Qdrant ---
            self.models_registry.qdrant_client.upsert(collection_name=bucket_uuid, points=points)
            logger.info(f"Тикет {external_id} добавлен в {bucket_uuid}: {len(points)} точек.")

        except Exception as e:
            logger.error(f"Ошибка при добавлении тикета {external_id}: {e}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Ошибка добавления тикета: {e}")
            return pb2.Empty()

        return pb2.Empty()

    def RemoveEntry(self, request: RemoveEntryRequest, context: ServicerContext) -> Empty:
        bucket_uuid: str = request.bucket_uuid
        external_ticket_id: str = request.external_ticket_id
        try:
            self.models_registry.qdrant_client.delete(
                collection_name=bucket_uuid,
                points_selector=models.FilterSelector(
                    filter=models.Filter(
                        must=[
                            models.FieldCondition(
                                key="ticket_id",
                                match=models.MatchValue(value=external_ticket_id)
                            )
                        ]
                    )
                )
            )
            logger.info(f"Удалены все точки для ticket_id={external_ticket_id} из {bucket_uuid}")
        except Exception as e:
            logger.error(f"Ошибка при удалении ticket_id={external_ticket_id}: {e}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Ошибка при удалении: {e}")
        return pb2.Empty()

    def Find(self, request: FindRequest, context):
        text_query: str = request.query.content
        images: RepeatedCompositeFieldContainer[ImageEntry] = request.images
        bucket_uuid: str = request.bucket_uuid
        top_k: int = request.top_k

        try:
            # === 1. Генерация векторов запроса ===
            translated_query = GoogleTranslator(source='auto', target='en').translate(text_query)

            # Текстовые вектора
            text_vec = self.models_registry.text_embedder.encode_text(translated_query)
            one_peace_text_vec = self.models_registry.one_peace_client.encode_text(translated_query)

            # Вектора изображений (по каждому отдельно)
            image_vectors = []
            for img in images:
                pil = Image.open(BytesIO(img.content)).convert("RGB")
                image_vectors.append(self.models_registry.one_peace_client.encode_image(pil, img.content_type))

            # === 2. Поиск по каждому модальному вектору ===
            aggregated_scores = {}

            def add_scores(results, modality):
                for pt in results:
                    ticket_id = pt.payload.get("ticket_id")
                    if not ticket_id:
                        continue
                    score = pt.score
                    if ticket_id not in aggregated_scores:
                        aggregated_scores[ticket_id] = 0.0
                    aggregated_scores[ticket_id] += score

            # Поиск по тексту (sbert)
            res = self.models_registry.qdrant_client.query_points(
                collection_name=bucket_uuid,
                query=text_vec.tolist(),
                limit=top_k,
                with_payload=True,
                with_vectors=False,
                using="description_sbert_embedding"
            ).points
            add_scores(res, "text")

            # Поиск по каждому изображению
            for idx, vec in enumerate(image_vectors):
                res = self.models_registry.qdrant_client.query_points(
                    collection_name=bucket_uuid,
                    query=vec.tolist(),
                    limit=top_k,
                    with_payload=True,
                    with_vectors=False,
                    using="one_peace_embedding"
                ).points
                add_scores(res, f"image_{idx}")

            # === 3. Агрегация результатов ===
            sorted_tickets = sorted(aggregated_scores.items(), key=lambda x: x[1], reverse=True)

            # === 4. Формирование ответа ===
            response = FindResponse()
            for ticket_id, _ in sorted_tickets[:10]:
                response.entries.append(FindResponseEntry(external_id=ticket_id))

            return response

        except Exception as e:
            logger.error(f"Ошибка в Find: {e}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Ошибка при выполнении поиска: {e}")
            return FindResponse()


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    registry: ModelRegistry = ModelRegistry(
        text_embedder=SBERTEmbedder(),
        one_peace_client=OnePeaceClient(),
        qdrant_client=QdrantClient("http://localhost:6333")
    )
    pb2_grpc.add_CloudberryStorageServicer_to_server(CloudberryStorage(registry), server)
    server.add_insecure_port("[::]:8002")
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
