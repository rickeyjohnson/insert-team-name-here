"""Tests for the CP3 comparison helpers (Dakarai)."""

import pandas as pd
import pytest
import torch
from PIL import Image

from recycle_coach import config, demo_eval, predict, train


@pytest.mark.parametrize("arch", sorted(train.ARCHITECTURES))
def test_build_model_outputs_three_classes(arch):
    model = train.build_model(pretrained=False, arch=arch).eval()
    with torch.no_grad():
        out = model(torch.zeros(1, 3, config.IMG_SIZE, config.IMG_SIZE))
    assert out.shape == (1, len(config.CLASSES))


@pytest.mark.parametrize("arch", sorted(train.ARCHITECTURES))
def test_head_and_backbone_split_all_parameters(arch):
    model = train.build_model(pretrained=False, arch=arch)
    head, backbone = train._head_and_backbone(model, arch)
    n_head = sum(p.numel() for p in head.parameters())
    n_back = sum(p.numel() for p in backbone.parameters())
    assert n_head > 0 and n_back > 0
    assert n_head + n_back == sum(p.numel() for p in model.parameters())


def test_build_model_rejects_unknown_arch():
    with pytest.raises(ValueError):
        train.build_model(pretrained=False, arch="vgg16")


def test_oversampler_balances_classes():
    df = pd.DataFrame({
        "image_id": [f"x{i}" for i in range(120)],
        "final_label": ["recycling"] * 80 + ["trash"] * 30 + ["special_handling"] * 10,
        "split": ["train"] * 120,
    })
    sampler = train.make_oversampler(df)
    drawn = df["final_label"].iloc[list(sampler)].value_counts(normalize=True)
    assert len(list(sampler)) == 120
    assert drawn["special_handling"] > 0.2  # ~1/3 expected vs 0.08 without oversampling


def test_predictor_loads_arch_from_checkpoint(tmp_path):
    model = train.build_model(pretrained=False, arch="mobilenet_v3_small")
    ckpt = tmp_path / "small.pt"
    torch.save({"arch": "mobilenet_v3_small", "state_dict": model.state_dict()}, ckpt)
    pred = predict.Predictor(checkpoint_path=ckpt, device="cpu")
    assert pred.arch == "mobilenet_v3_small"
    res = pred.predict(Image.new("RGB", (300, 200), color=(10, 200, 30)))
    assert res["label"] in config.CLASSES


def test_predictor_old_checkpoint_without_arch_is_large(tmp_path):
    model = train.build_model(pretrained=False, arch="mobilenet_v3_large")
    ckpt = tmp_path / "old.pt"
    torch.save({"state_dict": model.state_dict()}, ckpt)
    assert predict.Predictor(checkpoint_path=ckpt, device="cpu").arch == "mobilenet_v3_large"


@pytest.mark.parametrize("name,expected", [
    ("test_js_special_handling_battery.jpg", "special_handling"),
    ("test_rj_trash_chips.jpg", "trash"),
    ("test_ao_recycling_can.JPG", "recycling"),
    ("IMG_1234.jpg", None),
])
def test_label_from_filename(name, expected):
    assert demo_eval.label_from_filename(name) == expected
