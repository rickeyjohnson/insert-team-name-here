"""load_predictor() and predict(): the only way the app talks to the model.

Owner: Dakarai Lanes · Build plan: 3.4 · Spec: docs/PROJECT_SPEC.md §8.9, §12
Reads: models/mobilenetv3_best.pt, a PIL image
Writes: (nothing; returns {label, confidence, probs, guidance})
"""

import logging
from pathlib import Path
from typing import Any, Dict, Optional, Union

import numpy as np
import torch
import torch.nn as nn
from PIL import Image, ImageOps
from torchvision import models

from recycle_coach import config
from recycle_coach.dataset import get_transforms

logger = logging.getLogger(__name__)

GUIDANCE = {
    "recycling": "Recycling bin: empty and rinse; flatten cardboard.",
    "special_handling": (
        "Special handling: do not bin. Take to designated drop-off "
        "or check with campus facilities."
    ),
    "trash": "Trash bin: not accepted in standard campus recycling.",
}

LOW_CONFIDENCE_MESSAGE = "Not sure. Check the label guide or ask campus facilities."


class Predictor:
    """Production predictor wrapper for MobileNetV3 checkpoint."""

    def __init__(
        self,
        checkpoint_path: Optional[Path] = None,
        device: Optional[str] = None,
    ) -> None:
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device

        self.transform = get_transforms(split="val")
        self.classes = list(config.CLASSES)
        self.model = self._load_model(checkpoint_path)

    def _load_model(self, checkpoint_path: Optional[Path]) -> nn.Module:
        model = models.mobilenet_v3_large(weights=None)
        in_features = model.classifier[3].in_features
        model.classifier[3] = nn.Linear(in_features, len(self.classes))

        if checkpoint_path and Path(checkpoint_path).exists():
            ckpt = torch.load(checkpoint_path, map_location=self.device)
            state_dict = ckpt.get("state_dict", ckpt)
            model.load_state_dict(state_dict)
            logger.info("Loaded MobileNetV3 weights from %s", checkpoint_path)
        else:
            logger.warning(
                "Checkpoint %s not found. Model initialized with random weights.",
                checkpoint_path,
            )

        model.to(self.device)
        model.eval()
        return model

    @torch.no_grad()
    def predict(
        self,
        image: Union[Image.Image, Path, str],
        threshold: float = config.LOW_CONFIDENCE,
    ) -> Dict[str, Any]:
        """Predict class, probabilities, and disposal guidance for one image."""
        if not isinstance(image, Image.Image):
            with Image.open(image) as raw:
                pil_img = ImageOps.exif_transpose(raw).convert("RGB")
        else:
            pil_img = ImageOps.exif_transpose(image).convert("RGB")

        tensor = self.transform(pil_img).unsqueeze(0).to(self.device)
        logits = self.model(tensor)
        probs = torch.softmax(logits, dim=1)[0].cpu().numpy()

        k = int(np.argmax(probs))
        top_label = self.classes[k]
        top_confidence = round(float(probs[k]), 4)

        probs_dict = {
            cls_name: round(float(p), 4) for cls_name, p in zip(self.classes, probs)
        }

        if top_confidence >= threshold:
            guidance = GUIDANCE.get(top_label, "")
            is_low_confidence = False
        else:
            guidance = LOW_CONFIDENCE_MESSAGE
            is_low_confidence = True

        return {
            "label": top_label,
            "confidence": top_confidence,
            "probs": probs_dict,
            "guidance": guidance,
            "low_confidence": is_low_confidence,
        }


class FakePredictor:
    """Mock predictor for testing the demo app before weights are trained."""

    def __init__(self, default_label: str = "recycling") -> None:
        self.default_label = default_label
        self.classes = list(config.CLASSES)

    def predict(
        self,
        image: Union[Image.Image, Path, str],
        threshold: float = config.LOW_CONFIDENCE,
    ) -> Dict[str, Any]:
        probs = {
            "recycling": 0.85 if self.default_label == "recycling" else 0.10,
            "special_handling": 0.05 if self.default_label != "special_handling" else 0.85,
            "trash": 0.10 if self.default_label != "trash" else 0.85,
        }
        confidence = probs[self.default_label]
        return {
            "label": self.default_label,
            "confidence": confidence,
            "probs": probs,
            "guidance": GUIDANCE[self.default_label]
            if confidence >= threshold
            else LOW_CONFIDENCE_MESSAGE,
            "low_confidence": confidence < threshold,
        }


def load_predictor(
    checkpoint_path: Optional[Union[str, Path]] = config.CHECKPOINT_PATH,
    fake: bool = False,
    device: Optional[str] = None,
) -> Union[Predictor, FakePredictor]:
    """Load predictor model or fallback to fake if checkpoint is missing."""
    if fake:
        return FakePredictor()

    if checkpoint_path is None or not Path(checkpoint_path).exists():
        logger.warning(
            "Checkpoint %s not found. Falling back to FakePredictor.", checkpoint_path
        )
        return FakePredictor()

    return Predictor(checkpoint_path=Path(checkpoint_path), device=device)
