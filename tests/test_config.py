"""Smoke tests for the shared constants in recycle_coach.config."""

from recycle_coach import config


def test_classes_are_fixed_and_alphabetical():
    assert config.CLASSES == ("recycling", "special_handling", "trash")
    assert list(config.CLASSES) == sorted(config.CLASSES)


def test_class_indices_match_order():
    assert [config.CLASS_TO_INDEX[name] for name in config.CLASSES] == [0, 1, 2]


def test_split_ratios_sum_to_one():
    assert abs(sum(config.SPLIT_RATIOS.values()) - 1.0) < 1e-9


def test_paths_are_inside_the_repo():
    assert (config.ROOT / "AGENTS.md").exists()
    assert config.METADATA_DIR.is_relative_to(config.ROOT)
