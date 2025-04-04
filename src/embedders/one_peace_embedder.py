# import logging
# import os
# import sys
#
# import numpy as np
# import torch
# from PIL import Image
#
# from .interfaces import ImageEmbedder, TextEmbedder, AudioEmbedder
#
# # from torchvision import transforms
# ONE_PEACE_GITHUB_REPO_DIR_PATH = '/home/meno/anymodal/Cloudberry-Storage-Any-Modal/ONE-PEACE/'
# ONE_PEACE_MODEL_PATH = '/home/meno/models/one-peace.pt'
# PYTESSERACT_PATH = r'/usr/bin/tesseract'
# ONE_PEACE_VECTOR_SIZE = 1536
#
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
#     datefmt='%Y-%m-%d %H:%M:%S',
#     handlers=[
#         logging.FileHandler("bot.log", encoding="utf-8"),
#         logging.StreamHandler(sys.stdout)
#     ]
# )
# logger = logging.getLogger(__name__)
#
#
# class OnePeaceMultimodalEmbedder(ImageEmbedder, TextEmbedder, AudioEmbedder):
#     def __init__(self):
#         model_dir = ONE_PEACE_GITHUB_REPO_DIR_PATH
#         model_name = ONE_PEACE_MODEL_PATH
#         if not os.path.isdir(model_dir):
#             raise FileNotFoundError(f'The directory "{model_dir}" does not exist')
#         if not os.path.isfile(model_name):
#             raise FileNotFoundError(f'The model file "{model_name}" does not exist')
#         one_peace_dir = os.path.normpath(ONE_PEACE_GITHUB_REPO_DIR_PATH)
#         if not os.path.isdir(one_peace_dir):
#             err_msg = f'The dir "{one_peace_dir}" does not exist'
#             logger.error(err_msg)
#             raise ValueError(err_msg)
#         model_name = os.path.normpath(ONE_PEACE_MODEL_PATH)
#         if not os.path.isfile(model_name):
#             err_msg = f'The file "{model_name}" does not exist'
#             logger.error(err_msg)
#             raise ValueError(err_msg)
#         sys.path.append(one_peace_dir)
#         from one_peace.models import from_pretrained
#
#         logger.info("Загрузка модели ONE-PEACE")
#         current_workdir = os.getcwd()
#         logger.info(f'Текущая рабочая директория: {current_workdir}')
#
#         os.chdir(one_peace_dir)
#         logger.info(f'Новая рабочая директория: {os.getcwd()}')
#         self.model = from_pretrained(model_name, device=torch.device('cpu'))
#         logger.info("ONE-PEACE был успешно загружен")
#         self.transforms = self.transforms = transforms.Compose([
#             transforms.Resize((256, 256)),
#             transforms.ToTensor(),
#             transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
#         ])
#
#     def encode_text(self, text: str) -> np.ndarray:
#         tokens = self.model.process_text([text])
#         with torch.no_grad():
#             return self.model.extract_text_features(tokens).squeeze().cpu().numpy()
#
#     def encode_image(self, image: Image.Image) -> np.ndarray:
#         image_tensor = self.transforms(image).unsqueeze(0)
#         with torch.no_grad():
#             return self.model.extract_image_features(image_tensor).squeeze().cpu().numpy()
#
#     def encode_audio(self, waveform: np.ndarray, sr: int) -> np.ndarray:
#         processed = self.model.process_audio(waveform, sr)
#         with torch.no_grad():
#             return self.model.extract_audio_features(processed).squeeze().cpu().numpy()
