# GrayWolf Deployment Documentation

## `autonomous_deployer.py`:

This script is intended to automate the deployment process of the GrayWolf agent. It likely handles tasks such as:

-   Setting up the environment on the target VPS.
-   Configuring necessary services (e.g., `graywolf.service` using systemd).
-   Deploying the agent code and dependencies.
-   Managing configurations (e.g., `.env` files).
-   Performing initial health checks post-deployment.

## Usage:
To understand the exact usage and options, please refer to the script's internal help:
```bash
python3 deployment/autonomous_deployer.py --help
```

## Current Status:

The script exists, but its detailed functionality and deployment steps are not fully documented within the code itself. Further investigation or adding inline comments and a comprehensive README would be beneficial.

## Recommendation:
-   Add detailed inline comments within `autonomous_deployer.py`.
-   Create a more comprehensive README file in the `deployment/` directory explaining the deployment process, prerequisites, and configuration options.
