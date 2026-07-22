# Bandwagon Host VPS

Monitor and control a Bandwagon Host VPS from Home Assistant through the KiwiVM API.

## Highlights

- Tracks status, RAM, disk, swap, load, bandwidth, addresses, SSH, and server metadata.
- Reports suspension, policy, nullroute, and throttling problems.
- Provides Start/Stop, Reboot, and Force Stop controls.
- Reports API rate-limit budgets and platform capabilities.
- Includes a responsive, visually configurable dashboard card.

## Setup

After installing and restarting Home Assistant, open **Settings > Devices & services > Add integration**, search for **Bandwagon Host VPS**, and enter the VEID and API key shown on the KiwiVM API page.

Treat the API key as a password. Never include it in screenshots, logs, or issue reports.

See the repository README for installation, card configuration, troubleshooting, and release information.
