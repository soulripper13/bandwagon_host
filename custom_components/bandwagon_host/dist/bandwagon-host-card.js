class BandwagonHostCard extends HTMLElement {
  // Set the hass object and render the card
  set hass(hass) {
    this._hass = hass;
    if (!this.content) {
      const shadow = this.attachShadow({ mode: 'open' });
      shadow.innerHTML = `
        <style>
          :host {
            --card-padding: 16px;
            --gauge-size: 96px;
            --gauge-border: 5px;
            --primary-accent: var(--bandwagon-accent, var(--primary-color, #03a9f4));
            --success-color: #4caf50;
            --warning-color: #ff9800;
            --danger-color: #f44336;
            display: block;
            container-type: inline-size;
          }

          ha-card {
            overflow: hidden;
            padding: var(--card-padding);
            background: var(--bandwagon-background, var(--card-background-color, #1c1c1e));
            border-radius: var(--ha-card-border-radius, 12px);
            border: var(--ha-card-border-width, 1px) solid var(--ha-card-border-color, var(--divider-color, #2c2c2e));
            box-shadow: var(--ha-card-box-shadow, none);
            color: var(--primary-text-color, #ffffff);
            font-family: var(--paper-font-body1_-_font-family, inherit);
            position: relative;
          }

          .header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 20px;
          }

          .title-container {
            display: flex;
            flex-direction: column;
            min-width: 0;
          }

          .title {
            font-size: 1.25rem;
            font-weight: bold;
            color: var(--primary-text-color);
            overflow-wrap: anywhere;
          }

          .subtitle {
            font-size: 0.85rem;
            color: var(--secondary-text-color, #8e8e93);
            margin-top: 2px;
          }

          .status-badge {
            display: flex;
            align-items: center;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 500;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            flex: 0 0 auto;
            margin-left: 12px;
          }

          .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            margin-right: 6px;
            background: var(--secondary-text-color);
          }

          .status-badge.running .status-dot {
            background: var(--success-color);
            box-shadow: 0 0 8px var(--success-color);
            animation: pulse 2s infinite;
          }

          .status-badge.stopped .status-dot {
            background: var(--danger-color);
          }

          .status-badge.starting .status-dot {
            background: var(--warning-color);
            animation: pulse 1s infinite;
          }

          @keyframes pulse {
            0% { transform: scale(0.95); opacity: 0.5; }
            50% { transform: scale(1.1); opacity: 1; }
            100% { transform: scale(0.95); opacity: 0.5; }
          }

          .gauges-container {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            align-items: start;
            gap: 16px;
            margin-bottom: 20px;
          }

          .gauge-wrapper {
            display: flex;
            flex-direction: column;
            align-items: center;
            min-width: 0;
          }

          .gauge {
            position: relative;
            width: min(var(--gauge-size), 100%);
            aspect-ratio: 1;
            flex: 0 0 auto;
          }

          .gauge svg {
            width: 100%;
            height: 100%;
            transform: rotate(-90deg);
          }

          .gauge circle {
            fill: none;
            stroke-width: var(--gauge-border);
          }

          .gauge .track {
            stroke: rgba(255, 255, 255, 0.05);
          }

          .gauge .fill {
            stroke: var(--primary-accent);
            stroke-linecap: round;
            transition: stroke-dashoffset 0.6s ease;
          }

          .gauge .value {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 1.1rem;
            font-weight: bold;
          }

          .gauge-label {
            margin-top: 8px;
            font-size: 0.85rem;
            color: var(--secondary-text-color);
            font-weight: 500;
            text-align: center;
            overflow-wrap: anywhere;
          }

          .bandwidth-section {
            margin-bottom: 20px;
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 8px;
            padding: 12px;
          }

          .bandwidth-header {
            display: flex;
            justify-content: space-between;
            font-size: 0.85rem;
            margin-bottom: 6px;
            color: var(--secondary-text-color);
          }

          .bandwidth-header span:first-child {
            font-weight: 500;
            color: var(--primary-text-color);
          }

          .progress-bar-container {
            width: 100%;
            height: 8px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 4px;
            overflow: hidden;
          }

          .progress-bar {
            height: 100%;
            background: linear-gradient(90deg, var(--primary-accent), #00bcd4);
            border-radius: 4px;
            transition: width 0.6s ease;
          }

          .bandwidth-meta {
            display: flex;
            justify-content: space-between;
            gap: 12px;
            margin-top: 8px;
            color: var(--secondary-text-color);
            font-size: 0.75rem;
          }

          .grid-info {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 12px;
            margin-bottom: 20px;
          }

          .info-item {
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 8px;
            padding: 10px;
            display: flex;
            flex-direction: column;
          }

          .info-label {
            font-size: 0.75rem;
            color: var(--secondary-text-color);
            margin-bottom: 4px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
          }

          .info-value {
            font-size: 0.9rem;
            font-weight: 500;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
          }

          .warning-badge {
            background: rgba(255, 152, 0, 0.15);
            color: var(--warning-color);
            border: 1px solid rgba(255, 152, 0, 0.3);
            border-radius: 6px;
            padding: 8px;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            font-size: 0.8rem;
            font-weight: 500;
          }

          .warning-badge.critical {
            background: rgba(244, 67, 54, 0.15);
            color: var(--danger-color);
            border-color: rgba(244, 67, 54, 0.35);
          }

          .warning-badge ha-icon {
            --mdc-icon-size: 16px;
            margin-right: 6px;
          }

          .actions {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
          }

          .action-btn {
            flex: 1 1 92px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
            padding: 10px;
            border-radius: 8px;
            border: none;
            background: rgba(255, 255, 255, 0.05);
            color: var(--primary-text-color);
            font-weight: 500;
            font-size: 0.85rem;
            cursor: pointer;
            transition: all 0.2s ease;
            border: 1px solid rgba(255, 255, 255, 0.08);
          }

          .action-btn:hover:not(:disabled) {
            background: rgba(255, 255, 255, 0.1);
            border-color: rgba(255, 255, 255, 0.15);
          }

          .action-btn.btn-power.on {
            background: rgba(244, 67, 54, 0.15);
            color: var(--danger-color);
            border: 1px solid rgba(244, 67, 54, 0.3);
          }

          .action-btn.btn-power.on:hover {
            background: rgba(244, 67, 54, 0.25);
          }

          .action-btn.btn-power.off {
            background: rgba(76, 175, 80, 0.15);
            color: var(--success-color);
            border: 1px solid rgba(76, 175, 80, 0.3);
          }

          .action-btn.btn-power.off:hover {
            background: rgba(76, 175, 80, 0.25);
          }

          .action-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
          }

          @container (max-width: 260px) {
            .header {
              align-items: flex-start;
              gap: 8px;
            }

            .status-badge {
              margin-left: 0;
            }

            .gauges-container,
            .grid-info {
              grid-template-columns: 1fr;
            }
          }
        </style>
        <ha-card>
          <div class="card-content">
            <div class="header">
              <div class="title-container">
                <div class="title" id="card-title">Bandwagon Host VPS</div>
                <div class="subtitle" id="card-subtitle">Connecting...</div>
              </div>
              <div class="status-badge" id="status-badge">
                <span class="status-dot"></span>
                <span id="status-text">Offline</span>
              </div>
            </div>

            <div class="gauges-container" id="gauges-container">
              <div class="gauge-wrapper" id="ram-gauge-wrapper">
                <div class="gauge">
                  <svg viewBox="-2 -2 40 40" aria-hidden="true">
                    <circle class="track" cx="18" cy="18" r="15.915"></circle>
                    <circle class="fill" id="ram-fill" cx="18" cy="18" r="15.915" stroke-dasharray="0, 100"></circle>
                  </svg>
                  <div class="value" id="ram-val">0%</div>
                </div>
                <div class="gauge-label">RAM Usage</div>
              </div>

              <div class="gauge-wrapper" id="disk-gauge-wrapper">
                <div class="gauge">
                  <svg viewBox="-2 -2 40 40" aria-hidden="true">
                    <circle class="track" cx="18" cy="18" r="15.915"></circle>
                    <circle class="fill" id="disk-fill" cx="18" cy="18" r="15.915" stroke-dasharray="0, 100"></circle>
                  </svg>
                  <div class="value" id="disk-val">0%</div>
                </div>
                <div class="gauge-label">Disk Usage</div>
              </div>
            </div>

            <div class="bandwidth-section" id="bandwidth-section">
              <div class="bandwidth-header">
                <span>Bandwidth</span>
                <span id="bandwidth-text">0 / 0 GB (0%)</span>
              </div>
              <div class="progress-bar-container">
                <div class="progress-bar" id="bandwidth-bar" style="width: 0%"></div>
              </div>
              <div class="bandwidth-meta">
                <span id="bandwidth-remaining"></span>
                <span id="bandwidth-reset"></span>
              </div>
            </div>

            <div class="warning-badge" id="warning-badge" style="display: none;">
              <ha-icon icon="mdi:alert-decagram"></ha-icon>
              <span id="warning-text">CPU Throttling detected!</span>
            </div>

            <div class="grid-info">
              <div class="info-item" id="hostname-info-item">
                <div class="info-label">Hostname</div>
                <div class="info-value">-</div>
              </div>
              <div class="info-item" id="os-info-item">
                <div class="info-label">Operating System</div>
                <div class="info-value">-</div>
              </div>
              <div class="info-item" id="hypervisor-info-item">
                <div class="info-label">Hypervisor</div>
                <div class="info-value">-</div>
              </div>
              <div class="info-item" id="ip-info-item">
                <div class="info-label">IP Address</div>
                <div class="info-value" id="ip-val">-</div>
              </div>
              <div class="info-item" id="ssh-info-item">
                <div class="info-label">SSH Port</div>
                <div class="info-value" id="ssh-val">-</div>
              </div>
              <div class="info-item" id="load-info-item">
                <div class="info-label">Load Average</div>
                <div class="info-value" id="load-val">-</div>
              </div>
              <div class="info-item" id="location-info-item">
                <div class="info-label">Location</div>
                <div class="info-value" id="loc-val">-</div>
              </div>
            </div>

            <div class="actions" id="actions-container">
              <button class="action-btn btn-power" id="btn-power">
                <ha-icon icon="mdi:power"></ha-icon>
                <span id="btn-power-text">Toggle</span>
              </button>
              <button class="action-btn" id="btn-reboot">
                <ha-icon icon="mdi:restart"></ha-icon>
                <span>Reboot</span>
              </button>
              <button class="action-btn" id="btn-kill">
                <ha-icon icon="mdi:power-off"></ha-icon>
                <span>Force Stop</span>
              </button>
            </div>
          </div>
        </ha-card>
      `;
      this.content = shadow.getElementById('card-title').parentElement.parentElement;
    }

    this.updateCard();
  }

  // Set card config
  setConfig(config) {
    this.config = config;
    this.veidConfigured = !!config.veid;
    if (this._hass && this.shadowRoot) {
      this.updateCard();
    }
  }

  // Resolve only entities belonging to this VPS. Renamed entities require an override.
  findEntity(domain, key, configKey = key) {
    const veid = this.config.veid ? String(this.config.veid).trim() : '';
    const states = this._hass ? this._hass.states : null;
    if (!states) return null;
    
    // Check config overrides first
    if (this.config[`entity_${configKey}`]) {
      return this.config[`entity_${configKey}`];
    }

    if (!veid) return null;
    const expectedId = `${domain}.bandwagon_host_${veid}_${key}`.toLowerCase();
    const entityIds = Object.keys(states);
    const exactMatch = entityIds.find(id => id.toLowerCase() === expectedId);
    if (exactMatch) return exactMatch;

    const normalizedVeid = veid.toLowerCase();
    const normalizedKey = key.toLowerCase();
    const metadataMatch = entityIds.find(id => {
      if (!id.toLowerCase().startsWith(`${domain}.`)) return false;
      const attributes = states[id].attributes || {};
      const identifiers = [attributes.bandwagon_veid, attributes.bandwagon_hostname]
        .map(value => String(value || '').toLowerCase());
      return identifiers.includes(normalizedVeid) &&
        String(attributes.bandwagon_key || '').toLowerCase() === normalizedKey;
    });
    if (metadataMatch) return metadataMatch;

    return entityIds.find(id => {
      const normalizedId = id.toLowerCase();
      return normalizedId.startsWith(`${domain}.`) &&
        normalizedId.includes(normalizedVeid) &&
        normalizedId.includes(normalizedKey);
    }) || null;
  }

  async callServiceAction(button, domain, service, data) {
    button.disabled = true;
    try {
      await this._hass.callService(domain, service, data);
    } catch (error) {
      const event = new Event('hass-notification', { bubbles: true, composed: true });
      event.detail = { message: error?.message || 'Bandwagon Host action failed' };
      this.dispatchEvent(event);
    } finally {
      button.disabled = false;
    }
  }

  // Update card data and interface safely
  updateCard() {
    if (!this._hass || !this.config) return;

    const root = this.shadowRoot;

    if (!this.veidConfigured) {
      root.getElementById('card-subtitle').innerText = "Configure VEID";
      root.getElementById('card-title').innerText = "Bandwagon Host Card";
      root.getElementById('status-badge').style.display = 'none';
      root.getElementById('gauges-container').style.display = 'none';
      root.getElementById('bandwidth-section').style.display = 'none';
      root.getElementById('warning-badge').style.display = 'none';
      root.querySelector('.grid-info').style.display = 'none';
      root.getElementById('actions-container').style.display = 'none';
      
      // Inject welcome banner
      let welcome = root.getElementById('welcome-banner');
      if (!welcome) {
        welcome = document.createElement('div');
        welcome.id = 'welcome-banner';
        welcome.innerHTML = `
          <style>
            .welcome-banner {
              padding: 24px 16px;
              text-align: center;
              background: rgba(255, 255, 255, 0.02);
              border: 1px dashed rgba(255, 255, 255, 0.1);
              border-radius: 8px;
              margin-top: 10px;
            }
            .welcome-title {
              font-size: 1.1rem;
              font-weight: bold;
              color: var(--primary-accent, #03a9f4);
              margin-bottom: 8px;
            }
            .welcome-text {
              font-size: 0.85rem;
              color: var(--secondary-text-color, #8e8e93);
            }
          </style>
          <div class="welcome-banner">
            <div class="welcome-title">Welcome to Bandwagon Host Card</div>
            <div class="welcome-text">Please enter your <strong>VEID</strong> (or Hostname) in the visual editor or YAML config to begin monitoring.</div>
          </div>
        `;
        root.querySelector('.card-content').appendChild(welcome);
      }
      return;
    } else {
      // Remove welcome banner if present
      const welcome = root.getElementById('welcome-banner');
      if (welcome) welcome.remove();
      
      // Show layout containers
      root.getElementById('status-badge').style.display = 'flex';
      root.getElementById('gauges-container').style.display = 'grid';
      root.getElementById('bandwidth-section').style.display = 'block';
      root.querySelector('.grid-info').style.display = this.config.show_details === false ? 'none' : 'grid';
      root.getElementById('actions-container').style.display = this.config.show_actions === false ? 'none' : 'flex';
    }

    const states = this._hass.states;
    if (!states) return;

    // Resolve entities
    const powerEnt = this.findEntity('switch', 'power');
    const statusEnt = this.findEntity('sensor', 've_status', 'status');
    const ramUsageEnt = this.findEntity('sensor', 'ram_usage_percent', 'ram_usage');
    const diskUsageEnt = this.findEntity('sensor', 'disk_usage_percent', 'disk_usage');
    const dataUsedEnt = this.findEntity('sensor', 'data_used');
    const dataLimitEnt = this.findEntity('sensor', 'data_limit');
    const dataRemainingEnt = this.findEntity('sensor', 'data_remaining');
    const dataResetEnt = this.findEntity('sensor', 'data_next_reset');
    const loadEnt = this.findEntity('sensor', 'load_average');
    const ipEnt = this.findEntity('sensor', 'ip_addresses');
    const sshEnt = this.findEntity('sensor', 'ssh_port');
    const locEnt = this.findEntity('sensor', 'node_location', 'location');
    const planEnt = this.findEntity('sensor', 'plan');
    const hostnameEnt = this.findEntity('sensor', 'hostname');
    const osEnt = this.findEntity('sensor', 'operating_system');
    const hypervisorEnt = this.findEntity('sensor', 'vm_type');
    const cpuThrotEnt = this.findEntity('sensor', 'is_cpu_throttled');
    const diskThrotEnt = this.findEntity('sensor', 'is_disk_throttled');
    const cpuThrotBinaryEnt = this.findEntity('binary_sensor', 'cpu_throttled');
    const diskThrotBinaryEnt = this.findEntity('binary_sensor', 'disk_throttled');
    const suspendedEnt = this.findEntity('binary_sensor', 'suspended');
    const policyEnt = this.findEntity('binary_sensor', 'policy_violation');
    const nullrouteEnt = this.findEntity('binary_sensor', 'ip_nullrouted');
    const rebootBtnEnt = this.findEntity('button', 'restart');
    const killBtnEnt = this.findEntity('button', 'kill');

    // Get States
    const powerState = powerEnt ? states[powerEnt] : null;
    const statusState = statusEnt ? states[statusEnt] : null;
    const ramUsageState = ramUsageEnt ? states[ramUsageEnt] : null;
    const diskUsageState = diskUsageEnt ? states[diskUsageEnt] : null;
    const dataUsedState = dataUsedEnt ? states[dataUsedEnt] : null;
    const dataLimitState = dataLimitEnt ? states[dataLimitEnt] : null;
    const dataRemainingState = dataRemainingEnt ? states[dataRemainingEnt] : null;
    const dataResetState = dataResetEnt ? states[dataResetEnt] : null;
    const loadState = loadEnt ? states[loadEnt] : null;
    const ipState = ipEnt ? states[ipEnt] : null;
    const sshState = sshEnt ? states[sshEnt] : null;
    const locState = locEnt ? states[locEnt] : null;
    const planState = planEnt ? states[planEnt] : null;
    const hostnameState = hostnameEnt ? states[hostnameEnt] : null;
    const osState = osEnt ? states[osEnt] : null;
    const hypervisorState = hypervisorEnt ? states[hypervisorEnt] : null;
    const cpuThrotState = cpuThrotEnt ? states[cpuThrotEnt] : null;
    const diskThrotState = diskThrotEnt ? states[diskThrotEnt] : null;
    const cpuThrotBinaryState = cpuThrotBinaryEnt ? states[cpuThrotBinaryEnt] : null;
    const diskThrotBinaryState = diskThrotBinaryEnt ? states[diskThrotBinaryEnt] : null;
    const suspendedState = suspendedEnt ? states[suspendedEnt] : null;
    const policyState = policyEnt ? states[policyEnt] : null;
    const nullrouteState = nullrouteEnt ? states[nullrouteEnt] : null;

    // Title & Subtitle
    root.getElementById('card-title').innerText = this.config.title || (planState && planState.state ? `VPS Plan: ${planState.state}` : 'Bandwagon VPS');
    root.getElementById('card-subtitle').innerText = this.config.subtitle || `VEID: ${this.config.veid}`;

    // Status Badge
    const statusVal = statusState ? statusState.state.toLowerCase() : (powerState ? (powerState.state === 'on' ? 'running' : 'stopped') : 'unknown');
    const statusBadge = root.getElementById('status-badge');
    const statusText = root.getElementById('status-text');
    statusBadge.className = `status-badge ${statusVal}`;
    statusText.innerText = statusVal.toUpperCase();
    statusBadge.style.display = this.config.show_status === false ? 'none' : 'flex';

    // RAM Gauge
    const ramValElement = root.getElementById('ram-val');
    const ramFillElement = root.getElementById('ram-fill');
    const ramUsage = ramUsageState ? Number(ramUsageState.state) : NaN;
    if (this.config.show_ram !== false && Number.isFinite(ramUsage)) {
      root.getElementById('ram-gauge-wrapper').style.display = 'flex';
      ramValElement.innerText = `${ramUsage}%`;
      ramFillElement.setAttribute('stroke-dasharray', `${ramUsage}, 100`);
      ramFillElement.style.stroke = ramUsage > 90 ? 'var(--danger-color)' : (ramUsage > 75 ? 'var(--warning-color)' : 'var(--primary-accent)');
    } else {
      root.getElementById('ram-gauge-wrapper').style.display = 'none';
    }

    // Disk Gauge
    const diskValElement = root.getElementById('disk-val');
    const diskFillElement = root.getElementById('disk-fill');
    const diskUsage = diskUsageState ? Number(diskUsageState.state) : NaN;
    if (this.config.show_disk !== false && Number.isFinite(diskUsage)) {
      root.getElementById('disk-gauge-wrapper').style.display = 'flex';
      diskValElement.innerText = `${diskUsage}%`;
      diskFillElement.setAttribute('stroke-dasharray', `${diskUsage}, 100`);
      diskFillElement.style.stroke = diskUsage > 90 ? 'var(--danger-color)' : (diskUsage > 75 ? 'var(--warning-color)' : 'var(--primary-accent)');
    } else {
      root.getElementById('disk-gauge-wrapper').style.display = 'none';
    }

    // Hide gauge wrapper if both are empty/disabled
    if ((this.config.show_ram === false || !Number.isFinite(ramUsage)) && (this.config.show_disk === false || !Number.isFinite(diskUsage))) {
      root.getElementById('gauges-container').style.display = 'none';
    } else {
      root.getElementById('gauges-container').style.display = 'grid';
    }

    // Bandwidth
    const bandSection = root.getElementById('bandwidth-section');
    const used = dataUsedState ? Number(dataUsedState.state) : NaN;
    const limit = dataLimitState ? Number(dataLimitState.state) : NaN;
    if (this.config.show_bandwidth !== false && Number.isFinite(used) && Number.isFinite(limit)) {
      bandSection.style.display = 'block';
      const percent = limit > 0 ? Math.min(100, Math.round((used / limit) * 100)) : 0;
      root.getElementById('bandwidth-text').innerText = `${used} / ${limit} GB (${percent}%)`;
      const bar = root.getElementById('bandwidth-bar');
      bar.style.width = `${percent}%`;
      bar.style.background = percent > 90 ? 'var(--danger-color)' : (percent > 75 ? 'var(--warning-color)' : 'linear-gradient(90deg, var(--primary-accent), #00bcd4)');
      const remaining = dataRemainingState ? Number(dataRemainingState.state) : NaN;
      root.getElementById('bandwidth-remaining').innerText = Number.isFinite(remaining) ? `${remaining} GB remaining` : '';
      const resetDate = dataResetState ? new Date(dataResetState.state) : null;
      root.getElementById('bandwidth-reset').innerText = resetDate && !Number.isNaN(resetDate.getTime())
        ? `Resets ${resetDate.toLocaleDateString(this._hass.locale?.language || undefined, { month: 'short', day: 'numeric' })}`
        : '';
    } else {
      bandSection.style.display = 'none';
    }

    // Throttling Warnings
    const warningBadge = root.getElementById('warning-badge');
    const cpuThrottled = cpuThrotBinaryState?.state === 'on' || cpuThrotState?.state?.toLowerCase() === 'yes';
    const diskThrottled = diskThrotBinaryState?.state === 'on' || diskThrotState?.state?.toLowerCase() === 'yes';
    const suspended = suspendedState?.state === 'on';
    const policyViolation = policyState?.state === 'on';
    const nullrouted = nullrouteState?.state === 'on';
    const warnings = [];
    if (suspended) warnings.push('VPS suspended');
    if (policyViolation) warnings.push('Policy violation requires attention');
    if (nullrouted) warnings.push('IP nullroute active');
    if (cpuThrottled) warnings.push('CPU throttling active');
    if (diskThrottled) warnings.push('Disk I/O throttling active');
    if (warnings.length > 0) {
      warningBadge.style.display = 'flex';
      warningBadge.className = `warning-badge ${suspended || policyViolation || nullrouted ? 'critical' : ''}`;
      root.getElementById('warning-text').innerText = warnings.join(' | ');
    } else {
      warningBadge.style.display = 'none';
    }

    // Grid Info items
    const updateInfoItem = (id, stateObj, visible) => {
      const itemEl = root.getElementById(id);
      if (itemEl) {
        if (visible && stateObj && stateObj.state !== undefined) {
          itemEl.style.display = 'flex';
          itemEl.querySelector('.info-value').innerText = stateObj.state;
        } else {
          itemEl.style.display = 'none';
        }
      }
    };

    const showDetails = this.config.show_details !== false;
    updateInfoItem('hostname-info-item', hostnameState, showDetails && this.config.show_hostname !== false);
    updateInfoItem('os-info-item', osState, showDetails && this.config.show_os !== false);
    updateInfoItem('hypervisor-info-item', hypervisorState, showDetails && this.config.show_hypervisor !== false);
    updateInfoItem('ip-info-item', ipState, showDetails && this.config.show_ip !== false);
    updateInfoItem('ssh-info-item', sshState, showDetails && this.config.show_ssh !== false);
    updateInfoItem('load-info-item', loadState, showDetails && this.config.show_load !== false);
    updateInfoItem('location-info-item', locState, showDetails && this.config.show_location !== false);
    const detailsContainer = root.querySelector('.grid-info');
    const hasVisibleDetail = Array.from(detailsContainer.children)
      .some(item => item.style.display !== 'none');
    detailsContainer.style.display = showDetails && hasVisibleDetail ? 'grid' : 'none';

    // Actions Power button
    const btnPower = root.getElementById('btn-power');
    const btnPowerText = root.getElementById('btn-power-text');
    if (powerState && powerState.state !== undefined && this.config.show_actions !== false && this.config.show_power !== false) {
      btnPower.style.display = 'flex';
      const isOn = powerState.state === 'on';
      btnPower.className = `action-btn btn-power ${isOn ? 'on' : 'off'}`;
      btnPowerText.innerText = isOn ? 'Stop' : 'Start';
      btnPower.onclick = async () => {
        if (isOn && !confirm(`Stop VPS ${this.config.veid}? Services running on the VPS will become unavailable.`)) {
          return;
        }
        await this.callServiceAction(btnPower, 'switch', isOn ? 'turn_off' : 'turn_on', { entity_id: powerEnt });
      };
    } else {
      btnPower.style.display = 'none';
    }

    // Reboot action
    const btnReboot = root.getElementById('btn-reboot');
    if (rebootBtnEnt && this.config.show_actions !== false && this.config.show_reboot !== false) {
      btnReboot.style.display = 'flex';
      btnReboot.onclick = async () => {
        if (confirm(`Reboot VPS ${this.config.veid}? Services will be temporarily unavailable.`)) {
          await this.callServiceAction(btnReboot, 'button', 'press', { entity_id: rebootBtnEnt });
        }
      };
    } else {
      btnReboot.style.display = 'none';
    }

    // Kill action
    const btnKill = root.getElementById('btn-kill');
    if (killBtnEnt && this.config.show_actions !== false && this.config.show_kill !== false) {
      btnKill.style.display = 'flex';
      btnKill.onclick = async () => {
        if (confirm(`Force stop VPS ${this.config.veid}? This can cause data loss and should only be used when a normal stop fails.`)) {
          await this.callServiceAction(btnKill, 'button', 'press', { entity_id: killBtnEnt });
        }
      };
    } else {
      btnKill.style.display = 'none';
    }

    const actionsContainer = root.getElementById('actions-container');
    const hasVisibleAction = [btnPower, btnReboot, btnKill]
      .some(button => button.style.display !== 'none');
    actionsContainer.style.display = this.config.show_actions !== false && hasVisibleAction ? 'flex' : 'none';

    // Custom coloring override
    const numberSetting = (value, fallback, min, max) => {
      const parsed = Number(value);
      return Math.min(max, Math.max(min, Number.isFinite(parsed) && value !== '' ? parsed : fallback));
    };
    this.style.setProperty('--card-padding', `${numberSetting(this.config.card_padding, 16, 0, 40)}px`);
    this.style.setProperty('--gauge-size', `${numberSetting(this.config.gauge_size, 96, 56, 160)}px`);
    this.style.setProperty('--gauge-border', `${numberSetting(this.config.gauge_thickness, 5, 2, 8)}px`);
    this.style.setProperty('--bandwagon-accent', this.config.accent_color || 'var(--primary-color, #03a9f4)');
    this.style.setProperty('--bandwagon-background', this.config.background_color || 'var(--card-background-color, #1c1c1e)');
  }

  // Visual editor bindings
  static getConfigElement() {
    return document.createElement("bandwagon-host-card-editor");
  }

  static getStubConfig() {
    return {
      veid: "",
      title: "",
      subtitle: "",
      show_ram: true,
      show_disk: true,
      show_bandwidth: true,
      show_status: true,
      show_details: true,
      show_hostname: true,
      show_os: true,
      show_hypervisor: true,
      show_ip: true,
      show_ssh: true,
      show_load: true,
      show_location: true,
      show_actions: true,
      show_power: true,
      show_reboot: true,
      show_kill: true
    };
  }

  // Home Assistant size recommendation
  getCardSize() {
    return 4;
  }
}

