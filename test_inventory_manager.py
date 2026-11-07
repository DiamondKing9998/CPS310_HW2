"""Automated pytest tests for the CPS 310 Inventory Manager (Homework 2).

Run the full suite with:
    python -m pytest -v

No test reads from or writes to the real inventory.txt file. File tests use
pytest's tmp_path fixture, and all other tests work on in-memory lists.
"""

import pytest

from inventory_manager import (
    calculate_summary,
    find_matching_items,
    load_inventory,
    parse_quantity,
    remove_item_by_number,
    save_inventory,
    update_item_quantity,
    validate_new_item,
)


@pytest.fixture
def sample_inventory():
    """Five items across three categories, two of which are low stock (< 5)."""
    return [
        {"name": "Laptop Charger", "category": "Electronics", "quantity": 8},
        {"name": "Phone Charger", "category": "Electronics", "quantity": 5},
        {"name": "Printer Paper", "category": "Office Supplies", "quantity": 25},
        {"name": "Sticky Notes", "category": "Office Supplies", "quantity": 4},
        {"name": "Dry-Erase Markers", "category": "Classroom Supplies", "quantity": 3},
    ]


# ---------------------------------------------------------------------------
# 1. File loading
# ---------------------------------------------------------------------------


def test_load_inventory_reads_valid_file(tmp_path):
    # Arrange
    file_path = tmp_path / "inventory.txt"
    file_path.write_text(
        "HDMI Cable|Electronics|6\nStapler|Office Supplies|2\n", encoding="utf-8"
    )

    # Act
    inventory = load_inventory(file_path)

    # Assert
    assert inventory == [
        {"name": "HDMI Cable", "category": "Electronics", "quantity": 6},
        {"name": "Stapler", "category": "Office Supplies", "quantity": 2},
    ]


def test_load_inventory_converts_quantities_to_integers(tmp_path):
    # Arrange
    file_path = tmp_path / "inventory.txt"
    file_path.write_text("Printer Paper|Office Supplies|25\n", encoding="utf-8")

    # Act
    inventory = load_inventory(file_path)

    # Assert
    assert inventory[0]["quantity"] == 25
    assert isinstance(inventory[0]["quantity"], int)


def test_load_inventory_ignores_blank_lines(tmp_path):
    # Arrange
    file_path = tmp_path / "inventory.txt"
    file_path.write_text(
        "\nPens|Office Supplies|10\n\n   \nTape|Office Supplies|3\n\n",
        encoding="utf-8",
    )

    # Act
    inventory = load_inventory(file_path)

    # Assert
    assert [item["name"] for item in inventory] == ["Pens", "Tape"]


def test_load_inventory_missing_file_returns_empty_list(tmp_path):
    # Arrange
    missing_path = tmp_path / "does_not_exist.txt"

    # Act
    inventory = load_inventory(missing_path)

    # Assert
    assert inventory == []


# ---------------------------------------------------------------------------
# 2. File saving
# ---------------------------------------------------------------------------


def test_save_inventory_writes_pipe_delimited_lines(tmp_path, sample_inventory):
    # Arrange
    file_path = tmp_path / "inventory.txt"

    # Act
    save_inventory(sample_inventory, file_path)

    # Assert
    assert file_path.read_text(encoding="utf-8").splitlines() == [
        "Laptop Charger|Electronics|8",
        "Phone Charger|Electronics|5",
        "Printer Paper|Office Supplies|25",
        "Sticky Notes|Office Supplies|4",
        "Dry-Erase Markers|Classroom Supplies|3",
    ]


def test_save_empty_inventory_creates_empty_file(tmp_path):
    # Arrange
    file_path = tmp_path / "inventory.txt"

    # Act
    save_inventory([], file_path)

    # Assert
    assert file_path.exists()
    assert file_path.read_text(encoding="utf-8") == ""


def test_save_then_load_round_trip_preserves_inventory(tmp_path, sample_inventory):
    # Arrange
    file_path = tmp_path / "inventory.txt"

    # Act
    save_inventory(sample_inventory, file_path)
    loaded_inventory = load_inventory(file_path)

    # Assert
    assert loaded_inventory == sample_inventory
