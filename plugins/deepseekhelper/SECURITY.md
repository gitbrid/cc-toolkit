# Security Policy

## Supported Versions

Security fixes target the latest version on the default branch.

## Reporting a Vulnerability

Do not disclose suspected vulnerabilities in public issues.

Use GitHub private vulnerability reporting if it is enabled for the repository. If it is not enabled, open a minimal public issue that asks the maintainer to enable private reporting, without including exploit details or secrets.

## Secrets

Never commit `DEEPSEEK_API_KEY`, `.env`, usage logs, model cache files, or other local state. DeepSeekHelper reads credentials from the process environment, or from `launchctl` on macOS as a fallback.
