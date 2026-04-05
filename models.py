"""
models.py - AI 特征提取模型
基于 ResNet50 提取图像深度特征
"""
import logging
from PIL import Image

logger = logging.getLogger(__name__)


class AIFeatureExtractor:
    _instance = None
    _model = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_model()
        return cls._instance
    
    def _init_model(self):
        try:
            import torch
            import torchvision.models as models
            import torchvision.transforms as transforms
            self.device = torch.device("cpu")
            self.model = models.resnet50(weights="DEFAULT")
            self.model = torch.nn.Sequential(*list(self.model.children())[:-1])
            self.model.to(self.device)
            self.model.eval()
            self.transform = transforms.Compose([transforms.Resize(256), transforms.CenterCrop(224), transforms.ToTensor(), transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])])
            logger.info("AI 特征提取模型已加载 (ResNet50)")
        except ImportError as e:
            logger.error(f"请安装 torch 和 torchvision: {e}")
            self.model = None
    
    def extract(self, image_path):
        if self.model is None:
            raise RuntimeError("AI 模型未加载")
        import torch
        img = Image.open(image_path).convert("RGB")
        tensor = self.transform(img).unsqueeze(0).to(self.device)
        with torch.no_grad():
            features = self.model(tensor)
        return features.squeeze().cpu().numpy()
    
    def extract_batch(self, image_paths, batch_size=16):
        if self.model is None:
            raise RuntimeError("AI 模型未加载")
        import torch
        results = {}
        for i in range(0, len(image_paths), batch_size):
            batch = image_paths[i:i+batch_size]
            tensors = []
            valid_paths = []
            for path in batch:
                try:
                    img = Image.open(path).convert("RGB")
                    tensor = self.transform(img)
                    tensors.append(tensor)
                    valid_paths.append(path)
                except Exception as e:
                    logger.warning(f"图片加载失败 {path}: {e}")
            if not tensors:
                continue
            batch_tensor = torch.stack(tensors).to(self.device)
            with torch.no_grad():
                features = self.model(batch_tensor)
            features = features.squeeze().cpu().numpy()
            if features.ndim == 1:
                results[valid_paths[0]] = features
            else:
                for path, feat in zip(valid_paths, features):
                    results[path] = feat
        return results
