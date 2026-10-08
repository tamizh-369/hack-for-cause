"""Interactive Tour Guide Engine for Public Health Claim Watchdog.

Injects an autonomous, self-typing, animated dialogue HUD into the Streamlit DOM.
Survives Streamlit re-runs via sessionStorage, highlights elements with an animated
theatrical spotlight, types character-by-character into inputs, and switches tabs automatically.
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

        // Check if query param or start flag asks to start
        const urlParams = new URLSearchParams(window.parent.location.search);
        const autoStart = {start_flag} || urlParams.get('tour') === 'true' || parentDoc.getElementById('watchdog-trigger-tour');

        // Check if tour already initialized on parent
        if (parentDoc.getElementById('watchdog-tour-hud') && !window.parent.__restartTour) {{
            return;
        }}

        // Clean up previous tour elements if restarting
        const oldHud = parentDoc.getElementById('watchdog-tour-hud');
        if (oldHud) oldHud.remove();
        const oldSpotlight = parentDoc.getElementById('watchdog-tour-spotlight');
        if (oldSpotlight) oldSpotlight.remove();
        const oldStyles = parentDoc.getElementById('watchdog-tour-styles');
        if (oldStyles) oldStyles.remove();

        // Inject Tour Styles
        const styleEl = parentDoc.createElement('style');
        styleEl.id = 'watchdog-tour-styles';
        styleEl.innerHTML = `
            #watchdog-tour-spotlight {{
                position: fixed;
                pointer-events: none;
                z-index: 999990;
                border-radius: 18px;
                border: 2.5px solid #22d3ee;
                box-shadow: 0 0 0 9999px rgba(3, 4, 18, 0.72),
                            0 0 35px rgba(34, 211, 238, 0.75),
                            inset 0 0 20px rgba(124, 58, 237, 0.35);
                transition: all 0.65s cubic-bezier(0.22, 1, 0.36, 1);
                display: none;
            }}

            #watchdog-tour-hud {{
                position: fixed;
                bottom: 24px;
                left: 50%;
                transform: translateX(-50%);
                width: 780px;
                max-width: 92vw;
                background: rgba(10, 10, 26, 0.92);
                backdrop-filter: blur(28px) saturate(180%);
                -webkit-backdrop-filter: blur(28px) saturate(180%);
                border: 1.5px solid rgba(34, 211, 238, 0.45);
                border-radius: 22px;
                box-shadow: 0 16px 50px rgba(0, 0, 0, 0.8),
                            0 0 30px rgba(34, 211, 238, 0.25);
                color: #f1f5f9;
                font-family: 'Inter', system-ui, sans-serif;
                z-index: 999999;
                padding: 20px 24px 16px;
                box-sizing: border-box;
                animation: tourHudSlideUp 0.5s cubic-bezier(0.22, 1, 0.36, 1) both;
            }}

            @keyframes tourHudSlideUp {{
                from {{ opacity: 0; transform: translate(-50%, 40px) scale(0.96); }}
                to   {{ opacity: 1; transform: translate(-50%, 0) scale(1); }}
            }}

            .hud-header {{
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin-bottom: 10px;
                gap: 12px;
            }}

            .hud-badge {{
                display: flex;
                align-items: center;
                gap: 8px;
                background: linear-gradient(90deg, rgba(124,58,237,0.3), rgba(34,211,238,0.3));
                border: 1px solid rgba(34,211,238,0.4);
                border-radius: 100px;
                padding: 4px 14px;
                font-size: 0.78rem;
                font-weight: 800;
                letter-spacing: 0.5px;
                color: #22d3ee;
            }}

            .hud-wave {{
                display: inline-flex;
                align-items: center;
                gap: 3px;
                height: 12px;
            }}
            .hud-wave span {{
                width: 3px;
                background: #22d3ee;
                border-radius: 2px;
                animation: waveBar 1.2s ease-in-out infinite alternate;
            }}
            .hud-wave span:nth-child(1) {{ height: 6px; animation-delay: 0.1s; }}
            .hud-wave span:nth-child(2) {{ height: 12px; animation-delay: 0.3s; }}
            .hud-wave span:nth-child(3) {{ height: 8px; animation-delay: 0.2s; }}
            .hud-wave span:nth-child(4) {{ height: 14px; animation-delay: 0.4s; }}

            @keyframes waveBar {{
                0%   {{ transform: scaleY(0.4); }}
                100% {{ transform: scaleY(1.3); }}
            }}

            .hud-step-pill {{
                font-size: 0.75rem;
                color: rgba(241, 245, 249, 0.6);
                font-weight: 600;
            }}

            .hud-controls {{
                display: flex;
                align-items: center;
                gap: 6px;
            }}

            .hud-btn {{
                background: rgba(255, 255, 255, 0.08);
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 8px;
                color: #f1f5f9;
                font-size: 0.75rem;
                font-weight: 600;
                padding: 4px 10px;
                cursor: pointer;
                transition: all 0.2s ease;
            }}
            .hud-btn:hover {{
                background: rgba(34, 211, 238, 0.2);
                border-color: #22d3ee;
                color: #22d3ee;
                transform: translateY(-1px);
            }}

            .hud-title {{
                font-size: 1.12rem;
                font-weight: 800;
                background: linear-gradient(90deg, #22d3ee, #a3e635);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin: 0 0 6px 0;
            }}

            .hud-text {{
                font-size: 0.92rem;
                line-height: 1.55;
                color: rgba(241, 245, 249, 0.9);
                min-height: 48px;
                margin: 0 0 12px 0;
            }}

            .hud-progress-bg {{
                width: 100%;
                height: 4px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 4px;
                overflow: hidden;
            }}

            .hud-progress-fill {{
                height: 100%;
                width: 0%;
                background: linear-gradient(90deg, #7c3aed, #22d3ee, #a3e635);
                border-radius: 4px;
                transition: width 0.1s linear;
            }}
        `;
        parentDoc.head.appendChild(styleEl);

        // Inject Spotlight element
        const spotlightEl = parentDoc.createElement('div');
        spotlightEl.id = 'watchdog-tour-spotlight';
        parentDoc.body.appendChild(spotlightEl);

        // Inject HUD dialog element
        const hudEl = parentDoc.createElement('div');
        hudEl.id = 'watchdog-tour-hud';
        hudEl.innerHTML = `
            <div class="hud-header">
                <div class="hud-badge">
                    <span style="font-size:1.1rem">🛡️</span>
                    <span>WATCHDOG DEMO GUIDE</span>
                    <div class="hud-wave">
                        <span></span><span></span><span></span><span></span>
                    </div>
                </div>
                <div class="hud-step-pill" id="tour-step-counter">Step 1 of 12</div>
                <div class="hud-controls">
                    <button class="hud-btn" id="tour-btn-prev">⏮️ Prev</button>
                    <button class="hud-btn" id="tour-btn-pause">⏸️ Pause</button>
                    <button class="hud-btn" id="tour-btn-next">⏭️ Next</button>
                    <button class="hud-btn" id="tour-btn-close">✖️ Close</button>
                </div>
            </div>
            <div class="hud-title" id="tour-step-title">Loading Guide...</div>
            <div class="hud-text" id="tour-step-text">Initialising explorer walkthrough...</div>
            <div class="hud-progress-bg">
                <div class="hud-progress-fill" id="tour-progress-bar"></div>
            </div>
        `;
        parentDoc.body.appendChild(hudEl);

        // Define Tour Steps
        const TOUR_STEPS = [
            {{
                title: "🛡️ Welcome to Public Health Claim Watchdog",
                text: "We evaluate public health claims against official government datasets with 100% deterministic transparency. No black-box AI — every calculation is reproducible.",
                selector: ".hero",
                duration: 6000
            }},
            {{
                title: "📋 The Claim under Examination (CLM-001)",
                text: "Here is an illustrative claim: 'Full immunization coverage in Coimbatore rose by 8.5% between 2021 and 2022'. Notice the district, health indicator, and baseline periods.",
                selector: ".claim-card",
                duration: 6500
            }},
            {{
                title: "✅ Initial Verdict: SUPPORTED on Provisional Release 1",
                text: "Under provisional Release 1, coverage rose from 74.2% to 83.8% — a net change of +9.6%. This matches the claimed +8.5% within our ±1.5% margin of tolerance.",
                selector: ".claim-card + div",
                fallbackSelector: ".verdict-box",
                duration: 7000
            }},
            {{
                title: "📊 Verifiable Evidence Table",
                text: "Look at the Verifiable Evidence Table. Every slice of data, baseline, outcome, and mathematical rule is logged deterministically for peer audit.",
                selector: ".ev-card",
                duration: 6000
            }},
            {{
                title: "🗣️ Plain-Language & Regional Translations",
                text: "Public health claims must reach everyone. The engine provides plain explanations with draft translations in Tamil (தமிழ்) and Hindi (हिंदी).",
                selector: ".ex-card",
                duration: 6000
            }},
            {{
                title: "🔄 Switching to Audited Release 2 (Watch What Happens!)",
                text: "Now, watch what happens when official reconciled annual data is released months later. Switching to Release 2 (Audited)...",
                selector: "[data-testid='stSidebar'] [data-testid='stRadio']",
                action: (doc) => {{
                    // Autonomous click on Release 2 radio
                    const radios = doc.querySelectorAll("[data-testid='stSidebar'] [data-testid='stRadio'] label");
                    if (radios && radios.length > 1) {{
                        radios[1].click();
                    }}
                }},
                duration: 7500
            }},
            {{
                title: "🚨 REVISION DRIFT DETECTED!",
                text: "BOOM! The audited data reveals coverage only rose by +3.4%. The claim quietly flipped from SUPPORTED to UNSUPPORTED! Few tools re-check claims when data is revised.",
                selector: ".drift-alert",
                duration: 7500
            }},
            {{
                title: "🧑‍💼 Human-in-the-Loop Reviewer Sign-Off",
                text: "A fact-checker or journalist documents the drift finding and logs their decision into the session audit trail. Watch us approve...",
                selector: ".rev-card",
                action: (doc) => {{
                    // Autonomous click on Approve & Log
                    const buttons = doc.querySelectorAll(".stButton button");
                    for (const b of buttons) {{
                        if (b.innerText.includes("Approve") || b.innerText.includes("Log")) {{
                            b.click();
                            break;
                        }}
                    }}
                }},
                duration: 6500
            }},
            {{
                title: "⚖️ Cross-Release Comparison Matrix",
                text: "Switching to the Compare tab! Here, researchers can monitor cross-release drift across multiple districts (Coimbatore, Madurai, Salem) simultaneously.",
                selector: ".stTabs [data-baseweb='tab-list']",
                action: (doc) => {{
                    const tabs = doc.querySelectorAll(".stTabs [data-baseweb='tab']");
                    if (tabs && tabs.length > 1) tabs[1].click();
                }},
                duration: 6500
            }},
            {{
                title: "✍️ Free-Text Natural Language Parser",
                text: "Watch the engine parse natural language claims automatically. We will now type a fresh sentence into the parser character-by-character...",
                selector: ".stTabs [data-baseweb='tab-list']",
                action: (doc) => {{
                    // Switch to Tab 3 (Parser)
                    const tabs = doc.querySelectorAll(".stTabs [data-baseweb='tab']");
                    if (tabs && tabs.length > 2) tabs[2].click();

                    setTimeout(() => {{
                        const input = doc.querySelector(".stTextInput input");
                        if (input) {{
                            const claimSentence = "Institutional deliveries in Madurai rose by 4% between 2021 and 2022";
                            let idx = 0;
                            const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
                            nativeSetter.call(input, "");
                            input.dispatchEvent(new Event('input', {{ bubbles: true }}));

                            const typingInterval = setInterval(() => {{
                                if (idx <= claimSentence.length) {{
                                    nativeSetter.call(input, claimSentence.slice(0, idx));
                                    input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                                    idx++;
                                }} else {{
                                    clearInterval(typingInterval);
                                    input.dispatchEvent(new Event('change', {{ bubbles: true }}));
                                    setTimeout(() => {{
                                        const parseBtn = Array.from(doc.querySelectorAll(".stButton button"))
                                                              .find(b => b.innerText.includes("Parse") || b.innerText.includes("Verify"));
                                        if (parseBtn) parseBtn.click();
                                    }}, 400);
                                }}
                            }}, 35);
                        }}
                    }}, 600);
                }},
                duration: 9000
            }},
            {{
                title: "📂 Raw Data Explorer",
                text: "Auditors and public watchdogs can inspect both raw CSV releases side-by-side for full reproducibility and open science.",
                selector: ".stTabs [data-baseweb='tab-list']",
                action: (doc) => {{
                    const tabs = doc.querySelectorAll(".stTabs [data-baseweb='tab']");
                    if (tabs && tabs.length > 3) tabs[3].click();
                }},
                duration: 6000
            }},
            {{
                title: "📋 Session Audit Trail & CSV Export",
                text: "Every reviewer sign-off, verdict shift, and timestamp is immutably logged and downloadable as CSV. Ready for real-world deployment!",
                selector: ".stTabs [data-baseweb='tab-list']",
                action: (doc) => {{
                    const tabs = doc.querySelectorAll(".stTabs [data-baseweb='tab']");
                    if (tabs && tabs.length > 4) tabs[4].click();
                }},
                duration: 7000
            }},
            {{
                title: "🎉 Demo Complete — Built for SDG 3 & 16",
                text: "Transparent, bilingual, and 100% free with zero paid APIs. Thank you for watching the Public Health Claim Watchdog demonstration!",
                selector: ".hero",
                duration: 7000
            }}
        ];

        // Tour State
        let currentStep = parseInt(sessionStorage.getItem('watchdog_tour_step') || '0', 10);
        if (currentStep >= TOUR_STEPS.length) currentStep = 0;

        let isPaused = false;
        let stepTimer = null;
        let progressInterval = null;
        let typewriterTimer = null;

        function updateSpotlight(selector, fallbackSelector) {{
            let target = parentDoc.querySelector(selector);
            if (!target && fallbackSelector) {{
                target = parentDoc.querySelector(fallbackSelector);
            }}

            if (target) {{
                target.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
                const rect = target.getBoundingClientRect();
                const pad = 12;
                spotlightEl.style.display = 'block';
                spotlightEl.style.top = `${{Math.max(0, rect.top - pad)}}px`;
                spotlightEl.style.left = `${{Math.max(0, rect.left - pad)}}px`;
                spotlightEl.style.width = `${{rect.width + pad * 2}}px`;
                spotlightEl.style.height = `${{rect.height + pad * 2}}px`;
            }} else {{
                // Fallback: spotlight center of viewport
                spotlightEl.style.display = 'block';
                spotlightEl.style.top = '15%';
                spotlightEl.style.left = '10%';
                spotlightEl.style.width = '80%';
                spotlightEl.style.height = '60%';
            }}
        }}

        function typeWriter(text, element, speed = 20) {{
            if (typewriterTimer) clearInterval(typewriterTimer);
            element.innerHTML = '';
            let i = 0;
            typewriterTimer = setInterval(() => {{
                if (i < text.length) {{
                    element.innerHTML += text.charAt(i);
                    i++;
                }} else {{
                    clearInterval(typewriterTimer);
                }}
            }}, speed);
        }}

        function renderStep(idx) {{
            if (idx >= TOUR_STEPS.length) {{
                closeTour();
                return;
            }}

            const step = TOUR_STEPS[idx];
            sessionStorage.setItem('watchdog_tour_step', idx.toString());

            // Update UI elements
            parentDoc.getElementById('tour-step-counter').innerText = `Step ${{idx + 1}} of ${{TOUR_STEPS.length}}`;
            parentDoc.getElementById('tour-step-title').innerText = step.title;
            const textEl = parentDoc.getElementById('tour-step-text');
            typeWriter(step.text, textEl);

            // Execute autonomous action if defined
            if (step.action) {{
                try {{ step.action(parentDoc); }} catch (e) {{ console.error("Action error:", e); }}
            }}

            // Spotlight element
            setTimeout(() => {{
                updateSpotlight(step.selector, step.fallbackSelector);
            }}, 300);

            // Progress bar and countdown timer
            const progBar = parentDoc.getElementById('tour-progress-fill');
            const startTime = Date.now();
            const totalDuration = step.duration || 6000;

            if (stepTimer) clearTimeout(stepTimer);
            if (progressInterval) clearInterval(progressInterval);

            progressInterval = setInterval(() => {{
                if (!isPaused) {{
                    const elapsed = Date.now() - startTime;
                    const pct = Math.min(100, (elapsed / totalDuration) * 100);
                    progBar.style.width = `${{pct}}%`;
                }}
            }}, 80);

            stepTimer = setTimeout(() => {{
                if (!isPaused) {{
                    nextStep();
                }}
            }}, totalDuration);
        }}

        function nextStep() {{
            currentStep++;
            if (currentStep < TOUR_STEPS.length) {{
                renderStep(currentStep);
            }} else {{
                closeTour();
            }}
        }}

        function prevStep() {{
            currentStep = Math.max(0, currentStep - 1);
            renderStep(currentStep);
        }}

        function togglePause() {{
            isPaused = !isPaused;
            const pauseBtn = parentDoc.getElementById('tour-btn-pause');
            if (isPaused) {{
                pauseBtn.innerText = '▶️ Play';
                pauseBtn.style.color = '#a3e635';
            }} else {{
                pauseBtn.innerText = '⏸️ Pause';
                pauseBtn.style.color = '#f1f5f9';
            }}
        }}

        function closeTour() {{
            sessionStorage.removeItem('watchdog_tour_step');
            if (spotlightEl) spotlightEl.remove();
            if (hudEl) hudEl.remove();
            if (styleEl) styleEl.remove();
            if (stepTimer) clearTimeout(stepTimer);
            if (progressInterval) clearInterval(progressInterval);
            if (typewriterTimer) clearInterval(typewriterTimer);
        }}

        // Attach Button Listeners
        parentDoc.getElementById('tour-btn-next').onclick = nextStep;
        parentDoc.getElementById('tour-btn-prev').onclick = prevStep;
        parentDoc.getElementById('tour-btn-pause').onclick = togglePause;
        parentDoc.getElementById('tour-btn-close').onclick = closeTour;

        // Auto-pause when user hovers over HUD dialog
        hudEl.onmouseenter = () => {{ isPaused = true; }};
        hudEl.onmouseleave = () => {{
            const pauseBtn = parentDoc.getElementById('tour-btn-pause');
            if (pauseBtn && pauseBtn.innerText.includes("Pause")) {{
                isPaused = false;
            }}
        }};

        // Start initial step
        if (autoStart) {{
            setTimeout(() => {{
                renderStep(currentStep);
            }}, 600);
        }}
    }})();
    </script>
    </body>
    </html>
    """
