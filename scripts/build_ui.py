import subprocess

# 1. Fetch the complete original dashboard from commit f08c080
raw = subprocess.check_output(['git', 'show', 'f08c080:dashboard/index.html'], encoding='utf-8')

css_insert = """
/* HERO BANNER & KPI CARDS FROM REFERENCE (media_1788543690858.png) */
.hero-banner {
  background: linear-gradient(90deg, #070d1e 0%, #0d1a38 35%, #0f2048 55%, #0a142e 100%);
  border-radius: 14px;
  padding: 22px 30px;
  margin-bottom: 18px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: relative;
  overflow: hidden;
  box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.2);
  color: #ffffff;
}
.hero-banner-globe {
  position: absolute;
  left: 48%;
  top: 50%;
  transform: translate(-50%, -50%);
  pointer-events: none;
  opacity: 0.65;
  filter: drop-shadow(0 0 18px rgba(56, 189, 248, 0.45));
}
.hero-left { position: relative; z-index: 2; }
.hero-title {
  font-family: var(--display);
  font-size: 22px;
  font-weight: 800;
  letter-spacing: -0.02em;
  margin: 0 0 6px;
  color: #ffffff;
}
.hero-sub {
  font-size: 13px;
  color: #93c5fd;
  margin: 0;
  font-weight: 500;
}
.hero-center-quote {
  position: relative;
  z-index: 2;
  font-size: 13px;
  font-style: italic;
  color: rgba(224, 231, 255, 0.8);
  max-width: 220px;
  line-height: 1.45;
  text-align: right;
}
.hero-status-box {
  position: relative;
  z-index: 2;
  background: rgba(6, 78, 59, 0.45);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(16, 185, 129, 0.4);
  border-radius: 12px;
  padding: 10px 18px;
  display: flex;
  align-items: center;
  gap: 12px;
}
.hero-status-icon {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: rgba(16, 185, 129, 0.25);
  border: 1px solid rgba(16, 185, 129, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #34d399;
  flex-shrink: 0;
}
.hero-status-title { font-size: 13.5px; font-weight: 700; color: #ffffff; }
.hero-status-desc { font-size: 11px; color: #94a3b8; }

.bank-kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr) 190px;
  gap: 14px;
  margin-bottom: 20px;
}
@media (max-width: 1200px) {
  .bank-kpi-grid { grid-template-columns: repeat(2, 1fr) 1fr; }
}
@media (max-width: 768px) {
  .bank-kpi-grid { grid-template-columns: 1fr; }
}

.kpi-card {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 12px;
  padding: 16px 18px;
  box-shadow: 0 2px 8px rgba(15,23,42,0.02);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  cursor: pointer;
  transition: all 0.15s ease;
}
.kpi-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 14px rgba(15,23,42,0.06);
}
.kpi-card.selected {
  box-shadow: 0 0 0 2px var(--cyan), 0 4px 14px rgba(79, 70, 229, 0.15);
}
.card-sbi { background: #fffbfa; border: 1px solid #fee2e2; }
.card-hdfc { background: #fffbfa; border: 1px solid #fee2e2; }
.card-icici { background: #fffdf5; border: 1px solid #fef08a; }
.card-pnb { background: #f7fdf9; border: 1px solid #bbf7d0; }

.kpi-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}
.kpi-bank-header {
  display: flex;
  align-items: center;
  gap: 10px;
}
.bank-logo-img {
  width: 24px;
  height: 24px;
  object-fit: contain;
  flex-shrink: 0;
  display: block;
}
.bank-logo-img.round { border-radius: 50%; }
.bank-logo-img.radius-sm { border-radius: 4px; }
.kpi-bank-name {
  font-family: var(--display);
  font-size: 15px;
  font-weight: 700;
  color: var(--text);
}
.kpi-pill {
  font-size: 10.5px;
  font-weight: 700;
  padding: 3px 10px;
  border-radius: 20px;
  font-family: var(--mono);
  letter-spacing: 0.03em;
}
.pill-danger { background: #fee2e2; color: #ef4444; border: 1px solid #fca5a5; }
.pill-warn { background: #fef3c7; color: #d97706; border: 1px solid #fde68a; }
.pill-pass { background: #ecfdf5; color: #10b981; border: 1px solid #a7f3d0; }

.kpi-score-row {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-bottom: 2px;
}
.kpi-score {
  font-family: var(--display);
  font-size: 34px;
  font-weight: 800;
  line-height: 1;
}
.kpi-score-denom {
  font-size: 14px;
  font-weight: 600;
  color: #94a3b8;
  margin-left: 4px;
}
.kpi-delta {
  font-weight: 700;
  font-size: 12px;
  font-family: var(--mono);
}
.kpi-label {
  color: #64748b;
  font-size: 11px;
  font-weight: 600;
  margin-bottom: 8px;
}
.kpi-sparkline {
  width: 100%;
  height: 32px;
  overflow: visible;
}

.stats-card {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 12px;
  padding: 14px 16px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  box-shadow: 0 2px 8px rgba(15,23,42,0.02);
}
.stat-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 5px 0;
}
.stat-row:not(:last-child) {
  border-bottom: 1px solid var(--surface2);
}
.stat-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: var(--teal-soft);
  color: var(--cyan);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.stat-content { line-height: 1.2; }
.stat-val {
  font-family: var(--display);
  font-size: 14.5px;
  font-weight: 800;
  color: var(--text);
}
.stat-lbl {
  font-size: 10.5px;
  color: var(--text3);
  font-weight: 500;
}
"""

