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


# ---------------------------------------------------------------------------
# 3. Search
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "search_term, expected_names",
    [
        ("Printer Paper", ["Printer Paper"]),
        ("paper", ["Printer Paper"]),
        ("sTiCkY nOtEs", ["Sticky Notes"]),
        ("charger", ["Laptop Charger", "Phone Charger"]),
        ("stapler", []),
        ("", []),
        ("   ", []),
    ],
    ids=[
        "exact-name",
        "partial-name",
        "ignores-capitalization",
        "multiple-matches",
        "no-matches",
        "empty-term",
        "whitespace-only-term",
    ],
)
def test_find_matching_items_returns_expected_items(
    sample_inventory, search_term, expected_names
):
    # Arrange: sample_inventory fixture and parameterized search term

    # Act
    matches = find_matching_items(sample_inventory, search_term)

    # Assert
    assert [item["name"] for item in matches] == expected_names


# ---------------------------------------------------------------------------
# 4. Remove item
# ---------------------------------------------------------------------------


def test_remove_first_item(sample_inventory):
    # Arrange
    item_number = 1

    # Act
    removed_item = remove_item_by_number(sample_inventory, item_number)

    # Assert
    assert removed_item["name"] == "Laptop Charger"
    assert [item["name"] for item in sample_inventory] == [
        "Phone Charger",
        "Printer Paper",
        "Sticky Notes",
        "Dry-Erase Markers",
    ]


def test_remove_middle_item(sample_inventory):
    # Arrange
    item_number = 3

    # Act
    removed_item = remove_item_by_number(sample_inventory, item_number)

    # Assert
    assert removed_item["name"] == "Printer Paper"
    assert [item["name"] for item in sample_inventory] == [
        "Laptop Charger",
        "Phone Charger",
        "Sticky Notes",
        "Dry-Erase Markers",
    ]


def test_remove_last_item(sample_inventory):
    # Arrange
    item_number = 5

    # Act
    removed_item = remove_item_by_number(sample_inventory, item_number)

    # Assert
    assert removed_item["name"] == "Dry-Erase Markers"
    assert [item["name"] for item in sample_inventory] == [
        "Laptop Charger",
        "Phone Charger",
        "Printer Paper",
        "Sticky Notes",
    ]


@pytest.mark.parametrize(
    "item_number",
    [0, -1, 6],
    ids=["zero", "negative", "larger-than-inventory"],
)
def test_remove_rejects_invalid_item_number(sample_inventory, item_number):
    # Arrange
    original_inventory = [item.copy() for item in sample_inventory]

    # Act
    removed_item = remove_item_by_number(sample_inventory, item_number)

    # Assert
    assert removed_item is None
    assert sample_inventory == original_inventory


# ---------------------------------------------------------------------------
# 5. Update quantity
# ---------------------------------------------------------------------------


def test_update_item_quantity_changes_quantity(sample_inventory):
    # Arrange
    item_number = 2

    # Act
    result = update_item_quantity(sample_inventory, item_number, 12)

    # Assert
    assert result is True
    assert sample_inventory[1]["quantity"] == 12


def test_update_item_quantity_accepts_zero(sample_inventory):
    # Arrange
    item_number = 1

    # Act
    result = update_item_quantity(sample_inventory, item_number, 0)

    # Assert
    assert result is True
    assert sample_inventory[0]["quantity"] == 0


def test_update_item_quantity_leaves_other_items_unchanged(sample_inventory):
    # Arrange
    expected_inventory = [item.copy() for item in sample_inventory]
    expected_inventory[3]["quantity"] = 40

    # Act
    update_item_quantity(sample_inventory, 4, 40)

    # Assert
    assert sample_inventory == expected_inventory


@pytest.mark.parametrize(
    "item_number",
    [0, -3, 6],
    ids=["zero", "negative", "larger-than-inventory"],
)
def test_update_item_quantity_rejects_invalid_item_number(
    sample_inventory, item_number
):
    # Arrange
    original_inventory = [item.copy() for item in sample_inventory]

    # Act
    result = update_item_quantity(sample_inventory, item_number, 10)

    # Assert
    assert result is False
    assert sample_inventory == original_inventory


def test_update_item_quantity_rejects_negative_quantity(sample_inventory):
    # Arrange
    original_inventory = [item.copy() for item in sample_inventory]

    # Act
    result = update_item_quantity(sample_inventory, 1, -2)

    # Assert
    assert result is False
    assert sample_inventory == original_inventory


# ---------------------------------------------------------------------------
# 6. Add-item validation
# ---------------------------------------------------------------------------


def test_validate_new_item_accepts_valid_item(sample_inventory):
    # Arrange
    name, category, quantity = "HDMI Cable", "Electronics", 6

    # Act
    error = validate_new_item(sample_inventory, name, category, quantity)

    # Assert
    assert error is None