customElements.define('bandwagon-host-card', BandwagonHostCard);

// Card Editor custom element for visual configuration
class BandwagonHostCardEditor extends HTMLElement {
  setConfig(config) {
    this._config = config;
  }

  set hass(hass) {
    this._hass = hass;
    if (!this.content) {
      const shadow = this.attachShadow({ mode: 'open' });
      shadow.innerHTML = `
        <style>
          .form-group {
            margin-bottom: 16px;
            display: flex;
            flex-direction: column;
          }
          label {
            font-size: 0.9rem;
            font-weight: 500;
            color: var(--primary-text-color, #ffffff);
            margin-bottom: 6px;
          }
          input[type="text"], input[type="number"], input[type="color"] {
            padding: 8px 12px;
            border-radius: 4px;
            border: 1px solid var(--divider-color, #2c2c2e);
            background: var(--card-background-color, #1c1c1e);
            color: var(--primary-text-color, #ffffff);
            font-size: 0.9rem;
          }
          input[type="color"] {
            width: 100%;
            height: 40px;
            padding: 4px;
          }
          .section-title {
            margin: 20px 0 12px;
            color: var(--secondary-text-color, #8e8e93);
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
          }
          .number-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 10px;
          }
          .checkbox-group {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 12px;
          }
          .checkbox-group label {
            margin-bottom: 0;
            cursor: pointer;
          }
        </style>
        <div class="card-config">
          <div class="form-group">
            <label for="veid">VPS VEID or Hostname (Required)</label>
            <input type="text" id="veid" config-value="veid">
          </div>
          <div class="form-group">
            <label for="title">Title (Optional)</label>
            <input type="text" id="title" config-value="title">
          </div>
          <div class="form-group">
            <label for="subtitle">Subtitle (Optional)</label>
            <input type="text" id="subtitle" config-value="subtitle" placeholder="VEID: ...">
          </div>
          <div class="section-title">Appearance</div>
          <div class="form-group">
            <label for="accent_color">Accent Color (Optional)</label>
            <input type="color" id="accent_color" config-value="accent_color" value="#03a9f4">
          </div>
          <div class="form-group">
            <label for="background_color">Background Color (Optional)</label>
            <input type="color" id="background_color" config-value="background_color" value="#1c1c1e">
          </div>
          <div class="number-grid">
            <div class="form-group">
              <label for="gauge_size">Gauge Size</label>
              <input type="number" id="gauge_size" config-value="gauge_size" min="56" max="160" step="4">
            </div>
            <div class="form-group">
              <label for="gauge_thickness">Gauge Width</label>
              <input type="number" id="gauge_thickness" config-value="gauge_thickness" min="2" max="8" step="1">
            </div>
            <div class="form-group">
              <label for="card_padding">Card Padding</label>
              <input type="number" id="card_padding" config-value="card_padding" min="0" max="40" step="2">
            </div>
          </div>
          <div class="section-title">Visible Sections</div>
          <div class="checkbox-group">
            <input type="checkbox" id="show_ram" config-value="show_ram">
            <label for="show_ram">Show RAM Gauge</label>
          </div>
          <div class="checkbox-group">
            <input type="checkbox" id="show_disk" config-value="show_disk">
            <label for="show_disk">Show Disk Gauge</label>
          </div>
          <div class="checkbox-group">
            <input type="checkbox" id="show_bandwidth" config-value="show_bandwidth">
            <label for="show_bandwidth">Show Bandwidth Bar</label>
          </div>
          <div class="checkbox-group">
            <input type="checkbox" id="show_status" config-value="show_status">
            <label for="show_status">Show Status</label>
          </div>
          <div class="checkbox-group">
            <input type="checkbox" id="show_details" config-value="show_details">
            <label for="show_details">Show Server Details</label>
          </div>
          <div class="checkbox-group">
            <input type="checkbox" id="show_hostname" config-value="show_hostname">
            <label for="show_hostname">Show Hostname</label>
          </div>
          <div class="checkbox-group">
            <input type="checkbox" id="show_os" config-value="show_os">
            <label for="show_os">Show Operating System</label>
          </div>
          <div class="checkbox-group">
            <input type="checkbox" id="show_hypervisor" config-value="show_hypervisor">
            <label for="show_hypervisor">Show Hypervisor</label>
          </div>
          <div class="checkbox-group">
            <input type="checkbox" id="show_ip" config-value="show_ip">
            <label for="show_ip">Show IP Address</label>
          </div>
          <div class="checkbox-group">
            <input type="checkbox" id="show_ssh" config-value="show_ssh">
            <label for="show_ssh">Show SSH Port</label>
          </div>
          <div class="checkbox-group">
            <input type="checkbox" id="show_load" config-value="show_load">
            <label for="show_load">Show Load Average</label>
          </div>
          <div class="checkbox-group">
            <input type="checkbox" id="show_location" config-value="show_location">
            <label for="show_location">Show VPS Location</label>
          </div>
          <div class="checkbox-group">
            <input type="checkbox" id="show_actions" config-value="show_actions">
            <label for="show_actions">Show Actions</label>
          </div>
          <div class="checkbox-group">
            <input type="checkbox" id="show_power" config-value="show_power">
            <label for="show_power">Show Start/Stop</label>
          </div>
          <div class="checkbox-group">
            <input type="checkbox" id="show_reboot" config-value="show_reboot">
            <label for="show_reboot">Show Reboot</label>
          </div>
          <div class="checkbox-group">
            <input type="checkbox" id="show_kill" config-value="show_kill">
            <label for="show_kill">Show Force Stop (Kill) Button</label>
          </div>
          <div class="section-title">Entity Overrides</div>
          <div class="form-group">
            <label for="entity_hostname">Hostname Entity</label>
            <input type="text" id="entity_hostname" config-value="entity_hostname" placeholder="sensor.bandwagon_host_..._hostname">
          </div>
          <div class="form-group">
            <label for="entity_operating_system">Operating System Entity</label>
            <input type="text" id="entity_operating_system" config-value="entity_operating_system" placeholder="sensor.bandwagon_host_..._operating_system">
          </div>
          <div class="form-group">
            <label for="entity_vm_type">Hypervisor Entity</label>
            <input type="text" id="entity_vm_type" config-value="entity_vm_type" placeholder="sensor.bandwagon_host_..._vm_type">
          </div>
          <div class="form-group">
            <label for="entity_ip_addresses">IP Address Entity</label>
            <input type="text" id="entity_ip_addresses" config-value="entity_ip_addresses" placeholder="sensor.bandwagon_host_..._ip_addresses">
          </div>
          <div class="form-group">
            <label for="entity_ssh_port">SSH Port Entity</label>
            <input type="text" id="entity_ssh_port" config-value="entity_ssh_port" placeholder="sensor.bandwagon_host_..._ssh_port">
          </div>
          <div class="form-group">
            <label for="entity_load_average">Load Average Entity</label>
            <input type="text" id="entity_load_average" config-value="entity_load_average" placeholder="sensor.bandwagon_host_..._load_average">
          </div>
          <div class="form-group">
            <label for="entity_location">VPS Location Entity</label>
            <input type="text" id="entity_location" config-value="entity_location" placeholder="sensor.bandwagon_host_..._node_location">
          </div>
          <div class="form-group">
            <label for="entity_power">Start/Stop Entity</label>
            <input type="text" id="entity_power" config-value="entity_power" placeholder="switch.bandwagon_host_..._power">
          </div>
          <div class="form-group">
            <label for="entity_restart">Reboot Entity</label>
            <input type="text" id="entity_restart" config-value="entity_restart" placeholder="button.bandwagon_host_..._restart">
          </div>
          <div class="form-group">
            <label for="entity_kill">Force Stop Entity</label>
            <input type="text" id="entity_kill" config-value="entity_kill" placeholder="button.bandwagon_host_..._kill">
          </div>
        </div>
      `;
      this.content = shadow.querySelector('.card-config');

      // Bind event listeners
      this.content.addEventListener('change', (ev) => this._valueChanged(ev));
      this.content.addEventListener('input', (ev) => this._valueChanged(ev));
    }

    this._updateEditor();
  }

