# AI Usage

## Homework 2 — Automated Unit Testing

### Tool used

Claude Code running in VS Code with access to this project folder.

### How AI assisted

- **Planning:** I gave Claude the assignment page. It read the instructions and `inventory_manager.py`, then gave me a step-by-step plan that matched each part of the assignment to the code.
- **Refactoring (Part C):** Claude moved the logic out of the interactive functions into helper functions that take parameters and return results, with no `input()`, `print()` or file saving:
  - `find_matching_items`
  - `is_valid_item_number`
  - `remove_item_by_number`
  - `update_item_quantity`
  - `parse_quantity`
  - `validate_item_name`
  - `validate_category`
  - `validate_quantity`
  - `validate_new_item`
  - `is_low_stock`
  - `calculate_summary`

  The menu functions now call these helpers, and only the menu functions save to `inventory.txt`.
- **Writing the test suite (Parts D and E):** Claude wrote `test_inventory_manager.py`:
  - 54 collected tests
  - a `sample_inventory` fixture
  - six parameterized test functions with readable `ids`
  - six `tmp_path` file tests
  - Arrange/Act/Assert comments in every test
- **Commits:** Claude made the refactoring and testing commits on `feature/automated-testing`, one per feature. Each commit includes a `Co-Authored-By: Claude` line.

### Example prompts

- "Can you guide me through how to complete this assignment?" (with a link to the Homework 2 instructions)
- "Can you give specific plans for steps 1 and 2?
- "Can you make a template for the format and example paragraphs for AI_USAGE.md?"

### Suggestions accepted

- Return values instead of printing:
  - `None` or an error message from the validators
  - `True`/`False` from `update_item_quantity`
  - `None` from `remove_item_by_number` when the item number is invalid
- Keeping `save_inventory(..., INVENTORY_FILE)` out of the helper functions, so tests can never overwrite the real `inventory.txt`.
- Treating an empty or whitespace-only search term as "no matches" (`[]`).
- Rejecting negative quantities with an explicit `quantity < 0` check. Before, `-2` was only rejected because `isdigit()` fails on the minus sign.
- Testing the low-stock boundary with the quantities 0, 4, 5 and 6.

### How I verified the code and tests

- Ran the full regression suite with `python -m pytest -v`. All 54 tests passed.
- Ran `python inventory_manager.py` and tried every menu option: view, add (including a duplicate name and a negative quantity), update (including an invalid item number), remove, search, summary and exit. All of them behaved like the Homework 1 manual tests in `TESTING.md`.
- Checked with `git status` and `git diff` that the real `inventory.txt` was not changed by the tests.

I understand and take responsibility for every program change and every test in this submission.
