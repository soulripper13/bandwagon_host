# v1.0.0 - Initial release

The first public release of Bandwagon Host VPS for Home Assistant.

## Integration

- UI-based setup using a KiwiVM VEID and API key.
- Start/Stop, Reboot, and Force Stop controls.
- Configurable polling interval with KiwiVM API-budget monitoring.
- Home Assistant device and entity registration for the configured VPS.

## Monitoring

- VPS status, RAM, disk, swap, load, and monthly bandwidth usage.
- Bandwidth limit, remaining transfer, accounting multiplier, and reset date.
- Public and private addresses, SSH port, reverse DNS, MAC address, and IPv6 details.
- Hostname, operating system, hypervisor, plan, node, datacenter, disk quota, and mounted ISO.
- Suspension, policy violation, IP nullroute, CPU throttling, and disk throttling diagnostics.
- API rate-limit budgets, abuse points, and available platform capabilities.

## Dashboard card

- Bundled `custom:bandwagon-host-card` with automatic resource registration.
- Circular RAM and disk gauges and a monthly bandwidth progress bar.
- Server details and critical problem warnings.
- Start/Stop, Reboot, and Force Stop actions with confirmation dialogs.
- Visual controls for title, subtitle, colors, gauge dimensions, padding, visible sections, and entity overrides.
- Responsive layouts for mobile and desktop dashboards.

## Installation notes

Install through HACS or copy `custom_components/bandwagon_host` manually, then restart Home Assistant. If the bundled card does not appear after installation, hard-refresh the browser and verify `/bandwagon_host/bandwagon-host-card.js` is registered as a JavaScript module.