html_insert = """
  <!-- REAL-TIME SETTLEMENT RISK MONITORING HERO BANNER (media_1788543690858.png) -->
  <div class="hero-banner">
    <div class="hero-banner-globe">
      <svg viewBox="0 0 200 200" width="180" height="180">
        <defs>
          <radialGradient id="globe-glow" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stop-color="#38bdf8" stop-opacity="0.4"/>
            <stop offset="65%" stop-color="#1d4ed8" stop-opacity="0.12"/>
            <stop offset="100%" stop-color="#0f172a" stop-opacity="0"/>
          </radialGradient>
          <linearGradient id="globe-grid" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#60a5fa" stop-opacity="0.85"/>
            <stop offset="100%" stop-color="#38bdf8" stop-opacity="0.45"/>
          </linearGradient>
        </defs>
        <circle cx="100" cy="100" r="88" fill="url(#globe-glow)"/>
        <circle cx="100" cy="100" r="66" fill="none" stroke="url(#globe-grid)" stroke-width="1.2" stroke-dasharray="2 3"/>
        <ellipse cx="100" cy="100" rx="66" ry="22" fill="none" stroke="url(#globe-grid)" stroke-width="1" />
        <ellipse cx="100" cy="100" rx="66" ry="44" fill="none" stroke="url(#globe-grid)" stroke-width="1" />
        <ellipse cx="100" cy="100" rx="22" ry="66" fill="none" stroke="url(#globe-grid)" stroke-width="1" />
        <ellipse cx="100" cy="100" rx="44" ry="66" fill="none" stroke="url(#globe-grid)" stroke-width="1" />
        <line x1="34" y1="100" x2="166" y2="100" stroke="url(#globe-grid)" stroke-width="1.2"/>
        <line x1="100" y1="34" x2="100" y2="166" stroke="url(#globe-grid)" stroke-width="1.2"/>
        <circle cx="100" cy="56" r="2.5" fill="#38bdf8"/>
        <circle cx="122" cy="78" r="3" fill="#60a5fa"/>
        <circle cx="78" cy="100" r="2.5" fill="#93c5fd"/>
        <circle cx="144" cy="100" r="3" fill="#38bdf8"/>
        <circle cx="100" cy="122" r="2.5" fill="#60a5fa"/>
        <circle cx="64" cy="128" r="2" fill="#38bdf8"/>
        <circle cx="132" cy="138" r="2.5" fill="#93c5fd"/>
      </svg>
    </div>
    <div class="hero-left">
      <h1 class="hero-title">Real-Time Settlement Risk Monitoring</h1>
      <p class="hero-sub">Detect &nbsp;&bull;&nbsp; Simulate &nbsp;&bull;&nbsp; Mitigate &nbsp;&bull;&nbsp; Ensure Stability</p>
    </div>
    <div class="hero-center-quote">
      &ldquo;Proactive intelligence for a Stable Financial Ecosystem&rdquo;
    </div>
    <div class="hero-status-box">
      <div class="hero-status-icon">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#34d399" stroke-width="2.5">
          <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
          <polyline points="9 12 11 14 15 10"></polyline>
        </svg>
      </div>
      <div class="hero-status-text">
        <div class="hero-status-title">System Healthy</div>
        <div class="hero-status-desc">All core services operational</div>
      </div>
    </div>
  </div>

  <!-- BANK VITALITY SCORE KPI CARDS ROW (media_1788543690858.png) -->
  <div class="bank-kpi-grid">
    <!-- SBI -->
    <div class="kpi-card card-sbi selected" id="card-SBI" onclick="changeBank('SBI')">
      <div class="kpi-top">
        <div class="kpi-bank-header">
          <img src="assets/sbi.png" alt="SBI" class="bank-logo-img round" />
          <div class="kpi-bank-name">SBI</div>
        </div>
        <span class="kpi-pill pill-danger" id="badge-SBI">HIGH RISK</span>
      </div>
      <div>
        <div class="kpi-score-row">
          <div style="display:flex;align-items:baseline;">
            <span class="kpi-score" id="score-SBI" style="color:var(--coral);">22</span>
            <span class="kpi-score-denom">/ 100</span>
          </div>
          <span class="kpi-delta" style="color:var(--coral);" id="delta-SBI">&darr; -18 (24h)</span>
        </div>
        <div class="kpi-label">Bank Vitality Score</div>
      </div>
      <svg class="kpi-sparkline" viewBox="0 0 100 28" preserveAspectRatio="none">
        <defs>
          <linearGradient id="grad-red" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#fee2e2" stop-opacity="0.8"/>
            <stop offset="100%" stop-color="#fee2e2" stop-opacity="0"/>
          </linearGradient>
        </defs>
        <path d="M 0,8 Q 20,4 35,14 T 65,18 T 100,24 L 100,28 L 0,28 Z" fill="url(#grad-red)" />
        <path d="M 0,8 Q 20,4 35,14 T 65,18 T 100,24" fill="none" stroke="#e11d48" stroke-width="2" />
      </svg>
    </div>

    <!-- HDFC -->
    <div class="kpi-card card-hdfc" id="card-HDFC" onclick="changeBank('HDFC')">
      <div class="kpi-top">
        <div class="kpi-bank-header">
          <img src="assets/hdfc.png" alt="HDFC" class="bank-logo-img radius-sm" />
          <div class="kpi-bank-name">HDFC</div>
        </div>
        <span class="kpi-pill pill-danger" id="badge-HDFC">HIGH RISK</span>
      </div>
      <div>
        <div class="kpi-score-row">
          <div style="display:flex;align-items:baseline;">
            <span class="kpi-score" id="score-HDFC" style="color:var(--coral);">34</span>
            <span class="kpi-score-denom">/ 100</span>
          </div>
          <span class="kpi-delta" style="color:var(--coral);" id="delta-HDFC">&darr; -12 (24h)</span>
        </div>
        <div class="kpi-label">Bank Vitality Score</div>
      </div>
      <svg class="kpi-sparkline" viewBox="0 0 100 28" preserveAspectRatio="none">
        <path d="M 0,10 Q 25,6 45,16 T 80,14 T 100,22 L 100,28 L 0,28 Z" fill="url(#grad-red)" />
        <path d="M 0,10 Q 25,6 45,16 T 80,14 T 100,22" fill="none" stroke="#e11d48" stroke-width="2" />
      </svg>
    </div>

    <!-- ICICI -->
    <div class="kpi-card card-icici" id="card-ICICI" onclick="changeBank('ICICI')">
      <div class="kpi-top">
        <div class="kpi-bank-header">
          <img src="assets/icici.jpg" alt="ICICI" class="bank-logo-img round" />
          <div class="kpi-bank-name">ICICI</div>
        </div>
        <span class="kpi-pill pill-warn" id="badge-ICICI">MEDIUM</span>
      </div>
      <div>
        <div class="kpi-score-row">
          <div style="display:flex;align-items:baseline;">
            <span class="kpi-score" id="score-ICICI" style="color:var(--amber);">58</span>
            <span class="kpi-score-denom">/ 100</span>
          </div>
          <span class="kpi-delta" style="color:var(--amber);" id="delta-ICICI">&darr; -6 (24h)</span>
        </div>
        <div class="kpi-label">Bank Vitality Score</div>
      </div>
      <svg class="kpi-sparkline" viewBox="0 0 100 28" preserveAspectRatio="none">
        <defs>
          <linearGradient id="grad-amber" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#fef3c7" stop-opacity="0.8"/>
            <stop offset="100%" stop-color="#fef3c7" stop-opacity="0"/>
          </linearGradient>
        </defs>
        <path d="M 0,6 Q 30,14 55,8 T 85,16 T 100,18 L 100,28 L 0,28 Z" fill="url(#grad-amber)" />
        <path d="M 0,6 Q 30,14 55,8 T 85,16 T 100,18" fill="none" stroke="#d97706" stroke-width="2" />
      </svg>
    </div>

    <!-- PNB -->
    <div class="kpi-card card-pnb" id="card-PNB" onclick="changeBank('PNB')">
      <div class="kpi-top">
        <div class="kpi-bank-header">
          <img src="assets/pnb.png" alt="PNB" class="bank-logo-img radius-sm" />
          <div class="kpi-bank-name">PNB</div>
        </div>
        <span class="kpi-pill pill-pass" id="badge-PNB">LOW RISK</span>
      </div>
      <div>
        <div class="kpi-score-row">
          <div style="display:flex;align-items:baseline;">
            <span class="kpi-score" id="score-PNB" style="color:var(--moss);">76</span>
            <span class="kpi-score-denom">/ 100</span>
          </div>
          <span class="kpi-delta" style="color:var(--moss);" id="delta-PNB">&uarr; +4 (24h)</span>
        </div>
        <div class="kpi-label">Bank Vitality Score</div>
      </div>
      <svg class="kpi-sparkline" viewBox="0 0 100 28" preserveAspectRatio="none">
        <defs>
          <linearGradient id="grad-green" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#dcfce7" stop-opacity="0.8"/>
            <stop offset="100%" stop-color="#dcfce7" stop-opacity="0"/>
          </linearGradient>
        </defs>
        <path d="M 0,20 Q 30,22 50,14 T 80,12 T 100,4 L 100,28 L 0,28 Z" fill="url(#grad-green)" />
        <path d="M 0,20 Q 30,22 50,14 T 80,12 T 100,4" fill="none" stroke="#10b981" stroke-width="2" />
      </svg>
    </div>

    <!-- SUMMARY QUICK STATS -->
    <div class="stats-card">
      <div class="stat-row">
        <div class="stat-icon">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 21h18M3 10h18M5 10v11M9 10v11M15 10v11M19 10v11M12 2L2 7h20L12 2z"/></svg>
        </div>
        <div class="stat-content">
          <div class="stat-val">6</div>
          <div class="stat-lbl">Banks Monitoring</div>
        </div>
      </div>
      <div class="stat-row">
        <div class="stat-icon">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"></circle><path d="M14.5 9h-5a2 2 0 0 0 0 4h3a2 2 0 0 1 0 4h-5"></path></svg>
        </div>
        <div class="stat-content">
          <div class="stat-val">&#8377;5.00 Cr</div>
          <div class="stat-lbl">Simulated Capital</div>
        </div>
      </div>
      <div class="stat-row">
        <div class="stat-icon">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4.9 19.1C1 15.2 1 8.8 4.9 4.9M7.8 16.2c-2.3-2.3-2.3-6.1 0-8.5M12 12h.01M16.2 7.8c2.3 2.3 2.3 6.1 0 8.5M19.1 4.9c3.9 3.9 3.9 10.3 0 14.2"/></svg>
        </div>
        <div class="stat-content">
          <div class="stat-val" style="color:var(--cyan);">Live Feed</div>
          <div class="stat-lbl">Real-time data</div>
        </div>
      </div>
    </div>
  </div>
"""

# Insert CSS right before </style>
pos_style = raw.find('</style>')
step1 = raw[:pos_style] + css_insert + raw[pos_style:]

# Insert Hero and KPI Cards right after </header>
target_hdr = '</header>'
pos_hdr = step1.find(target_hdr)
pos_insert = pos_hdr + len(target_hdr)
final_html = step1[:pos_insert] + '\n' + html_insert + step1[pos_insert:]

# Ensure changeBank also highlights the selected KPI card
change_bank_js_old = "function changeBank(b){"
change_bank_js_new = """function changeBank(b){
  document.querySelectorAll('.kpi-card').forEach(c => {
    c.classList.toggle('selected', c.id === 'card-' + b);
  });"""
final_html = final_html.replace(change_bank_js_old, change_bank_js_new)

with open('dashboard/index.html', 'w', encoding='utf-8') as f:
    f.write(final_html)

print("Successfully restored old dashboard with reference banner & bank cards! Total lines:", len(final_html.splitlines()))
