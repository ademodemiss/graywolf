# Shell Policy Enhancements - Test Cases

## Test Scenarios for ShellPolicy:

1.  **Argument Validation Tests:**
    -   Test commands with known safe arguments.
    -   Test commands with known unsafe arguments (e.g., `rm -rf /`, `mkfs.ext4 /dev/sda1`).
    -   Test commands with arguments that bypass policy checks (e.g., using environment variables, complex shell expansions).
    -   Test commands with arguments that are valid for the base command but disallowed by policy.

2.  **Chained Command Tests:**
    -   Test commands with `&&`, `||`, `;`, `|` operators.
    -   Ensure chained commands are correctly identified as requiring confirmation.

3.  **Risky Command Confirmation:**
    -   Test risky commands with and without confirmation flags (if implemented).

4.  **Configurable Policy Loading:**
    -   Test loading policies from different file formats (JSON, YAML) if supported.
    -   Test policy updates without agent restart.

5.  **Edge Cases:
    *   Empty commands.
    *   Commands with unusual characters.
    *   Commands exceeding length limits (if any).

## Testing Framework Integration:
Consider integrating these tests with a standard Python testing framework like `pytest`.
