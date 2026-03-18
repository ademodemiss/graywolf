# Shell Policy Enhancements - Test Cases and Documentation

## Current Policy:
- Basic command categorization (allowed, risky, forbidden).
- Checks for chained commands (`&&`, `||`, `;`, `|`).

## Identified Gaps & Areas for Enhancement:
1.  **Argument Validation:** The current policy does not inspect command arguments, which can be a security risk (e.g., allowing `rm -rf /` with `ALLOW` decision).
2.  **Explicit Confirmation:** Confirmation for risky commands is implicit (via chained command detection). An explicit confirmation mechanism (user prompt or flag) is missing.
3.  **Policy Configurability:** Policy rules are hardcoded. Loading from external files (JSON/YAML) would improve flexibility.
4.  **Test Coverage:** Insufficient test cases for edge scenarios, argument validation, and complex command structures.

## Proposed Improvements & Actions:
1.  **Implement Argument Validation:** Add logic to parse and validate command arguments against predefined schemas or rules.
2.  **Introduce Explicit Confirmation:** For risky commands, add a mechanism for explicit user confirmation (e.g., `--force` flag or interactive prompt).
3.  **External Policy Configuration:** Load policy rules from configurable files (e.g., JSON, YAML) for easier management.
4.  **Develop Comprehensive Tests:** Create tests for:
    *   Various command structures and argument patterns.
    *   Edge cases for policy decisions.
    *   Chained command scenarios.
    *   Argument validation logic (once implemented).

## Future Considerations:
- Dynamic policy updates.
- Whitelisting specific command patterns.