@pytest.mark.parametrize(
    "name, category, quantity, expected_error",
    [
        ("", "Electronics", 6, "Item name cannot be empty."),
        ("   ", "Electronics", 6, "Item name cannot be empty."),
        ("HDMI Cable", "", 6, "Category cannot be empty."),
        ("HDMI|Cable", "Electronics", 6, "Item name may not contain the | character."),
        ("HDMI Cable", "Elec|tronics", 6, "Category may not contain the | character."),
        ("HDMI Cable", "Electronics", -2, "Quantity must be a nonnegative whole number."),
        ("HDMI Cable", "Electronics", None, "Quantity must be a nonnegative whole number."),
        ("Laptop Charger", "Electronics", 6, "An item with that name already exists."),
        ("laptop CHARGER", "Electronics", 6, "An item with that name already exists."),
    ],
    ids=[
        "empty-name",
        "whitespace-only-name",
        "empty-category",
        "pipe-in-name",
        "pipe-in-category",
        "negative-quantity",
        "nonnumeric-quantity",
        "duplicate-name",
        "duplicate-name-different-capitalization",
    ],
)
def test_validate_new_item_rejects_invalid_item(
    sample_inventory, name, category, quantity, expected_error
):
    # Arrange: sample_inventory fixture and parameterized item values

    # Act
    error = validate_new_item(sample_inventory, name, category, quantity)

    # Assert
    assert error == expected_error


@pytest.mark.parametrize(
    "quantity_text, expected",
    [
        ("12", 12),
        ("0", 0),
        (" 7 ", 7),
        ("-2", -2),
        ("six", None),
        ("3.5", None),
        ("", None),
    ],
    ids=[
        "whole-number",
        "zero",
        "surrounding-spaces",
        "negative-number",
        "word",
        "decimal",
        "empty",
    ],
)
def test_parse_quantity_converts_only_whole_numbers(quantity_text, expected):
    # Arrange: parameterized quantity text

    # Act
    result = parse_quantity(quantity_text)

    # Assert
    assert result == expected


# ---------------------------------------------------------------------------
# 7. Inventory summary
# ---------------------------------------------------------------------------


def test_summary_counts_unique_items(sample_inventory):
    # Arrange: sample_inventory fixture has 5 items

    # Act
    summary = calculate_summary(sample_inventory)

    # Assert
    assert summary["unique_items"] == 5


def test_summary_totals_quantity_across_all_items(sample_inventory):
    # Arrange: quantities are 8 + 5 + 25 + 4 + 3

    # Act
    summary = calculate_summary(sample_inventory)

    # Assert
    assert summary["total_quantity"] == 45


def test_summary_counts_low_stock_items(sample_inventory):
    # Arrange: Sticky Notes (4) and Dry-Erase Markers (3) are below 5

    # Act
    summary = calculate_summary(sample_inventory)

    # Assert
    assert summary["low_stock_items"] == 2


def test_summary_counts_items_by_category(sample_inventory):
    # Arrange: sample_inventory fixture

    # Act
    summary = calculate_summary(sample_inventory)

    # Assert
    assert summary["category_counts"] == {
        "Electronics": 2,
        "Office Supplies": 2,
        "Classroom Supplies": 1,
    }


def test_summary_category_counts_ignore_capitalization():
    # Arrange
    inventory = [
        {"name": "HDMI Cable", "category": "Electronics", "quantity": 6},
        {"name": "Mouse", "category": "electronics", "quantity": 9},
        {"name": "Keyboard", "category": "ELECTRONICS", "quantity": 7},
        {"name": "Pens", "category": "Office Supplies", "quantity": 20},
    ]

    # Act
    summary = calculate_summary(inventory)

    # Assert
    assert summary["category_counts"] == {"Electronics": 3, "Office Supplies": 1}


def test_summary_of_empty_inventory_is_all_zero():
    # Arrange
    inventory = []

    # Act
    summary = calculate_summary(inventory)

    # Assert
    assert summary == {
        "unique_items": 0,
        "total_quantity": 0,
        "low_stock_items": 0,
        "category_counts": {},
    }


@pytest.mark.parametrize(
    "quantity, expected_low_stock_count",
    [
        (0, 1),
        (4, 1),
        (5, 0),
        (6, 0),
    ],
    ids=["zero-is-low", "four-is-low", "five-is-not-low", "six-is-not-low"],
)
def test_summary_low_stock_boundary(quantity, expected_low_stock_count):
    # Arrange
    inventory = [{"name": "Test Item", "category": "Testing", "quantity": quantity}]

    # Act
    summary = calculate_summary(inventory)

    # Assert
    assert summary["low_stock_items"] == expected_low_stock_count