  _updateEditor() {
    if (!this._config) return;
    const root = this.shadowRoot;
    
    const setVal = (id, val) => {
      const el = root.getElementById(id);
      if (el) el.value = val !== undefined ? val : '';
    };

    const setChecked = (id, val) => {
      const el = root.getElementById(id);
      if (el) el.checked = val !== false;
    };

    setVal('veid', this._config.veid);
    setVal('title', this._config.title);
    setVal('subtitle', this._config.subtitle);
    setVal('accent_color', this._config.accent_color);
    setVal('background_color', this._config.background_color);
    setVal('gauge_size', this._config.gauge_size || 96);
    setVal('gauge_thickness', this._config.gauge_thickness || 5);
    setVal('card_padding', this._config.card_padding ?? 16);
    setVal('entity_hostname', this._config.entity_hostname);
    setVal('entity_operating_system', this._config.entity_operating_system);
    setVal('entity_vm_type', this._config.entity_vm_type);
    setVal('entity_ip_addresses', this._config.entity_ip_addresses);
    setVal('entity_ssh_port', this._config.entity_ssh_port);
    setVal('entity_load_average', this._config.entity_load_average);
    setVal('entity_location', this._config.entity_location);
    setVal('entity_power', this._config.entity_power);
    setVal('entity_restart', this._config.entity_restart);
    setVal('entity_kill', this._config.entity_kill);
    setChecked('show_ram', this._config.show_ram);
    setChecked('show_disk', this._config.show_disk);
    setChecked('show_bandwidth', this._config.show_bandwidth);
    setChecked('show_status', this._config.show_status);
    setChecked('show_details', this._config.show_details);
    setChecked('show_hostname', this._config.show_hostname);
    setChecked('show_os', this._config.show_os);
    setChecked('show_hypervisor', this._config.show_hypervisor);
    setChecked('show_ip', this._config.show_ip);
    setChecked('show_ssh', this._config.show_ssh);
    setChecked('show_load', this._config.show_load);
    setChecked('show_location', this._config.show_location);
    setChecked('show_actions', this._config.show_actions);
    setChecked('show_power', this._config.show_power);
    setChecked('show_reboot', this._config.show_reboot);
    setChecked('show_kill', this._config.show_kill);
  }

  _valueChanged(ev) {
    if (!this._config) return;
    const target = ev.target;
    const configKey = target.getAttribute('config-value');
    if (!configKey) return;

    const value = target.type === 'checkbox' ? target.checked : target.value;
    const newConfig = { ...this._config };
    
    if (value === '' || value === undefined) {
      delete newConfig[configKey];
    } else {
      newConfig[configKey] = value;
    }

    const event = new CustomEvent('config-changed', {
      detail: { config: newConfig },
      bubbles: true,
      composed: true,
    });
    this.dispatchEvent(event);
  }
}
customElements.define('bandwagon-host-card-editor', BandwagonHostCardEditor);

window.customCards = window.customCards || [];
window.customCards.push({
  type: "bandwagon-host-card",
  name: "Bandwagon Host Card",
  preview: true,
  description: "A premium dashboard card for monitoring and controlling Bandwagon Host VPS instances.",
  documentationURL: "https://github.com/soulripper13/bandwagon_host",
});
