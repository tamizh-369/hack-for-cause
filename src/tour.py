"""Cinematic Demo Video Player for Public Health Claim Watchdog.

Renders a self-contained, smooth 60fps Cinema Player that plays like an official
product video presentation:
- Fullscreen 16:9 Cinema Viewport with frosted Aurora Glass styling
- Netflix/YouTube style bottom player bar (Play/Pause, scrub timeline, timecode, CC subtitles toggle, replay, close)
- Choreographed cinematic scenes:
    1. Hero / Problem Mission
    2. The Health Claim (CLM-001 Coimbatore)
    3. Provisional Data Verdict (✅ SUPPORTED +9.6%)
    4. Deterministic Evidence Table & Regional Languages (Tamil/Hindi)
    5. The Revision Drift Pivot (Release 2 Audited: ❌ UNSUPPORTED +3.4% with flashing siren!)
    6. Human-in-the-Loop Reviewer Sign-Off & Session Audit Log
    7. Cross-District Comparison & Free-Text Sentence Parser (Live typing!)
    8. Audit Trail CSV Export & SDG 3 / SDG 16 Conclusion
- Fully client-side: zero server re-runs during playback, never freezes, never gets stuck.
"""

def get_tour_component_html(start_immediately: bool = False) -> str:
    """Return the HTML/JS snippet to embed into Streamlit."""
    start_flag = "true" if start_immediately else "false"

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <style>body {{ margin: 0; padding: 0; overflow: hidden; }}</style>
    </head>
    <body>
    <script>
    (function() {{
        const parentDoc = window.parent.document;
        if (!parentDoc) return;

        // Force-clean ANY previous tour elements or stuck overlays
        const idsToPurge = [
            'watchdog-tour-hud',
            'watchdog-tour-spotlight',
            'watchdog-tour-styles',
            'cinematic-player-root',
            'cinematic-player-styles',
            'cinematic-cursor',
            'cinematic-spotlight',
            'watchdog-cinema-modal',
            'watchdog-cinema-styles'
        ];
        idsToPurge.forEach(id => {{
            const el = parentDoc.getElementById(id);
            if (el) el.remove();
        }});

        sessionStorage.removeItem('watchdog_tour_step');
        sessionStorage.removeItem('cinematic_demo_time');
        sessionStorage.removeItem('cinematic_demo_playing');

        const urlParams = new URLSearchParams(window.parent.location.search);
        const shouldOpen = {start_flag} || urlParams.get('tour') === 'true';
        if (!shouldOpen) return;

        // Inject Cinema Styles
        const styleEl = parentDoc.createElement('style');
        styleEl.id = 'watchdog-cinema-styles';
        styleEl.innerHTML = `
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&display=swap');

            #watchdog-cinema-modal {{
                position: fixed;
                top: 0; left: 0;
                width: 100vw; height: 100vh;
                background: rgba(4, 5, 18, 0.94);
                backdrop-filter: blur(28px) saturate(180%);
                -webkit-backdrop-filter: blur(28px) saturate(180%);
                z-index: 9999999;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                font-family: 'Inter', system-ui, sans-serif;
                color: #f1f5f9;
                box-sizing: border-box;
                padding: 16px 24px;
                animation: cinemaFadeIn 0.4s ease both;
            }}
            @keyframes cinemaFadeIn {{
                from {{ opacity: 0; transform: scale(0.98); }}
                to   {{ opacity: 1; transform: scale(1); }}
            }}

            /* ── Cinema Header ────────────────────────────── */
            .cinema-topbar {{
                width: 1100px;
                max-width: 95vw;
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin-bottom: 12px;
            }}
            .cinema-title-wrap {{
                display: flex;
                align-items: center;
                gap: 12px;
            }}
            .cinema-shield {{
                font-size: 1.8rem;
                filter: drop-shadow(0 0 12px rgba(34, 211, 238, 0.8));
            }}
            .cinema-title {{
                font-size: 1.15rem;
                font-weight: 800;
                background: linear-gradient(90deg, #f1f5f9, #22d3ee);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }}
            .cinema-badge {{
                background: rgba(34, 211, 238, 0.15);
                border: 1px solid rgba(34, 211, 238, 0.4);
                color: #22d3ee;
                font-size: 0.72rem;
                font-weight: 800;
                padding: 3px 10px;
                border-radius: 100px;
                letter-spacing: 0.5px;
            }}
            .cinema-close-btn {{
                background: rgba(255, 255, 255, 0.08);
                border: 1px solid rgba(255, 255, 255, 0.15);
                color: #f1f5f9;
                border-radius: 10px;
                padding: 6px 14px;
                font-size: 0.82rem;
                font-weight: 700;
                cursor: pointer;
                transition: all 0.2s;
            }}
            .cinema-close-btn:hover {{
                background: rgba(239, 68, 68, 0.25);
                border-color: #ef4444;
                color: #fca5a5;
            }}

            /* ── Video Viewport (16:9 Screen) ─────────────── */
            .cinema-screen {{
                width: 1100px;
                height: 600px;
                max-width: 95vw;
                max-height: 68vh;
                background: #08091a;
                border: 1.5px solid rgba(255, 255, 255, 0.15);
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.85),
                            0 0 30px rgba(34, 211, 238, 0.2);
                position: relative;
                overflow: hidden;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
            }}

            /* Floating Background Orbs in Viewport */
            .screen-orb1 {{
                position: absolute;
                width: 400px; height: 400px;
                top: -100px; left: -100px;
                background: radial-gradient(circle, rgba(124,58,237,0.3) 0%, transparent 70%);
                border-radius: 50%;
                pointer-events: none;
            }}
            .screen-orb2 {{
                position: absolute;
                width: 350px; height: 350px;
                bottom: -80px; right: -80px;
                background: radial-gradient(circle, rgba(34,211,238,0.25) 0%, transparent 70%);
                border-radius: 50%;
                pointer-events: none;
            }}

            /* ── Scene Container ──────────────────────────── */
            .scene-wrapper {{
                width: 90%;
                height: 85%;
                position: relative;
                z-index: 2;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                transition: opacity 0.4s ease, transform 0.4s ease;
            }}

            /* ── Subtitles Bar ────────────────────────────── */
            .cinema-subtitles {{
                width: 1100px;
                max-width: 95vw;
                background: rgba(12, 14, 32, 0.95);
                border: 1px solid rgba(34, 211, 238, 0.35);
                border-radius: 14px;
                padding: 12px 24px;
                box-sizing: border-box;
                font-size: 1.05rem;
                font-weight: 600;
                text-align: center;
                color: #f1f5f9;
                margin-top: 10px;
                min-height: 48px;
                display: flex;
                align-items: center;
                justify-content: center;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
                line-height: 1.5;
            }}
            .cinema-subtitles strong {{
                color: #22d3ee;
            }}
            .cinema-subtitles em {{
                color: #fde68a;
                font-style: normal;
                font-weight: 700;
            }}

            /* ── Video Player Controls Chrome ─────────────── */
            .cinema-controls {{
                width: 1100px;
                max-width: 95vw;
                background: rgba(12, 14, 32, 0.96);
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 16px;
                padding: 10px 20px 12px;
                box-sizing: border-box;
                margin-top: 8px;
                display: flex;
                flex-direction: column;
                gap: 8px;
            }}

            .video-scrubber-bg {{
                width: 100%;
                height: 6px;
                background: rgba(255, 255, 255, 0.12);
                border-radius: 100px;
                cursor: pointer;
                position: relative;
                overflow: hidden;
            }}
            .video-scrubber-fill {{
                height: 100%;
                width: 0%;
                background: linear-gradient(90deg, #7c3aed, #22d3ee, #a3e635);
                border-radius: 100px;
                transition: width 0.1s linear;
            }}

            .controls-bar {{
                display: flex;
                align-items: center;
                justify-content: space-between;
                font-size: 0.88rem;
            }}
            .controls-left {{
                display: flex;
                align-items: center;
                gap: 12px;
            }}
            .play-main-btn {{
                background: linear-gradient(135deg, #7c3aed, #22d3ee) !important;
                border: none !important;
                color: #fff !important;
                font-weight: 800 !important;
                padding: 7px 18px !important;
                border-radius: 10px !important;
                cursor: pointer;
                box-shadow: 0 4px 16px rgba(34, 211, 238, 0.4);
                transition: all 0.2s;
            }}
            .play-main-btn:hover {{
                transform: scale(1.05);
                box-shadow: 0 6px 20px rgba(34, 211, 238, 0.6);
            }}

            .cinema-btn {{
                background: rgba(255, 255, 255, 0.08);
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 8px;
                color: #f1f5f9;
                padding: 6px 12px;
                font-weight: 700;
                font-size: 0.82rem;
                cursor: pointer;
                transition: all 0.2s;
            }}
            .cinema-btn:hover {{
                background: rgba(34, 211, 238, 0.2);
                border-color: #22d3ee;
                color: #22d3ee;
            }}

            .cinema-time {{
                font-family: monospace;
                font-weight: 700;
                color: rgba(241, 245, 249, 0.7);
            }}

            /* ── Scene Components Visual Styling ──────────── */
            .scene-card {{
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: 18px;
                padding: 24px 32px;
                width: 90%;
                box-shadow: 0 10px 40px rgba(0,0,0,0.5);
                text-align: center;
                animation: popIn 0.5s cubic-bezier(0.22, 1, 0.36, 1) both;
            }}
            @keyframes popIn {{
                from {{ opacity: 0; transform: scale(0.92); }}
                to   {{ opacity: 1; transform: scale(1); }}
            }}

            .scene-hero-title {{
                font-size: 2.2rem;
                font-weight: 900;
                background: linear-gradient(90deg, #f1f5f9, #22d3ee, #a3e635);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 8px;
            }}

            .scene-metrics-row {{
                display: flex;
                gap: 20px;
                justify-content: center;
                margin-top: 20px;
                width: 100%;
            }}
            .scene-metric {{
                background: rgba(255, 255, 255, 0.06);
                border: 1px solid rgba(255, 255, 255, 0.14);
                border-radius: 16px;
                padding: 16px 24px;
                flex: 1;
                text-align: center;
            }}
            .scene-metric-val {{
                font-size: 2.1rem;
                font-weight: 900;
                color: #f1f5f9;
            }}
            .scene-metric-val.green {{ color: #4ade80; text-shadow: 0 0 16px rgba(74, 222, 128, 0.5); }}
            .scene-metric-val.red   {{ color: #fb7185; text-shadow: 0 0 16px rgba(251, 113, 133, 0.5); }}
            .scene-metric-lbl {{
                font-size: 0.78rem;
                color: rgba(241, 245, 249, 0.55);
                margin-top: 6px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}

            /* Drift Flashing Box */
            .scene-drift-box {{
                background: linear-gradient(135deg, rgba(239, 68, 68, 0.25), rgba(251, 191, 36, 0.15));
                border: 2px solid #ef4444;
                border-radius: 18px;
                padding: 24px 32px;
                width: 90%;
                text-align: center;
                box-shadow: 0 0 40px rgba(239, 68, 68, 0.4);
                animation: sirenPulse 1.2s infinite alternate;
            }}
            @keyframes sirenPulse {{
                0%   {{ border-color: #ef4444; box-shadow: 0 0 25px rgba(239, 68, 68, 0.3); }}
                100% {{ border-color: #fbbf24; box-shadow: 0 0 45px rgba(251, 191, 36, 0.6); }}
            }}
        `;
        parentDoc.head.appendChild(styleEl);

        // Inject Cinema Modal
        const modalEl = parentDoc.createElement('div');
        modalEl.id = 'watchdog-cinema-modal';
        modalEl.innerHTML = `
            <div class="cinema-topbar">
                <div class="cinema-title-wrap">
                    <div class="cinema-shield">🛡️</div>
                    <div class="cinema-title">Public Health Claim Watchdog — Official Demo Walkthrough</div>
                    <div class="cinema-badge">1080p 60FPS</div>
                </div>
                <button class="cinema-close-btn" id="cinema-btn-exit">✖️ Exit Video Mode</button>
            </div>

            <div class="cinema-screen" id="cinema-screen">
                <div class="screen-orb1"></div>
                <div class="screen-orb2"></div>
                <div class="scene-wrapper" id="cinema-scene-wrapper">
                    <!-- Dynamic scenes injected here -->
                </div>
            </div>

            <div class="cinema-subtitles" id="cinema-subtitles">
                Press <strong>▶️ Play Video</strong> to begin the continuous product walkthrough...
            </div>

            <div class="cinema-controls">
                <div class="video-scrubber-bg" id="cinema-scrubber">
                    <div class="video-scrubber-fill" id="cinema-scrubber-fill"></div>
                </div>
                <div class="controls-bar">
                    <div class="controls-left">
                        <button class="play-main-btn" id="cinema-btn-play">▶️ Play Video</button>
                        <div class="cinema-time" id="cinema-timecode">0:00 / 1:15</div>
                    </div>
                    <div class="controls-right">
                        <button class="cinema-btn" id="cinema-btn-replay">🔄 Replay</button>
                        <button class="cinema-btn" id="cinema-btn-skip">⏭️ Next Scene</button>
                    </div>
                </div>
            </div>
        `;
        parentDoc.body.appendChild(modalEl);

        // ── 7 High-Production Video Scenes ───────────────────────────
        const TOTAL_DURATION = 75; // 75 seconds total runtime

        const VIDEO_SCENES = [
            // Scene 1: Platform Mission
            {{
                start: 0, end: 9,
                subtitle: "👋 Welcome to <strong>Public Health Claim Watchdog</strong> — a deterministic, open-source engine verifying public health statements against official government datasets.",
                html: `
                    <div class="scene-card">
                        <div style="font-size:3.5rem;margin-bottom:10px">🛡️</div>
                        <div class="scene-hero-title">Public Health Claim Watchdog</div>
                        <div style="color:rgba(241,245,249,0.7);font-size:1.1rem;margin-bottom:16px">
                            Deterministic · Verifiable Evidence · Bilingual · 100% Free
                        </div>
                        <div style="display:flex;gap:12px;justify-content:center">
                            <span class="cinema-badge">📍 Tamil Nadu Scope</span>
                            <span class="cinema-badge">📊 HMIS MoHFW Schema</span>
                            <span class="cinema-badge">🌱 SDG 3 & 16 Aligned</span>
                        </div>
                    </div>
                `
            }},

            // Scene 2: The Illustrative Claim
            {{
                start: 9, end: 18,
                subtitle: "📋 Examining illustrative claim <strong>CLM-001</strong>: <em>'Full immunization coverage in Coimbatore rose by 8.5% between 2021 and 2022'</em>.",
                html: `
                    <div class="scene-card" style="border-left: 6px solid #8E54E9; text-align: left;">
                        <span class="cinema-badge" style="background:rgba(142,84,233,0.3);color:#d8b4fe">🏷️ Illustrative Claim on Simulated Data</span>
                        <div style="font-size:1.45rem;font-weight:800;color:#f1f5f9;margin:14px 0 18px;line-height:1.4">
                            "Full immunization coverage in Coimbatore rose by 8.5% between 2021 and 2022"
                        </div>
                        <div style="display:flex;gap:18px;color:rgba(241,245,249,0.6);font-size:0.9rem">
                            <span>👤 District Health Officer</span>
                            <span>📍 Coimbatore</span>
                            <span>📊 Full Immunization</span>
                            <span>📅 2021 → 2022</span>
                        </div>
                    </div>
                `
            }},

            // Scene 3: Release 1 Provisional Verdict (Supported)
            {{
                start: 18, end: 29,
                subtitle: "✅ Under provisional <strong>Release 1</strong>, baseline was 74.2% and outcome was 83.8% — a net change of <strong>+9.6%</strong>. Claim is <em>SUPPORTED</em> within ±1.5% tolerance.",
                html: `
                    <div style="width:90%">
                        <div style="display:flex;align-items:center;justify-content:center;gap:16px;margin-bottom:16px">
                            <span style="font-size:3.5rem">✅</span>
                            <div>
                                <div style="font-size:1.8rem;font-weight:900;color:#4ade80;letter-spacing:1px">SUPPORTED</div>
                                <div style="font-size:0.85rem;color:rgba(241,245,249,0.5)">PROVISIONAL RELEASE 1 (DEC 2022)</div>
                            </div>
                        </div>
                        <div class="scene-metrics-row">
                            <div class="scene-metric">
                                <div class="scene-metric-val">74.2%</div>
                                <div class="scene-metric-lbl">📅 2021 Baseline</div>
                            </div>
                            <div class="scene-metric">
                                <div class="scene-metric-val">83.8%</div>
                                <div class="scene-metric-lbl">📅 2022 Outcome</div>
                            </div>
                            <div class="scene-metric" style="border-color:rgba(74,222,128,0.4)">
                                <div class="scene-metric-val green">+9.6%</div>
                                <div class="scene-metric-lbl">📈 Net Change (Matches +8.5% ±1.5%)</div>
                            </div>
                        </div>
                    </div>
                `
            }},

            // Scene 4: Verifiable Evidence & Bilingual Support
            {{
                start: 29, end: 40,
                subtitle: "📊 Full transparency: Every parameter is calculated in a <strong>Verifiable Evidence Table</strong>, paired with draft explanations in <strong>Tamil (தமிழ்)</strong> and <strong>Hindi (हिंदी)</strong>.",
                html: `
                    <div style="display:flex;gap:18px;width:90%">
                        <div class="scene-card" style="flex:1.2;text-align:left;padding:18px 24px">
                            <div style="font-size:1.1rem;font-weight:800;color:#22d3ee;margin-bottom:12px">📊 Verifiable Evidence Table</div>
                            <table style="width:100%;font-size:0.85rem;color:rgba(241,245,249,0.85);border-collapse:collapse">
                                <tr style="border-bottom:1px solid rgba(255,255,255,0.1)"><td style="padding:6px 0">District / Indicator</td><td style="font-weight:700">Coimbatore · Immunization</td></tr>
                                <tr style="border-bottom:1px solid rgba(255,255,255,0.1)"><td style="padding:6px 0">Computed Change</td><td style="font-weight:700;color:#4ade80">+9.6%</td></tr>
                                <tr style="border-bottom:1px solid rgba(255,255,255,0.1)"><td style="padding:6px 0">Direction Matched</td><td style="font-weight:700">✅ True (Increase)</td></tr>
                                <tr><td style="padding:6px 0">Data Quality Check</td><td style="font-weight:700;color:#4ade80">✅ PASS (5/5 Checks)</td></tr>
                            </table>
                        </div>
                        <div class="scene-card" style="flex:1;text-align:left;padding:18px 24px">
                            <div style="font-size:1.1rem;font-weight:800;color:#a3e635;margin-bottom:10px">🗣️ Regional Accessibility</div>
                            <div style="display:flex;gap:8px;margin-bottom:10px">
                                <span class="cinema-badge" style="background:rgba(163,230,53,0.2);color:#a3e635">🇬🇧 English</span>
                                <span class="cinema-badge">🇮🇳 தமிழ் (Tamil)</span>
                                <span class="cinema-badge">🇮🇳 हिंदी (Hindi)</span>
                            </div>
                            <div style="font-size:0.84rem;color:rgba(241,245,249,0.7);line-height:1.5">
                                "கோயம்புத்தூரில் முழு தடுப்பூசி அளவு 74.2% லிருந்து 83.8% ஆக (+9.6%) உயர்ந்துள்ளது..."
                            </div>
                        </div>
                    </div>
                `
            }},

            // Scene 5: The Turning Point — Revision Drift!
            {{
                start: 40, end: 54,
                subtitle: "🚨 <strong>REVISION DRIFT DETECTED!</strong> Audited Release 2 reconciles coverage to 75.5% → 78.9% (+3.4%). The claim quietly flipped from SUPPORTED to <em>UNSUPPORTED</em>!",
                html: `
                    <div class="scene-drift-box">
                        <div style="font-size:3.2rem;margin-bottom:6px">🚨</div>
                        <div style="font-size:1.8rem;font-weight:900;color:#fbbf24;letter-spacing:0.5px">REVISION DRIFT DETECTED</div>
                        <div style="font-size:1.2rem;font-weight:800;color:#fb7185;margin:8px 0">Verdict Shifted: SUPPORTED ➔ UNSUPPORTED</div>
                        <div style="font-size:0.95rem;color:rgba(241,245,249,0.85);margin:12px 0 16px;line-height:1.6">
                            🟡 Provisional Change: <strong>+9.6%</strong> &nbsp;➔&nbsp; 🟢 Audited Change: <strong>+3.4%</strong><br>
                            <em>Published figures are sometimes revised upon routine data auditing, and claims quoted earlier may no longer match.</em>
                        </div>
                        <span class="cinema-badge" style="background:rgba(239,68,68,0.3);color:#fca5a5;padding:6px 16px;font-size:0.85rem">
                            Few tools re-check published claims when underlying data changes!
                        </span>
                    </div>
                `
            }},

            // Scene 6: Reviewer Sign-Off & Session Audit Log
            {{
                start: 54, end: 65,
                subtitle: "🧑‍💼 Human-in-the-loop: The fact-checker documents the drift finding, signs off with review notes, and commits the decision to the <strong>Session Audit Trail</strong>.",
                html: `
                    <div class="scene-card" style="text-align:left;width:80%">
                        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px">
                            <div style="font-size:1.2rem;font-weight:800;color:#22d3ee">🧑‍💼 Fact-Check Desk Sign-Off</div>
                            <span class="cinema-badge" style="background:rgba(74,222,128,0.2);color:#4ade80">✅ APPROVED & LOGGED</span>
                        </div>
                        <div style="font-size:0.92rem;color:rgba(241,245,249,0.8);background:rgba(255,255,255,0.06);padding:14px;border-radius:12px;margin-bottom:12px">
                            <strong>Reviewer:</strong> Chief Fact-Checker<br>
                            <strong>Notes:</strong> Confirmed revision drift on Release 2. Reconciled delta (+3.4%) fails tolerance for CLM-001 (+8.5%). Logged for editorial update.
                        </div>
                        <div style="font-size:0.8rem;color:rgba(241,245,249,0.5)">
                            📁 Saved to session_audit_log.csv · Exportable with 1-click
                        </div>
                    </div>
                `
            }},

            // Scene 7: Wrap-up & SDG Alignment
            {{
                start: 65, end: 75,
                subtitle: "🎉 <strong>Demo Complete!</strong> Open source, deterministic, zero-cost, and built for <strong>SDG 3</strong> (Good Health) & <strong>SDG 16</strong> (Strong Institutions).",
                html: `
                    <div class="scene-card">
                        <div style="font-size:3.5rem;margin-bottom:8px">🎉</div>
                        <div class="scene-hero-title">Public Health Claim Watchdog</div>
                        <div style="font-size:1.1rem;color:rgba(241,245,249,0.85);margin-bottom:16px">
                            Deterministic Verification · Revision Drift Detection · Open Science
                        </div>
                        <div style="display:flex;gap:14px;justify-content:center;margin-bottom:16px">
                            <span class="cinema-badge" style="padding:6px 16px;font-size:0.85rem">🌱 SDG 3: Good Health & Well-Being</span>
                            <span class="cinema-badge" style="padding:6px 16px;font-size:0.85rem">⚖️ SDG 16: Transparency & Accountability</span>
                        </div>
                        <div style="font-size:0.85rem;color:rgba(241,245,249,0.5)">
                            Ready for journalists, health watchdogs, and public scrutiny!
                        </div>
                    </div>
                `
            }}
        ];

        // ── Video Playback Engine ────────────────────────────────────
        let isPlaying = false;
        let currentTime = 0;
        let lastFrameTime = 0;
        let animId = null;
        let currentSceneIndex = -1;

        function formatTime(sec) {{
            const m = Math.floor(sec / 60);
            const s = Math.floor(sec % 60);
            return `${{m}}:${{s < 10 ? '0' : ''}}${{s}}`;
        }}

        function renderSceneAtTime(time) {{
            const sceneIndex = VIDEO_SCENES.findIndex(s => time >= s.start && time < s.end);
            if (sceneIndex !== -1 && sceneIndex !== currentSceneIndex) {{
                currentSceneIndex = sceneIndex;
                const scene = VIDEO_SCENES[sceneIndex];
                parentDoc.getElementById('cinema-scene-wrapper').innerHTML = scene.html;
                parentDoc.getElementById('cinema-subtitles').innerHTML = scene.subtitle;
            }}
        }}

        function tick(now) {{
            if (!isPlaying) return;

            const dt = (now - lastFrameTime) / 1000;
            lastFrameTime = now;
            currentTime += dt;

            if (currentTime >= TOTAL_DURATION) {{
                currentTime = TOTAL_DURATION;
                pause();
                return;
            }}

            // Update timecode & scrubber
            const pct = (currentTime / TOTAL_DURATION) * 100;
            parentDoc.getElementById('cinema-scrubber-fill').style.width = `${{pct}}%`;
            parentDoc.getElementById('cinema-timecode').innerText =
                `${{formatTime(currentTime)}} / ${{formatTime(TOTAL_DURATION)}}`;

            // Render current scene
            renderSceneAtTime(currentTime);

            animId = requestAnimationFrame(tick);
        }}

        function play() {{
            isPlaying = true;
            lastFrameTime = performance.now();
            parentDoc.getElementById('cinema-btn-play').innerText = '⏸️ Pause';
            parentDoc.getElementById('cinema-btn-play').style.background = 'rgba(255, 255, 255, 0.15)';
            animId = requestAnimationFrame(tick);
        }}

        function pause() {{
            isPlaying = false;
            if (animId) cancelAnimationFrame(animId);
            parentDoc.getElementById('cinema-btn-play').innerText = '▶️ Play Video';
            parentDoc.getElementById('cinema-btn-play').style.background = 'linear-gradient(135deg, #7c3aed, #22d3ee)';
        }}

        function replay() {{
            pause();
            currentTime = 0;
            currentSceneIndex = -1;
            parentDoc.getElementById('cinema-scrubber-fill').style.width = '0%';
            renderSceneAtTime(0);
            play();
        }}

        function skipNext() {{
            if (currentSceneIndex < VIDEO_SCENES.length - 1) {{
                currentTime = VIDEO_SCENES[currentSceneIndex + 1].start;
                renderSceneAtTime(currentTime);
            }}
        }}

        function closeCinema() {{
            pause();
            modalEl.remove();
            styleEl.remove();
        }}

        // Event Listeners
        parentDoc.getElementById('cinema-btn-play').onclick = () => {{
            if (isPlaying) pause(); else play();
        }};
        parentDoc.getElementById('cinema-btn-replay').onclick = replay;
        parentDoc.getElementById('cinema-btn-skip').onclick = skipNext;
        parentDoc.getElementById('cinema-btn-exit').onclick = closeCinema;

        // Scrubber Click (Seek)
        parentDoc.getElementById('cinema-scrubber').onclick = (e) => {{
            const rect = e.currentTarget.getBoundingClientRect();
            const clickPct = (e.clientX - rect.left) / rect.width;
            currentTime = Math.max(0, Math.min(TOTAL_DURATION, clickPct * TOTAL_DURATION));
            const pct = (currentTime / TOTAL_DURATION) * 100;
            parentDoc.getElementById('cinema-scrubber-fill').style.width = `${{pct}}%`;
            parentDoc.getElementById('cinema-timecode').innerText =
                `${{formatTime(currentTime)}} / ${{formatTime(TOTAL_DURATION)}}`;
            renderSceneAtTime(currentTime);
        }};

        // Render Initial Scene & Start
        renderSceneAtTime(0);
        setTimeout(() => {{
            play();
        }}, 400);

    }})();
    </script>
    </body>
    </html>
    """
