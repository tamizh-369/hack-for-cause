"""Cinematic Demo Video Player for Public Health Claim Watchdog.

Self-contained, high-production 1080p-style video simulator with:
- True 60 FPS continuous playback
- Netflix/YouTube style controls: Play/Pause, timeline scrubber, 0:00 / 1:18 timecode, CC subtitles, replay, skip
- Interactive video screen with animated scenes:
    1. Introduction & Mission (Tamil Nadu HMIS)
    2. The Evaluated Claim (CLM-001 Coimbatore Immunization)
    3. Provisional Release 1 Verdict (✅ SUPPORTED +9.6%)
    4. Deterministic Evidence Table & Regional Languages (Tamil / Hindi)
    5. The Revision Drift Pivot (Release 2 Audited: 🚨 DRIFT ALERT -> ❌ UNSUPPORTED +3.4%)
    6. Reviewer Desk Sign-Off & Session Audit Trail Logging
    7. Free-Text Sentence Parser & SDG 3 / SDG 16 Conclusion
- 100% self-contained: zero iframe sandbox dependencies, zero server re-runs during playback, never freezes.
"""

def get_cinema_player_html() -> str:
    """Return self-contained HTML/CSS/JS for the Cinema Video Player."""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            background: #060714;
            color: #f1f5f9;
            font-family: 'Inter', system-ui, -apple-system, sans-serif;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            width: 100vw;
            user-select: none;
        }

        /* ── Main Cinema Container ────────────────────────── */
        .cinema-container {
            width: 98%;
            max-width: 960px;
            height: 96vh;
            max-height: 620px;
            background: #090a1c;
            border: 1.5px solid rgba(255, 255, 255, 0.12);
            border-radius: 20px;
            box-shadow: 0 16px 50px rgba(0, 0, 0, 0.8),
                        0 0 30px rgba(34, 211, 238, 0.18);
            display: flex;
            flex-direction: column;
            position: relative;
            overflow: hidden;
        }

        /* ── Top Bar ──────────────────────────────────────── */
        .player-topbar {
            padding: 12px 20px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: rgba(12, 14, 32, 0.85);
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
            z-index: 10;
        }
        .topbar-left {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .topbar-icon {
            font-size: 1.4rem;
            filter: drop-shadow(0 0 10px rgba(34, 211, 238, 0.8));
        }
        .topbar-title {
            font-size: 0.98rem;
            font-weight: 800;
            background: linear-gradient(90deg, #f1f5f9, #22d3ee);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .topbar-badge {
            background: rgba(34, 211, 238, 0.15);
            border: 1px solid rgba(34, 211, 238, 0.4);
            color: #22d3ee;
            font-size: 0.7rem;
            font-weight: 800;
            padding: 2px 8px;
            border-radius: 100px;
            letter-spacing: 0.5px;
        }
        .rec-indicator {
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 0.72rem;
            color: #f87171;
            font-weight: 700;
        }
        .rec-dot {
            width: 8px; height: 8px;
            background: #ef4444;
            border-radius: 50%;
            box-shadow: 0 0 10px #ef4444;
            animation: pulseDot 1.2s infinite;
        }
        @keyframes pulseDot {
            0%, 100% { opacity: 1; transform: scale(1); }
            50%      { opacity: 0.3; transform: scale(0.7); }
        }

        /* ── Video Screen (Stage) ─────────────────────────── */
        .player-stage {
            flex: 1;
            position: relative;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
            background: radial-gradient(circle at 50% 50%, #0d0f2b 0%, #060714 100%);
        }

        /* Ambient Glowing Orbs */
        .orb-violet {
            position: absolute;
            width: 380px; height: 380px;
            top: -100px; left: -100px;
            background: radial-gradient(circle, rgba(124,58,237,0.3) 0%, transparent 70%);
            border-radius: 50%;
            pointer-events: none;
        }
        .orb-cyan {
            position: absolute;
            width: 320px; height: 320px;
            bottom: -80px; right: -80px;
            background: radial-gradient(circle, rgba(34,211,238,0.25) 0%, transparent 70%);
            border-radius: 50%;
            pointer-events: none;
        }

        /* Big Center Play Overlay */
        .big-play-overlay {
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(6, 7, 20, 0.65);
            backdrop-filter: blur(8px);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            z-index: 30;
            cursor: pointer;
            transition: opacity 0.3s ease;
        }
        .big-play-btn {
            width: 84px; height: 84px;
            border-radius: 50%;
            background: linear-gradient(135deg, #7c3aed, #22d3ee);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2.2rem;
            color: #ffffff;
            box-shadow: 0 0 35px rgba(34, 211, 238, 0.7);
            border: 2px solid rgba(255, 255, 255, 0.3);
            transition: transform 0.25s, box-shadow 0.25s;
        }
        .big-play-btn:hover {
            transform: scale(1.1);
            box-shadow: 0 0 50px rgba(34, 211, 238, 0.9);
        }
        .big-play-text {
            margin-top: 14px;
            font-size: 1.05rem;
            font-weight: 800;
            color: #f1f5f9;
            letter-spacing: 0.5px;
        }

        /* ── Dynamic Scene Container ──────────────────────── */
        .scene-content {
            width: 90%;
            height: 90%;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            z-index: 5;
            transition: opacity 0.35s ease, transform 0.35s ease;
        }

        /* Cards & Scene Layouts */
        .scene-card {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.12);
            border-radius: 18px;
            padding: 22px 28px;
            width: 100%;
            max-width: 800px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.4);
            animation: cardPopIn 0.4s cubic-bezier(0.22, 1, 0.36, 1) both;
        }
        @keyframes cardPopIn {
            from { opacity: 0; transform: scale(0.94); }
            to   {{ opacity: 1; transform: scale(1); }}
        }

        .hero-title {
            font-size: 2rem;
            font-weight: 900;
            background: linear-gradient(90deg, #f1f5f9, #22d3ee, #a3e635);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 6px;
        }

        .metrics-grid {
            display: flex;
            gap: 14px;
            width: 100%;
            margin-top: 14px;
        }
        .metric-cell {
            flex: 1;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 14px;
            padding: 14px 10px;
            text-align: center;
        }
        .metric-cell-val {
            font-size: 1.85rem;
            font-weight: 900;
            color: #f1f5f9;
        }
        .metric-cell-val.green { color: #4ade80; text-shadow: 0 0 16px rgba(74, 222, 128, 0.6); }
        .metric-cell-val.red   { color: #fb7185; text-shadow: 0 0 16px rgba(251, 113, 133, 0.6); }
        .metric-cell-lbl {
            font-size: 0.72rem;
            color: rgba(241, 245, 249, 0.55);
            margin-top: 4px;
            text-transform: uppercase;
            font-weight: 600;
        }

        /* Revision Drift Alert Siren */
        .drift-siren-box {
            background: linear-gradient(135deg, rgba(239, 68, 68, 0.28), rgba(251, 191, 36, 0.18));
            border: 2px solid #ef4444;
            border-radius: 18px;
            padding: 22px 28px;
            width: 100%;
            max-width: 800px;
            text-align: center;
            box-shadow: 0 0 35px rgba(239, 68, 68, 0.45);
            animation: sirenAlert 1s infinite alternate;
        }
        @keyframes sirenAlert {
            0%   { border-color: #ef4444; box-shadow: 0 0 20px rgba(239, 68, 68, 0.3); }
            100% {{ border-color: #fbbf24; box-shadow: 0 0 45px rgba(251, 191, 36, 0.65); }}
        }

        /* ── Subtitle Narration Bar ───────────────────────── */
        .subtitles-banner {
            width: 100%;
            background: rgba(10, 12, 28, 0.94);
            border-top: 1px solid rgba(34, 211, 238, 0.25);
            padding: 10px 24px;
            font-size: 0.95rem;
            font-weight: 600;
            line-height: 1.45;
            text-align: center;
            color: #f1f5f9;
            min-height: 48px;
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10;
        }
        .subtitles-banner strong { color: #22d3ee; }
        .subtitles-banner em { color: #fbbf24; font-style: normal; font-weight: 700; }

        /* ── Bottom Controls Bar ──────────────────────────── */
        .player-controls {
            padding: 10px 20px 14px;
            background: rgba(12, 14, 32, 0.95);
            display: flex;
            flex-direction: column;
            gap: 8px;
            z-index: 10;
        }
        .scrubber-track {
            width: 100%;
            height: 6px;
            background: rgba(255, 255, 255, 0.12);
            border-radius: 100px;
            cursor: pointer;
            position: relative;
            overflow: hidden;
        }
        .scrubber-fill {
            height: 100%;
            width: 0%;
            background: linear-gradient(90deg, #7c3aed, #22d3ee, #a3e635);
            border-radius: 100px;
            transition: width 0.08s linear;
        }

        .controls-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-size: 0.85rem;
        }
        .controls-left, .controls-right {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .ctrl-btn {
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 8px;
            color: #f1f5f9;
            padding: 6px 14px;
            font-size: 0.82rem;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.2s;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }
        .ctrl-btn:hover {
            background: rgba(34, 211, 238, 0.25);
            border-color: #22d3ee;
            color: #22d3ee;
            transform: translateY(-1px);
        }
        .btn-play-toggle {
            background: linear-gradient(135deg, #7c3aed, #22d3ee) !important;
            border: none !important;
            color: #fff !important;
            padding: 7px 18px !important;
            border-radius: 10px !important;
            box-shadow: 0 4px 14px rgba(34, 211, 238, 0.4);
        }
        .btn-play-toggle:hover {
            transform: scale(1.05) translateY(-1px) !important;
            box-shadow: 0 6px 20px rgba(34, 211, 238, 0.6) !important;
        }

        .timecode {
            font-family: monospace;
            font-size: 0.85rem;
            font-weight: 700;
            color: rgba(241, 245, 249, 0.7);
        }
      </style>
    </head>
    <body>

    <div class="cinema-container">
        <!-- Top Bar -->
        <div class="player-topbar">
            <div class="topbar-left">
                <span class="topbar-icon">🛡️</span>
                <span class="topbar-title">Public Health Claim Watchdog</span>
                <span class="topbar-badge">DEMO WALKTHROUGH</span>
            </div>
            <div class="rec-indicator">
                <div class="rec-dot"></div>
                <span>REC READY · 1080p</span>
            </div>
        </div>

        <!-- Video Stage -->
        <div class="player-stage" id="player-stage">
            <div class="orb-violet"></div>
            <div class="orb-cyan"></div>

            <!-- Big Center Play Button Overlay -->
            <div class="big-play-overlay" id="big-play-overlay">
                <div class="big-play-btn">▶</div>
                <div class="big-play-text">PLAY DEMO WALKTHROUGH</div>
            </div>

            <!-- Scene Dynamic Wrapper -->
            <div class="scene-content" id="scene-content">
                <!-- Scenes injected by JS -->
            </div>
        </div>

        <!-- Subtitles CC Banner -->
        <div class="subtitles-banner" id="subtitles-banner">
            Click <strong>▶ PLAY DEMO</strong> to start autonomous walkthrough...
        </div>

        <!-- Bottom Controls -->
        <div class="player-controls">
            <div class="scrubber-track" id="scrubber-track">
                <div class="scrubber-fill" id="scrubber-fill"></div>
            </div>
            <div class="controls-row">
                <div class="controls-left">
                    <button class="ctrl-btn btn-play-toggle" id="btn-play">▶ Play</button>
                    <div class="timecode" id="timecode-display">0:00 / 1:18</div>
                </div>
                <div class="controls-right">
                    <button class="ctrl-btn" id="btn-replay">🔄 Replay</button>
                    <button class="ctrl-btn" id="btn-skip">⏭️ Next Scene</button>
                </div>
            </div>
        </div>
    </div>

    <script>
    (function() {
        const TOTAL_DURATION = 78; // 78 seconds

        const SCENES = [
            // Scene 1: Platform & Mission
            {
                start: 0, end: 10,
                subtitle: "👋 Welcome to <strong>Public Health Claim Watchdog</strong> — a deterministic, open-source engine verifying public health statements against official government HMIS datasets.",
                html: `
                    <div class="scene-card" style="text-align:center">
                        <div style="font-size:3.2rem;margin-bottom:8px">🛡️</div>
                        <div class="hero-title">Public Health Claim Watchdog</div>
                        <div style="color:rgba(241,245,249,0.7);font-size:1.05rem;margin-bottom:14px">
                            Transparent Evidence · Deterministic Math · Bilingual · 100% Free
                        </div>
                        <div style="display:flex;gap:10px;justify-content:center">
                            <span class="topbar-badge">📍 Tamil Nadu Scope</span>
                            <span class="topbar-badge">📊 Official HMIS Schema</span>
                            <span class="topbar-badge">🌱 SDG 3 & 16 Aligned</span>
                        </div>
                    </div>
                `
            },

            // Scene 2: The Health Claim
            {
                start: 10, end: 20,
                subtitle: "📋 Examining illustrative claim <strong>CLM-001</strong>: <em>'Full immunization coverage in Coimbatore rose by 8.5% between 2021 and 2022'</em>.",
                html: `
                    <div class="scene-card" style="border-left: 6px solid #8E54E9; text-align: left;">
                        <span class="topbar-badge" style="background:rgba(142,84,233,0.3);color:#d8b4fe">🏷️ Illustrative Claim on Simulated Data</span>
                        <div style="font-size:1.35rem;font-weight:800;color:#f1f5f9;margin:12px 0 16px;line-height:1.4">
                            "Full immunization coverage in Coimbatore rose by 8.5% between 2021 and 2022"
                        </div>
                        <div style="display:flex;gap:16px;color:rgba(241,245,249,0.6);font-size:0.85rem">
                            <span>👤 District Health Officer</span>
                            <span>📍 Coimbatore</span>
                            <span>📊 Full Immunization</span>
                            <span>📅 2021 → 2022</span>
                        </div>
                    </div>
                `
            },

            // Scene 3: Release 1 Provisional Verdict (Supported)
            {
                start: 20, end: 32,
                subtitle: "✅ Under provisional <strong>Release 1</strong>, coverage rose from 74.2% to 83.8% (<strong>+9.6%</strong>). Within our ±1.5% tolerance, the claim is initially <em>SUPPORTED</em>.",
                html: `
                    <div style="width:100%;max-width:800px">
                        <div style="display:flex;align-items:center;justify-content:center;gap:14px;margin-bottom:12px">
                            <span style="font-size:3.2rem">✅</span>
                            <div>
                                <div style="font-size:1.6rem;font-weight:900;color:#4ade80;letter-spacing:1px">SUPPORTED</div>
                                <div style="font-size:0.8rem;color:rgba(241,245,249,0.5)">PROVISIONAL RELEASE 1 (DEC 2022)</div>
                            </div>
                        </div>
                        <div class="metrics-grid">
                            <div class="metric-cell">
                                <div class="metric-cell-val">74.2%</div>
                                <div class="metric-cell-lbl">📅 2021 Baseline</div>
                            </div>
                            <div class="metric-cell">
                                <div class="metric-cell-val">83.8%</div>
                                <div class="metric-cell-lbl">📅 2022 Outcome</div>
                            </div>
                            <div class="metric-cell" style="border-color:rgba(74,222,128,0.4)">
                                <div class="metric-cell-val green">+9.6%</div>
                                <div class="metric-cell-lbl">📈 Net Delta (Matches ±1.5%)</div>
                            </div>
                        </div>
                    </div>
                `
            },

            // Scene 4: Verifiable Evidence & Regional Translations
            {
                start: 32, end: 44,
                subtitle: "📊 Full transparency: Every parameter is calculated in a <strong>Verifiable Evidence Table</strong>, paired with draft explanations in <strong>Tamil (தமிழ்)</strong> and <strong>Hindi (हिंदी)</strong>.",
                html: `
                    <div style="display:flex;gap:14px;width:100%;max-width:800px">
                        <div class="scene-card" style="flex:1.2;text-align:left;padding:16px 20px">
                            <div style="font-size:1rem;font-weight:800;color:#22d3ee;margin-bottom:10px">📊 Verifiable Evidence Table</div>
                            <table style="width:100%;font-size:0.82rem;color:rgba(241,245,249,0.85);border-collapse:collapse">
                                <tr style="border-bottom:1px solid rgba(255,255,255,0.08)"><td style="padding:5px 0">District / Indicator</td><td style="font-weight:700">Coimbatore · Immunization</td></tr>
                                <tr style="border-bottom:1px solid rgba(255,255,255,0.08)"><td style="padding:5px 0">Computed Change</td><td style="font-weight:700;color:#4ade80">+9.6%</td></tr>
                                <tr style="border-bottom:1px solid rgba(255,255,255,0.08)"><td style="padding:5px 0">Direction Matched</td><td style="font-weight:700">✅ True (Increase)</td></tr>
                                <tr><td style="padding:5px 0">Quality Checks</td><td style="font-weight:700;color:#4ade80">✅ PASS (5/5 Checks)</td></tr>
                            </table>
                        </div>
                        <div class="scene-card" style="flex:1;text-align:left;padding:16px 20px">
                            <div style="font-size:1rem;font-weight:800;color:#a3e635;margin-bottom:8px">🗣️ Regional Accessibility</div>
                            <div style="display:flex;gap:6px;margin-bottom:8px">
                                <span class="topbar-badge" style="background:rgba(163,230,53,0.2);color:#a3e635">🇬🇧 EN</span>
                                <span class="topbar-badge">🇮🇳 தமிழ்</span>
                                <span class="topbar-badge">🇮🇳 हिंदी</span>
                            </div>
                            <div style="font-size:0.8rem;color:rgba(241,245,249,0.7);line-height:1.5">
                                "கோயம்புத்தூரில் முழு தடுப்பூசி அளவு 74.2% லிருந்து 83.8% ஆக (+9.6%) உயர்ந்துள்ளது..."
                            </div>
                        </div>
                    </div>
                `
            },

            // Scene 5: The Turning Point — Revision Drift!
            {
                start: 44, end: 58,
                subtitle: "🚨 <strong>REVISION DRIFT DETECTED!</strong> Audited Release 2 reconciles coverage to 75.5% → 78.9% (+3.4%). The claim quietly flipped from SUPPORTED to <em>UNSUPPORTED</em>!",
                html: `
                    <div class="drift-siren-box">
                        <div style="font-size:2.8rem;margin-bottom:4px">🚨</div>
                        <div style="font-size:1.6rem;font-weight:900;color:#fbbf24;letter-spacing:0.5px">REVISION DRIFT DETECTED</div>
                        <div style="font-size:1.15rem;font-weight:800;color:#fb7185;margin:6px 0">Verdict Shifted: SUPPORTED ➔ UNSUPPORTED</div>
                        <div style="font-size:0.9rem;color:rgba(241,245,249,0.85);margin:10px 0 14px;line-height:1.5">
                            🟡 Provisional: <strong>+9.6%</strong> &nbsp;➔&nbsp; 🟢 Audited: <strong>+3.4%</strong><br>
                            <em>Published figures are sometimes revised upon routine data auditing, and claims quoted earlier may no longer match.</em>
                        </div>
                        <span class="topbar-badge" style="background:rgba(239,68,68,0.3);color:#fca5a5;padding:5px 14px;font-size:0.8rem">
                            Few tools re-check published claims when underlying data changes!
                        </span>
                    </div>
                `
            },

            // Scene 6: Reviewer Sign-Off & Session Audit Trail
            {
                start: 58, end: 68,
                subtitle: "🧑‍💼 Human-in-the-loop: The reviewer documents the drift finding, signs off with notes, and commits the decision to the <strong>Session Audit Trail</strong> with 1-click CSV export.",
                html: `
                    <div class="scene-card" style="text-align:left;max-width:800px">
                        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
                            <div style="font-size:1.1rem;font-weight:800;color:#22d3ee">🧑‍💼 Fact-Check Desk Sign-Off</div>
                            <span class="topbar-badge" style="background:rgba(74,222,128,0.2);color:#4ade80">✅ APPROVED & LOGGED</span>
                        </div>
                        <div style="font-size:0.88rem;color:rgba(241,245,249,0.8);background:rgba(255,255,255,0.06);padding:12px;border-radius:10px;margin-bottom:10px">
                            <strong>Reviewer:</strong> Chief Fact-Checker<br>
                            <strong>Notes:</strong> Confirmed revision drift on Release 2. Reconciled delta (+3.4%) fails tolerance for CLM-001 (+8.5%). Logged for editorial update.
                        </div>
                        <div style="font-size:0.75rem;color:rgba(241,245,249,0.5)">
                            📁 Saved to session_audit_log.csv · Exportable in 1-click
                        </div>
                    </div>
                `
            },

            // Scene 7: Wrap-up & SDG Alignment
            {
                start: 68, end: 78,
                subtitle: "🎉 <strong>Demo Complete!</strong> Open source, deterministic, zero-cost, and built for <strong>SDG 3</strong> (Good Health) & <strong>SDG 16</strong> (Strong Institutions).",
                html: `
                    <div class="scene-card" style="text-align:center">
                        <div style="font-size:3rem;margin-bottom:6px">🎉</div>
                        <div class="hero-title">Public Health Claim Watchdog</div>
                        <div style="font-size:1.02rem;color:rgba(241,245,249,0.85);margin-bottom:14px">
                            Deterministic Verification · Revision Drift Detection · Open Science
                        </div>
                        <div style="display:flex;gap:12px;justify-content:center;margin-bottom:14px">
                            <span class="topbar-badge" style="padding:5px 14px;font-size:0.8rem">🌱 SDG 3: Good Health & Well-Being</span>
                            <span class="topbar-badge" style="padding:5px 14px;font-size:0.8rem">⚖️ SDG 16: Transparency & Accountability</span>
                        </div>
                        <div style="font-size:0.8rem;color:rgba(241,245,249,0.5)">
                            Ready for journalists, health watchdogs, and public scrutiny!
                        </div>
                    </div>
                `
            }
        ];

        let isPlaying = false;
        let currentTime = 0;
        let lastTimestamp = 0;
        let animId = null;
        let activeSceneIndex = -1;

        const stage = document.getElementById('player-stage');
        const bigOverlay = document.getElementById('big-play-overlay');
        const sceneContent = document.getElementById('scene-content');
        const subtitlesBanner = document.getElementById('subtitles-banner');
        const scrubberFill = document.getElementById('scrubber-fill');
        const scrubberTrack = document.getElementById('scrubber-track');
        const timecodeDisplay = document.getElementById('timecode-display');
        const btnPlay = document.getElementById('btn-play');
        const btnReplay = document.getElementById('btn-replay');
        const btnSkip = document.getElementById('btn-skip');

        function formatTime(s) {
            const m = Math.floor(s / 60);
            const sec = Math.floor(s % 60);
            return `${m}:${sec < 10 ? '0' : ''}${sec}`;
        }

        function renderScene(t) {
            const idx = SCENES.findIndex(sc => t >= sc.start && t < sc.end);
            if (idx !== -1 && idx !== activeSceneIndex) {
                activeSceneIndex = idx;
                sceneContent.innerHTML = SCENES[idx].html;
                subtitlesBanner.innerHTML = SCENES[idx].subtitle;
            }
        }

        function loop(now) {
            if (!isPlaying) return;

            const dt = (now - lastTimestamp) / 1000;
            lastTimestamp = now;
            currentTime += dt;

            if (currentTime >= TOTAL_DURATION) {
                currentTime = TOTAL_DURATION;
                pause();
                return;
            }

            const pct = (currentTime / TOTAL_DURATION) * 100;
            scrubberFill.style.width = `${pct}%`;
            timecodeDisplay.innerText = `${formatTime(currentTime)} / ${formatTime(TOTAL_DURATION)}`;

            renderScene(currentTime);
            animId = requestAnimationFrame(loop);
        }

        function play() {
            isPlaying = true;
            bigOverlay.style.opacity = '0';
            setTimeout(() => { bigOverlay.style.display = 'none'; }, 300);
            btnPlay.innerText = '⏸ Pause';
            btnPlay.style.background = 'rgba(255, 255, 255, 0.15)';
            lastTimestamp = performance.now();
            animId = requestAnimationFrame(loop);
        }

        function pause() {
            isPlaying = false;
            if (animId) cancelAnimationFrame(animId);
            btnPlay.innerText = '▶ Play';
            btnPlay.style.background = 'linear-gradient(135deg, #7c3aed, #22d3ee)';
        }

        function replay() {
            pause();
            currentTime = 0;
            activeSceneIndex = -1;
            scrubberFill.style.width = '0%';
            renderScene(0);
            play();
        }

        function skipNext() {
            if (activeSceneIndex < SCENES.length - 1) {
                currentTime = SCENES[activeSceneIndex + 1].start;
                renderScene(currentTime);
            }
        }

        bigOverlay.onclick = play;
        btnPlay.onclick = () => { if (isPlaying) pause(); else play(); };
        btnReplay.onclick = replay;
        btnSkip.onclick = skipNext;

        scrubberTrack.onclick = (e) => {
            const rect = scrubberTrack.getBoundingClientRect();
            const clickRatio = (e.clientX - rect.left) / rect.width;
            currentTime = Math.max(0, Math.min(TOTAL_DURATION, clickRatio * TOTAL_DURATION));
            scrubberFill.style.width = `${(currentTime / TOTAL_DURATION) * 100}%`;
            timecodeDisplay.innerText = `${formatTime(currentTime)} / ${formatTime(TOTAL_DURATION)}`;
            renderScene(currentTime);
        };

        // Render Initial Scene (Ready)
        renderScene(0);
    })();
    </script>
    </body>
    </html>
    """
