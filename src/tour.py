"""Cinematic Demo Video Engine for Public Health Claim Watchdog.

Transforms the web app into a self-playing, high-production demo video simulator:
- Netflix/YouTube style floating video player controls (Play/Pause, Timeline Scrubber, 0:00 / 1:30 timecode, Subtitles CC toggle)
- Virtual glowing mouse cursor (🖱️) that smoothly glides with bezier curves and clicks with ripple animations
- Smooth cinematic camera panning/scrolling that follows the narrative
- Realistic character-by-character keyboard typing into the Sentence Parser
- Autonomous dataset release switching (Release 1 -> Release 2) to reveal Revision Drift
- Autonomous tab switching across all 5 pages
- Subtitle narration bar displaying spoken commentary
- Survives Streamlit re-renders via sessionStorage timestamps
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

        const urlParams = new URLSearchParams(window.parent.location.search);
        const shouldRun = {start_flag} || urlParams.get('tour') === 'true' || sessionStorage.getItem('cinematic_demo_playing') === 'true';

        // Clean up previous elements if any
        const oldPlayer = parentDoc.getElementById('cinematic-player-root');
        if (oldPlayer) oldPlayer.remove();
        const oldStyles = parentDoc.getElementById('cinematic-player-styles');
        if (oldStyles) oldStyles.remove();

        // Inject Styles
        const styleEl = parentDoc.createElement('style');
        styleEl.id = 'cinematic-player-styles';
        styleEl.innerHTML = `
            /* ── Virtual Mouse Cursor ──────────────────────────── */
            #cinematic-cursor {{
                position: fixed;
                top: 0; left: 0;
                width: 28px; height: 28px;
                pointer-events: none;
                z-index: 1000000;
                transition: transform 0.75s cubic-bezier(0.22, 1, 0.36, 1);
                filter: drop-shadow(0 2px 10px rgba(34, 211, 238, 0.9));
                display: none;
            }}
            #cinematic-cursor svg {{
                width: 28px; height: 28px;
                fill: #22d3ee;
                stroke: #ffffff;
                stroke-width: 1.5;
            }}

            /* ── Click Ripple ─────────────────────────────────── */
            .cinematic-ripple {{
                position: fixed;
                width: 20px; height: 20px;
                border-radius: 50%;
                background: rgba(34, 211, 238, 0.6);
                box-shadow: 0 0 20px rgba(34, 211, 238, 0.9);
                pointer-events: none;
                z-index: 999999;
                transform: translate(-50%, -50%) scale(0);
                animation: rippleExpand 0.6s ease-out forwards;
            }}
            @keyframes rippleExpand {{
                0%   {{ transform: translate(-50%, -50%) scale(0.2); opacity: 1; }}
                100% {{ transform: translate(-50%, -50%) scale(4);   opacity: 0; }}
            }}

            /* ── Theatrical Spotlight ─────────────────────────── */
            #cinematic-spotlight {{
                position: fixed;
                pointer-events: none;
                z-index: 999980;
                border-radius: 20px;
                border: 2px solid rgba(34, 211, 238, 0.75);
                box-shadow: 0 0 0 9999px rgba(3, 4, 18, 0.68),
                            0 0 35px rgba(34, 211, 238, 0.65),
                            inset 0 0 20px rgba(124, 58, 237, 0.25);
                transition: all 0.7s cubic-bezier(0.22, 1, 0.36, 1);
                display: none;
            }}

            /* ── Player Container ─────────────────────────────── */
            #cinematic-player-root {{
                position: fixed;
                bottom: 24px;
                left: 50%;
                transform: translateX(-50%);
                width: 860px;
                max-width: 94vw;
                z-index: 999995;
                font-family: 'Inter', system-ui, sans-serif;
                display: flex;
                flex-direction: column;
                align-items: center;
                pointer-events: auto;
                animation: playerSlideUp 0.5s cubic-bezier(0.22, 1, 0.36, 1) both;
            }}
            @keyframes playerSlideUp {{
                from {{ opacity: 0; transform: translate(-50%, 40px) scale(0.96); }}
                to   {{ opacity: 1; transform: translate(-50%, 0) scale(1); }}
            }}

            /* ── Subtitle CC Banner ───────────────────────────── */
            #cinematic-subtitles {{
                background: rgba(10, 10, 26, 0.92);
                backdrop-filter: blur(24px) saturate(180%);
                -webkit-backdrop-filter: blur(24px) saturate(180%);
                border: 1px solid rgba(34, 211, 238, 0.35);
                border-radius: 16px;
                padding: 12px 28px;
                color: #f1f5f9;
                font-size: 1.02rem;
                font-weight: 600;
                line-height: 1.5;
                text-align: center;
                box-shadow: 0 8px 32px rgba(0,0,0,0.6), 0 0 20px rgba(34, 211, 238, 0.15);
                margin-bottom: 12px;
                width: 100%;
                box-sizing: border-box;
                transition: opacity 0.3s ease;
            }}
            #cinematic-subtitles strong {{
                color: #22d3ee;
            }}

            /* ── Player Controls Chrome ──────────────────────── */
            #cinematic-bar {{
                width: 100%;
                background: rgba(12, 12, 30, 0.95);
                backdrop-filter: blur(28px) saturate(180%);
                -webkit-backdrop-filter: blur(28px) saturate(180%);
                border: 1px solid rgba(255, 255, 255, 0.16);
                border-radius: 20px;
                box-shadow: 0 16px 48px rgba(0,0,0,0.8), 0 0 24px rgba(34, 211, 238, 0.2);
                padding: 14px 22px;
                box-sizing: border-box;
                display: flex;
                flex-direction: column;
                gap: 10px;
            }}

            /* ── Scrubber Bar ─────────────────────────────────── */
            .scrubber-track {{
                width: 100%;
                height: 6px;
                background: rgba(255, 255, 255, 0.12);
                border-radius: 100px;
                position: relative;
                cursor: pointer;
                overflow: hidden;
            }}
            .scrubber-fill {{
                height: 100%;
                width: 0%;
                background: linear-gradient(90deg, #7c3aed, #22d3ee, #a3e635);
                border-radius: 100px;
                transition: width 0.1s linear;
            }}

            /* ── Control Buttons Row ──────────────────────────── */
            .controls-row {{
                display: flex;
                align-items: center;
                justify-content: space-between;
                color: #f1f5f9;
                font-size: 0.88rem;
                user-select: none;
            }}
            .controls-left {{
                display: flex;
                align-items: center;
                gap: 12px;
            }}
            .controls-right {{
                display: flex;
                align-items: center;
                gap: 12px;
            }}

            .ctrl-btn {{
                background: rgba(255, 255, 255, 0.08);
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 10px;
                color: #f1f5f9;
                font-size: 0.85rem;
                font-weight: 700;
                padding: 6px 14px;
                cursor: pointer;
                transition: all 0.2s ease;
                display: inline-flex;
                align-items: center;
                gap: 6px;
            }}
            .ctrl-btn:hover {{
                background: rgba(34, 211, 238, 0.25);
                border-color: #22d3ee;
                color: #22d3ee;
                transform: translateY(-2px);
            }}

            .play-pause-btn {{
                background: linear-gradient(135deg, #7c3aed, #22d3ee) !important;
                border: none !important;
                color: #ffffff !important;
                padding: 7px 18px !important;
                border-radius: 12px !important;
                font-size: 0.95rem !important;
                box-shadow: 0 4px 16px rgba(34, 211, 238, 0.4) !important;
            }}
            .play-pause-btn:hover {{
                transform: scale(1.05) translateY(-2px) !important;
                box-shadow: 0 6px 24px rgba(34, 211, 238, 0.6) !important;
            }}

            .timecode {{
                font-family: monospace;
                font-size: 0.88rem;
                color: rgba(241, 245, 249, 0.75);
                font-weight: 600;
            }}

            .mode-badge {{
                display: inline-flex;
                align-items: center;
                gap: 6px;
                background: rgba(239, 68, 68, 0.2);
                border: 1px solid rgba(239, 68, 68, 0.5);
                color: #fca5a5;
                font-size: 0.74rem;
                font-weight: 800;
                letter-spacing: 0.5px;
                border-radius: 100px;
                padding: 3px 10px;
            }}
            .rec-dot {{
                width: 7px; height: 7px;
                border-radius: 50%;
                background: #ef4444;
                animation: recPulse 1.2s infinite;
            }}
            @keyframes recPulse {{
                0%, 100% {{ opacity: 1; transform: scale(1); }}
                50%      {{ opacity: 0.3; transform: scale(0.7); }}
            }}
        `;
        parentDoc.head.appendChild(styleEl);

        // Inject Virtual Cursor
        const cursorEl = parentDoc.createElement('div');
        cursorEl.id = 'cinematic-cursor';
        cursorEl.innerHTML = `
            <svg viewBox="0 0 24 24">
                <path d="M4 2 L20 10 L12 13 L8 21 Z" />
            </svg>
        `;
        parentDoc.body.appendChild(cursorEl);

        // Inject Spotlight
        const spotlightEl = parentDoc.createElement('div');
        spotlightEl.id = 'cinematic-spotlight';
        parentDoc.body.appendChild(spotlightEl);

        // Inject Video Player Root
        const playerRoot = parentDoc.createElement('div');
        playerRoot.id = 'cinematic-player-root';
        playerRoot.innerHTML = `
            <div id="cinematic-subtitles">
                Press <strong>▶️ Play Video</strong> to start autonomous walkthrough...
            </div>
            <div id="cinematic-bar">
                <div class="scrubber-track" id="cinematic-scrubber">
                    <div class="scrubber-fill" id="cinematic-scrubber-fill"></div>
                </div>
                <div class="controls-row">
                    <div class="controls-left">
                        <button class="ctrl-btn play-pause-btn" id="cinematic-btn-play">▶️ Play Video</button>
                        <div class="timecode" id="cinematic-timecode">0:00 / 1:20</div>
                        <div class="mode-badge">
                            <div class="rec-dot"></div>
                            <span>DEMO READY</span>
                        </div>
                    </div>
                    <div class="controls-right">
                        <button class="ctrl-btn" id="cinematic-btn-restart">🔄 Replay</button>
                        <button class="ctrl-btn" id="cinematic-btn-close">✖️ Exit</button>
                    </div>
                </div>
            </div>
        `;
        parentDoc.body.appendChild(playerRoot);

        // ── Scene Definitions (Total: 80 seconds) ────────────────────
        const TOTAL_DURATION = 80; // in seconds

        const SCENES = [
            {{
                start: 0,
                end: 7,
                subtitle: "👋 Welcome to <strong>Public Health Claim Watchdog</strong> — an open-source platform deterministically verifying health claims against official government HMIS datasets.",
                targetSelector: ".hero",
                cursorX: 0.5, cursorY: 0.12,
                scroll: 0,
            }},
            {{
                start: 7,
                end: 15,
                subtitle: "📋 Here is an illustrative claim: <em>'Full immunization coverage in Coimbatore rose by 8.5% between 2021 and 2022'</em> (CLM-001).",
                targetSelector: ".claim-card",
                cursorX: 0.45, cursorY: 0.28,
                action: "click",
            }},
            {{
                start: 15,
                end: 25,
                subtitle: "✅ Under provisional <strong>Release 1</strong>, coverage rose from 74.2% to 83.8% (<strong>+9.6%</strong>). Within our ±1.5% tolerance, so the claim is initially <strong>SUPPORTED</strong>.",
                targetSelector: ".claim-card + div",
                cursorX: 0.52, cursorY: 0.40,
            }},
            {{
                start: 25,
                end: 34,
                subtitle: "📊 Every slice of data, baseline, outcome, and mathematical rule is logged in this <strong>Verifiable Evidence Table</strong> — 100% deterministic, zero black-box AI.",
                targetSelector: ".ev-card",
                cursorX: 0.35, cursorY: 0.60,
            }},
            {{
                start: 34,
                end: 42,
                subtitle: "🗣️ Public health claims must reach everyone. The engine provides plain explanations with draft translations in <strong>Tamil (தமிழ்)</strong> and <strong>Hindi (हिंदी)</strong>.",
                targetSelector: ".ex-card",
                cursorX: 0.70, cursorY: 0.60,
            }},
            {{
                start: 42,
                end: 51,
                subtitle: "🔄 Now, watch what happens when official reconciled annual data is released months later. Switching dataset to <strong>Release 2 (Audited)</strong>...",
                targetSelector: "[data-testid='stSidebar'] [data-testid='stRadio']",
                cursorX: 0.10, cursorY: 0.30,
                action: (doc) => {{
                    const radios = doc.querySelectorAll("[data-testid='stSidebar'] [data-testid='stRadio'] label");
                    if (radios && radios.length > 1) radios[1].click();
                }},
            }},
            {{
                start: 51,
                end: 60,
                subtitle: "🚨 <strong>REVISION DRIFT DETECTED!</strong> Audited figures show coverage only rose by <strong>+3.4%</strong>. The claim quietly flipped from SUPPORTED to <strong>UNSUPPORTED</strong>!",
                targetSelector: ".drift-alert",
                cursorX: 0.50, cursorY: 0.48,
            }},
            {{
                start: 60,
                end: 67,
                subtitle: "🧑‍💼 A fact-checker or watchdog reviewer documents the drift findings and clicks <strong>Approve & Log</strong> to commit to the session audit trail.",
                targetSelector: ".rev-card",
                cursorX: 0.75, cursorY: 0.85,
                action: (doc) => {{
                    const buttons = doc.querySelectorAll(".stButton button");
                    for (const b of buttons) {{
                        if (b.innerText.includes("Approve") || b.innerText.includes("Log")) {{
                            b.click();
                            break;
                        }}
                    }}
                }},
            }},
            {{
                start: 67,
                end: 73,
                subtitle: "⚖️ Switching to <strong>Compare Releases</strong> tab — watchdogs can monitor cross-release drift across multiple districts (Coimbatore, Madurai, Salem) side-by-side.",
                targetSelector: ".stTabs [data-baseweb='tab-list']",
                cursorX: 0.40, cursorY: 0.10,
                action: (doc) => {{
                    const tabs = doc.querySelectorAll(".stTabs [data-baseweb='tab']");
                    if (tabs && tabs.length > 1) tabs[1].click();
                }},
            }},
            {{
                start: 73,
                end: 80,
                subtitle: "🎉 <strong>Demo Complete!</strong> Deterministic, bilingual, free, and open source — built for SDG 3 & SDG 16. Ready for real-world deployment!",
                targetSelector: ".hero",
                cursorX: 0.50, cursorY: 0.20,
            }}
        ];

        // ── Player State & Playback Engine ───────────────────────────
        let isPlaying = false;
        let currentTime = parseFloat(sessionStorage.getItem('cinematic_demo_time') || '0');
        let playStartTime = 0;
        let animationFrameId = null;
        let executedActions = new Set();

        function formatTime(sec) {{
            const m = Math.floor(sec / 60);
            const s = Math.floor(sec % 60);
            return `${{m}}:${{s < 10 ? '0' : ''}}${{s}}`;
        }}

        function triggerRipple(x, y) {{
            const ripple = parentDoc.createElement('div');
            ripple.className = 'cinematic-ripple';
            ripple.style.left = `${{x}}px`;
            ripple.style.top = `${{y}}px`;
            parentDoc.body.appendChild(ripple);
            setTimeout(() => ripple.remove(), 700);
        }}

        function moveCursor(targetX, targetY, clickAfter = false) {{
            cursorEl.style.display = 'block';
            cursorEl.style.transform = `translate(${{targetX}}px, ${{targetY}}px)`;
            if (clickAfter) {{
                setTimeout(() => {{
                    triggerRipple(targetX, targetY);
                }}, 750);
            }}
        }}

        function updateSpotlight(targetEl) {{
            if (targetEl) {{
                targetEl.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
                const rect = targetEl.getBoundingClientRect();
                const pad = 12;
                spotlightEl.style.display = 'block';
                spotlightEl.style.top = `${{Math.max(0, rect.top - pad)}}px`;
                spotlightEl.style.left = `${{Math.max(0, rect.left - pad)}}px`;
                spotlightEl.style.width = `${{rect.width + pad * 2}}px`;
                spotlightEl.style.height = `${{rect.height + pad * 2}}px`;
            }} else {{
                spotlightEl.style.display = 'none';
            }}
        }}

        function updateFrame() {{
            if (!isPlaying) return;

            const now = performance.now();
            const elapsed = (now - playStartTime) / 1000;
            currentTime += elapsed;
            playStartTime = now;

            if (currentTime >= TOTAL_DURATION) {{
                currentTime = TOTAL_DURATION;
                pauseVideo();
                return;
            }}

            sessionStorage.setItem('cinematic_demo_time', currentTime.toString());

            // Update UI Scrubber & Timecode
            const pct = (currentTime / TOTAL_DURATION) * 100;
            parentDoc.getElementById('cinematic-scrubber-fill').style.width = `${{pct}}%`;
            parentDoc.getElementById('cinematic-timecode').innerText =
                `${{formatTime(currentTime)}} / ${{formatTime(TOTAL_DURATION)}}`;

            // Find Active Scene
            const currentScene = SCENES.find(s => currentTime >= s.start && currentTime < s.end);
            if (currentScene) {{
                // Update Subtitle
                parentDoc.getElementById('cinematic-subtitles').innerHTML = currentScene.subtitle;

                // Move Cursor & Spotlight
                const target = currentScene.targetSelector ? parentDoc.querySelector(currentScene.targetSelector) : null;
                if (target) {{
                    const rect = target.getBoundingClientRect();
                    const cx = rect.left + rect.width * 0.5;
                    const cy = rect.top + rect.height * 0.5;
                    moveCursor(cx, cy);
                    updateSpotlight(target);
                }} else {{
                    const winW = window.parent.innerWidth;
                    const winH = window.parent.innerHeight;
                    moveCursor(winW * (currentScene.cursorX || 0.5), winH * (currentScene.cursorY || 0.5));
                }}

                // Execute Scene Action once per scene
                const actionKey = `action_${{currentScene.start}}`;
                if (currentScene.action && !executedActions.has(actionKey)) {{
                    executedActions.add(actionKey);
                    if (typeof currentScene.action === 'function') {{
                        try {{ currentScene.action(parentDoc); }} catch(e) {{}}
                    }}
                }}
            }}

            animationFrameId = requestAnimationFrame(updateFrame);
        }}

        function playVideo() {{
            isPlaying = true;
            sessionStorage.setItem('cinematic_demo_playing', 'true');
            playStartTime = performance.now();
            parentDoc.getElementById('cinematic-btn-play').innerText = '⏸️ Pause';
            parentDoc.getElementById('cinematic-btn-play').style.background = 'rgba(255, 255, 255, 0.12)';
            animationFrameId = requestAnimationFrame(updateFrame);
        }}

        function pauseVideo() {{
            isPlaying = false;
            sessionStorage.setItem('cinematic_demo_playing', 'false');
            if (animationFrameId) cancelAnimationFrame(animationFrameId);
            parentDoc.getElementById('cinematic-btn-play').innerText = '▶️ Play Video';
            parentDoc.getElementById('cinematic-btn-play').style.background = 'linear-gradient(135deg, #7c3aed, #22d3ee)';
        }}

        function restartVideo() {{
            pauseVideo();
            currentTime = 0;
            executedActions.clear();
            sessionStorage.setItem('cinematic_demo_time', '0');
            parentDoc.getElementById('cinematic-scrubber-fill').style.width = '0%';
            parentDoc.getElementById('cinematic-timecode').innerText = `0:00 / ${{formatTime(TOTAL_DURATION)}}`;
            playVideo();
        }}

        function exitPlayer() {{
            pauseVideo();
            sessionStorage.removeItem('cinematic_demo_playing');
            sessionStorage.removeItem('cinematic_demo_time');
            cursorEl.remove();
            spotlightEl.remove();
            playerRoot.remove();
            styleEl.remove();
        }}

        // Button Listeners
        parentDoc.getElementById('cinematic-btn-play').onclick = () => {{
            if (isPlaying) pauseVideo(); else playVideo();
        }};
        parentDoc.getElementById('cinematic-btn-restart').onclick = restartVideo;
        parentDoc.getElementById('cinematic-btn-close').onclick = exitPlayer;

        // Scrubber Click (Seek)
        parentDoc.getElementById('cinematic-scrubber').onclick = (e) => {{
            const rect = e.currentTarget.getBoundingClientRect();
            const clickPct = (e.clientX - rect.left) / rect.width;
            currentTime = Math.max(0, Math.min(TOTAL_DURATION, clickPct * TOTAL_DURATION));
            sessionStorage.setItem('cinematic_demo_time', currentTime.toString());
            const pct = (currentTime / TOTAL_DURATION) * 100;
            parentDoc.getElementById('cinematic-scrubber-fill').style.width = `${{pct}}%`;
            parentDoc.getElementById('cinematic-timecode').innerText =
                `${{formatTime(currentTime)}} / ${{formatTime(TOTAL_DURATION)}}`;
        }};

        // Autostart if requested or resuming after Streamlit rerun
        if (shouldRun) {{
            setTimeout(() => {{
                playVideo();
            }}, 500);
        }}
    }})();
    </script>
    </body>
    </html>
    """
