import argparse

import grpc
import one_peace_service_pb2 as pb2
import one_peace_service_pb2_grpc as pb2_grpc
from PIL.Image import Image


class OnePeaceClient:
    def __init__(self, host='localhost', port=60061):
        channel = grpc.insecure_channel(f"{host}:{port}")
        self.stub = pb2_grpc.OnePeaceEmbedderStub(channel)

    def encode_text(self, text: str):
        request = pb2.TextRequest(text=text)
        response = self.stub.EncodeText(request)
        return list(response.vector)

    def encode_image(self, image: Image):
        request = pb2.ImageRequest(content=image.tobytes())
        response = self.stub.EncodeImage(request)
        return list(response.vector)

    def encode_audio(self, audio_path: str):
        waveform, sample_rate = sf.read(audio_path, dtype='float32')
        # Ensure mono
        if waveform.ndim > 1:
            waveform = waveform.mean(axis=1)
        content = waveform.tobytes()
        request = pb2.AudioRequest(content=content, sample_rate=sample_rate)
        response = self.stub.EncodeAudio(request)
        return list(response.vector)


if __name__ == "__main__":
    client = OnePeaceClient()

    parser = argparse.ArgumentParser()
    parser.add_argument("--text", type=str, help="Text to embed")
    parser.add_argument("--image", type=str, help="Path to image")
    parser.add_argument("--audio", type=str, help="Path to audio file")
    args = parser.parse_args()

    if args.text:
        vec = client.encode_text(args.text)
        print("Text embedding:", vec[:5], "...")

    if args.image:
        vec = client.encode_image(args.image)
        print("Image embedding:", vec[:5], "...")

    if args.audio:
        vec = client.encode_audio(args.audio)
        print("Audio embedding:", vec[:5], "...")
