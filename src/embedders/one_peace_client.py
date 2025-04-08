import logging

import grpc
import one_peace_service_pb2 as pb2
import one_peace_service_pb2_grpc as pb2_grpc
from PIL.Image import Image
import soundfile as sf
from io import BytesIO

from cloudberry_storage_pb2 import ImageContentType

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("OnePeaceClient")


class OnePeaceClient:
    def __init__(self, host='localhost', port=60061):
        self.host = host
        self.port = port
        try:
            logger.info(f"Попытка подключения к gRPC-сервису ONE-PEACE по адресу {host}:{port}...")
            channel = grpc.insecure_channel(f"{host}:{port}")
            self.stub = pb2_grpc.OnePeaceEmbedderStub(channel)
            logger.info("Подключение к ONE-PEACE успешно установлено.")
        except Exception as e:
            logger.exception(f"Ошибка при подключении к ONE-PEACE gRPC-сервису: {e}")

    def encode_text(self, text: str):
        logger.info(f"Получен текст для эмбеддинга: '{text}'")
        try:
            request = pb2.TextRequest(text=text)
            response = self.stub.EncodeText(request)
            logger.info(f"Эмбеддинг текста успешно получен. Размер вектора: {len(response.vector)}")
            return list(response.vector)
        except grpc.RpcError as e:
            logger.error(f"gRPC-ошибка при вызове EncodeText: {e.details()} (code={e.code()})")
        except Exception as e:
            logger.exception(f"Непредвиденная ошибка при вызове EncodeText: {e}")
        return []

    def encode_image(self, image: Image, content_type: ImageContentType):
        logger.info(f"Получено изображение для эмбеддинга. Размер: {image.size}, формат: {image.mode}")
        try:
            if content_type == ImageContentType.PNG:
                format_str = "PNG"
            elif content_type == ImageContentType.JPEG:
                format_str = "JPEG"
            else:
                raise ValueError(f"Неподдерживаемый формат изображения: {content_type}")

            buffer = BytesIO()
            image.save(buffer, format=format_str)
            image_bytes = buffer.getvalue()

            logger.info(f"Изображение сериализовано в формате {format_str}, размер {len(image_bytes)} байт")

            request = pb2.ImageRequest(content=image_bytes)
            response = self.stub.EncodeImage(request)
            logger.info(f"Эмбеддинг изображения успешно получен. Размер вектора: {len(response.vector)}")
            return list(response.vector)
        except grpc.RpcError as e:
            logger.error(f"gRPC-ошибка при вызове EncodeImage: {e.details()} (code={e.code()})")
        except Exception as e:
            logger.exception(f"Непредвиденная ошибка при вызове EncodeImage: {e}")
        return []

    def encode_audio(self, audio_path: str):
        logger.info(f"Получен аудиофайл для эмбеддинга: {audio_path}")
        try:
            waveform, sample_rate = sf.read(audio_path, dtype='float32')
            if waveform.ndim > 1:
                waveform = waveform.mean(axis=1)
                logger.info("Аудиофайл был многоканальным, преобразован в моно.")
            content = waveform.tobytes()
            request = pb2.AudioRequest(content=content, sample_rate=sample_rate)
            response = self.stub.EncodeAudio(request)
            logger.info(f"Эмбеддинг аудио успешно получен. Размер вектора: {len(response.vector)}")
            return list(response.vector)
        except grpc.RpcError as e:
            logger.error(f"gRPC-ошибка при вызове EncodeAudio: {e.details()} (code={e.code()})")
        except Exception as e:
            logger.exception(f"Непредвиденная ошибка при вызове EncodeAudio: {e}")
        return []

# if __name__ == "__main__":
#     client = OnePeaceClient()
#
#     parser = argparse.ArgumentParser()
#     parser.add_argument("--text", type=str, help="Text to embed")
#     parser.add_argument("--image", type=str, help="Path to image")
#     parser.add_argument("--audio", type=str, help="Path to audio file")
#     args = parser.parse_args()
#
#     if args.text:
#         vec = client.encode_text(args.text)
#         print("Text embedding:", vec[:5], "...")
#
#     if args.image:
#         vec = client.encode_image(args.image)
#         print("Image embedding:", vec[:5], "...")
#
#     if args.audio:
#         vec = client.encode_audio(args.audio)
#         print("Audio embedding:", vec[:5], "...")
