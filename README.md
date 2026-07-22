# Bandwagon Host VPS for Home Assistant

[![HACS validation](https://github.com/soulripper13/bandwagon_host/actions/workflows/hacs.yaml/badge.svg)](https://github.com/soulripper13/bandwagon_host/actions/workflows/hacs.yaml)
[![Hassfest](https://github.com/soulripper13/bandwagon_host/actions/workflows/hassfest.yaml/badge.svg)](https://github.com/soulripper13/bandwagon_host/actions/workflows/hassfest.yaml)
[![GitHub release](https://img.shields.io/github/v/release/soulripper13/bandwagon_host)](https://github.com/soulripper13/bandwagon_host/releases)
[![License](https://img.shields.io/github/license/soulripper13/bandwagon_host)](LICENSE)
[![GitHub issues](https://img.shields.io/github/issues/soulripper13/bandwagon_host)](https://github.com/soulripper13/bandwagon_host/issues)

A Home Assistant custom integration for monitoring and controlling Bandwagon Host VPS instances through the KiwiVM REST API.

[![Open in HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=soulripper13&repository=bandwagon_host&category=integration)
[![Add integration](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=bandwagon_host)

## Features

- Starts, stops, reboots, and force-stops a VPS.
- Tracks RAM, disk, swap, load, and monthly bandwidth data.
- Tracks bandwidth allowance, remaining transfer, accounting multiplier, and reset date.
- Tracks public and private addresses, SSH port, reverse DNS, MAC address, and IPv6 details.
- Reports hostname, operating system, hypervisor, plan, node, datacenter, mounted ISO, and disk quota.
- Reports suspension, policy violation, nullroute, CPU throttling, and disk throttling problems.
- Reports API rate-limit budgets and available platform capabilities.
- Includes a responsive dashboard card with a visual editor.

## Installation

### HACS

Until the repository is accepted into the HACS default list, add it as a custom repository:

1. Open HACS.
2. Open the menu and select **Custom repositories**.
3. Add `https://github.com/soulripper13/bandwagon_host` with category **Integration**.
4. Search for **Bandwagon Host VPS Control** and select **Download**.
5. Restart Home Assistant.

After default-list acceptance, the custom-repository step is no longer required.

### Manual

Copy `custom_components/bandwagon_host` into the `custom_components` directory in your Home Assistant configuration, then restart Home Assistant.

## Configuration

1. Open the KiwiVM control panel for the VPS.
2. Open its API page and obtain the VEID and API key.
3. In Home Assistant, open **Settings > Devices & services > Add integration**.
4. Search for **Bandwagon Host VPS** and enter the credentials.

The options flow controls the polling interval. The minimum is 30 seconds and the default is 60 seconds. Increase the interval if the API-budget sensors show that the account is approaching its KiwiVM limits.

The API key is sent only to the KiwiVM API, but it grants control over the VPS. Store it securely and never include it in documentation, screenshots, logs, or issue reports.

## Entities

| Type | Entities |
| --- | --- |
| Controls | Power switch, Restart button, Force Stop button |
| Utilization | RAM, disk, swap, load |
| Transfer | Used, limit, remaining, percentage, multiplier, reset date |
| Network | Addresses, SSH port, reverse DNS, MAC, private addresses, IPv6 data |
| Server | Status, plan, hostname, OS, hypervisor, node, datacenter, mounted ISO |
| Problems | Suspended, policy violation, nullroute, CPU throttled, disk throttled |
| Diagnostics | API budgets, abuse points, disk quota, platform capabilities |

Diagnostic entities may be disabled by default. Enable them from the integration's device or entity page when needed.

## Dashboard card

The bundled `custom:bandwagon-host-card` is registered automatically. If automatic registration is unavailable, add `/bandwagon_host/bandwagon-host-card.js` as a JavaScript module under **Settings > Dashboards > Resources**.

Add the card through the dashboard card picker and use its visual editor, or configure it in YAML:

```yaml
type: custom:bandwagon-host-card
veid: "1234567"
title: Production VPS
subtitle: Los Angeles
accent_color: "#ffb000"
background_color: "#1c1c1e"
gauge_size: 96
gauge_thickness: 5
card_padding: 16
show_ram: true
show_disk: true
show_bandwidth: true
show_details: true
show_actions: true
```

The editor also provides individual detail/action visibility switches and entity overrides for renamed or replacement entities.

## Troubleshooting

### Setup or authentication fails

Copy the VEID and API key again from the KiwiVM API page. Confirm there are no spaces before or after either value.

### Updates fail intermittently

Inspect the remaining API-budget entities and increase the polling interval. KiwiVM can reject requests when its short-term or daily limits are exhausted.

### The dashboard card is missing or outdated

Restart Home Assistant after upgrading. Confirm `/bandwagon_host/bandwagon-host-card.js` is registered as a JavaScript module, then hard-refresh the browser.

### Debug logging

```yaml
logger:
  default: info
  logs:
    custom_components.bandwagon_host: debug
```

Remove the API key, VEID, addresses, and hostnames before sharing logs.

## Releases

Install tagged GitHub releases rather than development snapshots. Release highlights and upgrade notes are maintained in [RELEASE_NOTES.md](RELEASE_NOTES.md).

## Support

Report reproducible bugs through [GitHub Issues](https://github.com/soulripper13/bandwagon_host/issues). Include the Home Assistant version, integration version, relevant sanitized logs, and reproduction steps.

## License and trademarks

This project is licensed under the [MIT License](LICENSE). Bandwagon Host and KiwiVM are trademarks of their respective owners. This community integration is not affiliated with or endorsed by Bandwagon Host.
