"""Two-stage MobileNetV3 fine-tuning with early stopping on val macro F1.

Owner: Dakarai Lanes · Build plan: 3.2 · Spec: docs/PROJECT_SPEC.md §10, §8.8
Reads: data/metadata/splits.csv, data/processed/
Writes: models/mobilenetv3_best.pt
"""

import logging
import time
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.metrics import accuracy_score, f1_score
from torch.utils.data import DataLoader
from torchvision import models

from recycle_coach import config
from recycle_coach.dataset import create_dataloaders

logger = logging.getLogger(__name__)


def get_device() -> torch.device:
    """Pick CUDA if available, then MPS (Apple Silicon), then CPU."""
    if torch.cuda.is_available():
        return torch.device("cuda")
    elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def build_model(num_classes: int = len(config.CLASSES), pretrained: bool = True) -> nn.Module:
    """Construct MobileNetV3-Large with updated classifier layer."""
    weights = (
        models.MobileNet_V3_Large_Weights.DEFAULT
        if pretrained
        else None
    )
    model = models.mobilenet_v3_large(weights=weights)
    in_features = model.classifier[3].in_features
    model.classifier[3] = nn.Linear(in_features, num_classes)
    return model


def compute_class_weights(
    splits_df: pd.DataFrame,
    device: torch.device,
) -> torch.Tensor:
    """Compute balanced class weights from the train split."""
    train_df = splits_df[splits_df["split"] == "train"]
    counts = train_df["final_label"].value_counts().reindex(config.CLASSES, fill_value=1).values
    total = sum(counts)
    n_classes = len(config.CLASSES)
    weights = total / (n_classes * counts.astype(np.float32))
    return torch.tensor(weights, dtype=torch.float32, device=device)


@torch.no_grad()
def evaluate_epoch(
    model: nn.Module,
    dataloader: DataLoader,
    device: torch.device,
) -> Dict[str, float]:
    """Evaluate model on DataLoader and return accuracy and macro F1."""
    model.eval()
    all_preds: List[int] = []
    all_targets: List[int] = []

    for images, targets in dataloader:
        images = images.to(device)
        logits = model(images)
        preds = torch.argmax(logits, dim=1).cpu().numpy()
        all_preds.extend(preds.tolist())
        all_targets.extend(targets.numpy().tolist())

    acc = float(accuracy_score(all_targets, all_preds))
    f1 = float(f1_score(all_targets, all_preds, average="macro", zero_division=0))
    return {"accuracy": round(acc, 4), "macro_f1": round(f1, 4)}


def train_model(
    splits_csv: Path = config.SPLITS_CSV,
    processed_dir: Path = config.PROCESSED_DIR,
    checkpoint_path: Path = config.CHECKPOINT_PATH,
    stage1_epochs: int = 3,
    stage2_epochs: int = 15,
    stage1_lr: float = 1e-3,
    stage2_lr: float = 1e-4,
    batch_size: int = 32,
    patience: int = 5,
    pretrained: bool = True,
    device: Optional[torch.device] = None,
) -> Dict[str, Any]:
    """Two-stage training pipeline with early stopping."""
    if device is None:
        device = get_device()
    logger.info("Training on device: %s", device)

    splits_df = pd.read_csv(splits_csv)
    loaders = create_dataloaders(
        splits_csv=splits_csv,
        processed_dir=processed_dir,
        batch_size=batch_size,
    )
    dl_train = loaders["train"]
    dl_val = loaders["val"]

    class_weights = compute_class_weights(splits_df, device=device)
    criterion = nn.CrossEntropyLoss(weight=class_weights)

    model = build_model(pretrained=pretrained).to(device)

    # Stage 1: Train classifier head only
    logger.info("Stage 1: Training classifier head (%d epochs)...", stage1_epochs)
    for param in model.features.parameters():
        param.requires_grad = False

    opt_stage1 = torch.optim.AdamW(model.classifier.parameters(), lr=stage1_lr)

    for ep in range(1, stage1_epochs + 1):
        model.train()
        for images, targets in dl_train:
            images, targets = images.to(device), targets.to(device)
            opt_stage1.zero_grad()
            loss = criterion(model(images), targets)
            loss.backward()
            opt_stage1.step()

    # Stage 2: Unfreeze backbone and fine-tune entire network
    logger.info("Stage 2: Full fine-tuning (%d epochs max, patience %d)...", stage2_epochs, patience)
    for param in model.parameters():
        param.requires_grad = True

    opt_stage2 = torch.optim.AdamW(model.parameters(), lr=stage2_lr, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(opt_stage2, T_max=stage2_epochs)

    best_macro_f1 = -1.0
    best_state_dict = None
    best_epoch = 0
    epochs_no_improve = 0
    history: List[Dict[str, Any]] = []

    for ep in range(1, stage2_epochs + 1):
        t0 = time.time()
        model.train()
        total_loss = 0.0
        n_samples = 0

        for images, targets in dl_train:
            images, targets = images.to(device), targets.to(device)
            opt_stage2.zero_grad()
            loss = criterion(model(images), targets)
            loss.backward()
            opt_stage2.step()

            total_loss += loss.item() * len(targets)
            n_samples += len(targets)

        scheduler.step()
        avg_train_loss = total_loss / max(n_samples, 1)

        val_scores = evaluate_epoch(model, dl_val, device=device)
        val_f1 = val_scores["macro_f1"]
        val_acc = val_scores["accuracy"]

        history.append({
            "epoch": ep,
            "train_loss": round(avg_train_loss, 4),
            "val_accuracy": val_acc,
            "val_macro_f1": val_f1,
            "elapsed_sec": round(time.time() - t0, 1),
        })

        logger.info(
            "Epoch %2d: train loss %.4f | val acc %.3f | val macro F1 %.3f (%ds)",
            ep, avg_train_loss, val_acc, val_f1, int(time.time() - t0),
        )

        if val_f1 > best_macro_f1:
            best_macro_f1 = val_f1
            best_epoch = ep
            best_state_dict = {k: v.cpu() for k, v in model.state_dict().items()}
            epochs_no_improve = 0
        else:
            epochs_no_improve += 1
            if epochs_no_improve >= patience:
                logger.info("Early stopping triggered at epoch %d", ep)
                break

    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    checkpoint_data = {
        "arch": "mobilenet_v3_large",
        "classes": list(config.CLASSES),
        "img_size": config.IMG_SIZE,
        "mean": list(config.IMAGENET_MEAN),
        "std": list(config.IMAGENET_STD),
        "state_dict": best_state_dict or model.state_dict(),
        "val_macro_f1": best_macro_f1,
        "best_epoch": best_epoch,
        "split_seed": config.SEED,
        "trained_at": str(date.today()),
    }
    torch.save(checkpoint_data, checkpoint_path)
    logger.info("Saved best checkpoint to %s (val macro F1: %.4f)", checkpoint_path, best_macro_f1)

    return {
        "best_macro_f1": best_macro_f1,
        "best_epoch": best_epoch,
        "history": history,
        "checkpoint_path": str(checkpoint_path),
    }
