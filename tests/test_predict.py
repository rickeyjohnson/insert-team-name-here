"""Unit tests for predict.py (Dakarai / Amaka)."""

from PIL import Image
import pytest

from recycle_coach import config, predict


def test_fake_predictor_api_structure():
    pred = predict.load_predictor(fake=True)
    im = Image.new("RGB", (224, 224), color=(100, 100, 100))

    res = pred.predict(im)

    assert "label" in res
    assert "confidence" in res
    assert "probs" in res
    assert "guidance" in res
    assert res["label"] in config.CLASSES
    assert sum(res["probs"].values()) == pytest.approx(1.0, 0.01)
    assert not res["low_confidence"]


def test_predictor_low_confidence():
    pred = predict.FakePredictor(default_label="recycling")
    im = Image.new("RGB", (224, 224), color=(100, 100, 100))

    # Set threshold above default fake confidence (0.85)
    res = pred.predict(im, threshold=0.90)

    assert res["low_confidence"] is True
    assert "Not sure" in res["guidance"]


def test_real_predictor_architecture_forward():
    # Test Predictor initialized without checkpoint (random weights forward pass)
    pred = predict.Predictor(checkpoint_path=None, device="cpu")
    im = Image.new("RGB", (224, 224), color=(200, 150, 50))

    res = pred.predict(im)

    assert res["label"] in config.CLASSES
    assert 0.0 <= res["confidence"] <= 1.0
    assert sum(res["probs"].values()) == pytest.approx(1.0, 0.001)
    assert len(res["probs"]) == 3
