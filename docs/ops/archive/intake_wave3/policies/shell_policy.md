# Shell Policy Enhancements

## Current Policy:
- Basic command categorization (allowed, risky, forbidden).
- Checks for chained commands (`&&`, `||`, `;`, `|`).

## Identified Gaps:
- Command argument validation is missing. Policies do not inspect arguments passed to commands.
- Risky commands are confirmed, but the confirmation process is implicit.
- Allowed commands list is hardcoded and could be made configurable.

## Proposed Improvements:
1.  **Argument Validation:** Implement logic to check command arguments against predefined patterns or rules (e.g., disallow specific dangerous arguments like `rm -rf /`).
2.  **Explicit Confirmation Workflow:** Make confirmation explicit (e.g., prompting the user or requiring a specific flag like `--force`) rather than implicit confirmation through chained command detection.
3.  **Configurable Policies:** Load `allowed_commands`, `risky_commands`, `forbidden_commands` from a configuration file (e.g., JSON or YAML) to allow easier customization and policy management.
4.  **Enhanced Test Cases:** Add more comprehensive test cases for edge scenarios, including various command structures, arguments, and policy decision outcomes.

## Future Considerations:
- Whitelisting specific command patterns instead of just base commands.
- Dynamic policy updates without agent restart.
