"""CPS 310 - Homework 1: Inventory Manager
Instructor solution checkpoint.
"""

INVENTORY_FILE = "inventory.txt"
LOW_STOCK_THRESHOLD = 5


def display_menu():
    """Display the main Inventory Manager menu."""
    print("\nInventory Manager")
    print("1. View inventory")
    print("2. Add an item")
    print("3. Update an item quantity")
    print("4. Remove an item")
    print("5. Search inventory")
    print("6. View inventory summary")
    print("7. Exit")


def load_inventory(filename):
    """Load inventory records from a pipe-delimited text file."""
    inventory = []

    try:
        with open(filename, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue

                name, category, quantity = line.split("|")
                inventory.append(
                    {
                        "name": name,
                        "category": category,
                        "quantity": int(quantity),
                    }
                )
    except FileNotFoundError:
        return []

    return inventory


def save_inventory(inventory, filename):
    """Save the complete inventory to a pipe-delimited text file."""
    with open(filename, "w", encoding="utf-8") as file:
        for item in inventory:
            file.write(
                f'{item["name"]}|{item["category"]}|{item["quantity"]}\n'
            )


def view_inventory(inventory):
    """Display all inventory items in a numbered list."""
    if not inventory:
        print("No inventory items found.")
        return

    print("\nInventory:")
    for index, item in enumerate(inventory, start=1):
        print(
            f'{index}. {item["name"]} | {item["category"]} | '
            f'Quantity: {item["quantity"]}'
        )


def parse_quantity(quantity_text):
    """Convert quantity text to an int, or return None if it is not a whole number.

    Negative numbers such as "-2" are converted; validate_quantity rejects them.
    """
    quantity_text = quantity_text.strip()
    try:
        return int(quantity_text)
    except ValueError:
        return None


def validate_item_name(inventory, name):
    """Return an error message for an invalid new item name, or None if valid."""
    name = name.strip()
    if not name:
        return "Item name cannot be empty."
    if "|" in name:
        return "Item name may not contain the | character."
    for item in inventory:
        if item["name"].lower() == name.lower():
            return "An item with that name already exists."
    return None


def validate_category(category):
    """Return an error message for an invalid category, or None if valid."""
    category = category.strip()
    if not category:
        return "Category cannot be empty."
    if "|" in category:
        return "Category may not contain the | character."
    return None


def validate_quantity(quantity):
    """Return an error message for an invalid quantity, or None if valid."""
    if quantity is None or quantity < 0:
        return "Quantity must be a nonnegative whole number."
    return None


def validate_new_item(inventory, name, category, quantity):
    """Return the first validation error for a new item, or None if it is valid."""
    return (
        validate_item_name(inventory, name)
        or validate_category(category)
        or validate_quantity(quantity)
    )


def add_item(inventory):
    """Prompt for and add one validated inventory item, then save it."""
    name = input("Enter the item name: ").strip()
    error = validate_item_name(inventory, name)
    if error:
        print(error)
        return

    category = input("Enter the category: ").strip()
    error = validate_category(category)
    if error:
        print(error)
        return

    quantity = parse_quantity(input("Enter the quantity: "))
    error = validate_quantity(quantity)
    if error:
        print(error)
        return

    inventory.append({"name": name, "category": category, "quantity": quantity})
    save_inventory(inventory, INVENTORY_FILE)
    print("Item added successfully.")


def is_valid_item_number(inventory, item_number):
    """Return True if item_number is a valid 1-based position in inventory."""
    return 1 <= item_number <= len(inventory)


def update_item_quantity(inventory, item_number, new_quantity):
    """Set the quantity of the item at 1-based item_number.

    Returns True on success. Returns False, leaving the inventory unchanged,
    if the item number is out of range or the quantity is negative.
    """
    if not is_valid_item_number(inventory, item_number):
        return False
    if new_quantity < 0:
        return False

    inventory[item_number - 1]["quantity"] = new_quantity
    return True


def remove_item_by_number(inventory, item_number):
    """Remove and return the item at 1-based item_number.

    Returns None, leaving the inventory unchanged, if the number is invalid.
    """
    if not is_valid_item_number(inventory, item_number):
        return None
    return inventory.pop(item_number - 1)


def update_quantity(inventory):
    """Prompt for an item number and replace its quantity, then save it."""
    if not inventory:
        print("No inventory items found.")
        return

    view_inventory(inventory)
    selection_text = input("Enter the item number to update: ").strip()
    if not selection_text.isdigit():
        print("Item number must be a valid whole number.")
        return

    selection = int(selection_text)
    if not is_valid_item_number(inventory, selection):
        print("Item number is outside the available range.")
        return

    quantity_text = input("Enter the new quantity: ").strip()
    if not quantity_text.isdigit():
        print("Quantity must be a nonnegative whole number.")
        return

    quantity = int(quantity_text)
    update_item_quantity(inventory, selection, quantity)
    item = inventory[selection - 1]
    save_inventory(inventory, INVENTORY_FILE)
    print(f'{item["name"]} quantity updated to {quantity}.')


def remove_item(inventory):
    """Prompt for an item number, remove that item, then save the inventory."""
    if not inventory:
        print("No inventory items found.")
        return

    view_inventory(inventory)
    selection_text = input("Enter the item number to remove: ").strip()
    if not selection_text.isdigit():
        print("Item number must be a valid whole number.")
        return

    removed_item = remove_item_by_number(inventory, int(selection_text))
    if removed_item is None:
        print("Item number is outside the available range.")
        return

    save_inventory(inventory, INVENTORY_FILE)
    print(f'Item removed: {removed_item["name"]}')


def find_matching_items(inventory, search_term):
    """Return items whose names contain search_term, ignoring capitalization.

    An empty or whitespace-only search term matches nothing and returns [].
    """
    search_term = search_term.strip().lower()
    if not search_term:
        return []

    matches = []
    for item in inventory:
        if search_term in item["name"].lower():
            matches.append(item)
    return matches


def search_inventory(inventory):
    """Prompt for an item-name search term and display matching items."""
    search_term = input("Enter part or all of an item name: ").strip()
    if not search_term:
        print("Search term cannot be empty.")
        return

    matches = find_matching_items(inventory, search_term)

    if not matches:
        print("No inventory items matched your search.")
        return

    print("\nSearch Results:")
    for index, item in enumerate(matches, start=1):
        print(
            f'{index}. {item["name"]} | {item["category"]} | '
            f'Quantity: {item["quantity"]}'
        )


def is_low_stock(quantity):
    """Return True if quantity is below the low-stock threshold."""
    return quantity < LOW_STOCK_THRESHOLD


def calculate_summary(inventory):
    """Calculate summary values for the inventory.

    Returns a dictionary with unique_items, total_quantity, low_stock_items,
    and category_counts. Category counts ignore capitalization and are keyed
    by the first spelling of each category that appears in the inventory.
    """
    total_quantity = 0
    low_stock_items = 0
    category_counts = {}
    category_labels = {}

    for item in inventory:
        total_quantity += item["quantity"]

        if is_low_stock(item["quantity"]):
            low_stock_items += 1

        category_key = item["category"].lower()
        if category_key not in category_labels:
            category_labels[category_key] = item["category"]
        label = category_labels[category_key]
        category_counts[label] = category_counts.get(label, 0) + 1

    return {
        "unique_items": len(inventory),
        "total_quantity": total_quantity,
        "low_stock_items": low_stock_items,
        "category_counts": category_counts,
    }


def display_summary(inventory):
    """Display inventory summary information."""
    summary = calculate_summary(inventory)

    print("\nInventory Summary")
    print(f'Unique items: {summary["unique_items"]}')
    print(f'Total quantity: {summary["total_quantity"]}')
    print(f'Low-stock items: {summary["low_stock_items"]}')
    print("\nItems by category:")

    if not summary["category_counts"]:
        print("No categories found.")
        return

    for category, count in summary["category_counts"].items():
        print(f"{category}: {count}")


def main():
    """Run the Inventory Manager menu loop."""
    inventory = load_inventory(INVENTORY_FILE)

    while True:
        display_menu()
        choice = input("Choose an option (1-7): ").strip()

        if choice == "1":
            view_inventory(inventory)
        elif choice == "2":
            add_item(inventory)
        elif choice == "3":
            update_quantity(inventory)
        elif choice == "4":
            remove_item(inventory)
        elif choice == "5":
            search_inventory(inventory)
        elif choice == "6":
            display_summary(inventory)
        elif choice == "7":
            print("Goodbye!")
            break
        else:
            print("Please enter a menu option from 1 through 7.")


if __name__ == "__main__":
    main()
