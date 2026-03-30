#!/usr/bin/env sh
#
# Copyright (C) 2026 Pocopico Trireme <https: //github.com/trireme-loader>
#
# This is free software, licensed under the MIT License.
# See /LICENSE for more information.
cat << EOF
<!DOCTYPE html>
        <html lang="en">

        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>Trireme - Assistance</title>
            <link rel="preconnect" href="https://fonts.googleapis.com">
            <link
                href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600&family=Syne:wght@400;700;800&display=swap"
                rel="stylesheet">
            <style>
                :root {
                    --bg0: #080b0f;
                    --bg1: #0d1117;
                    --bg2: #131920;
                    --bg3: #1a2230;
                    --border: #1f2d3d;
                    --border2: #2a3f55;
                    --green: #00ff88;
                    --blue: #00c4ff;
                    --amber: #ffaa00;
                    --red: #ff4455;
                    --t1: #e8edf3;
                    --t2: #8a9ab0;
                    --t3: #4a5a70;
                    --mono: 'JetBrains Mono', monospace;
                    --head: 'Syne', sans-serif;
                }

                *,
                *::before,
                *::after {
                    box-sizing: border-box;
                    margin: 0;
                    padding: 0
                }

                html,
                body {
                    background: var(--bg0);
                    color: var(--t1);
                    font-family: var(--mono);
                    min-height: 100vh;
                    overflow-x: hidden
                }

                body::before {
                    content: '';
                    position: fixed;
                    inset: 0;
                    pointer-events: none;
                    z-index: 0;
                    background-image: linear-gradient(rgba(0, 255, 136, .02) 1px, transparent 1px),
                        linear-gradient(90deg, rgba(0, 255, 136, .02) 1px, transparent 1px);
                    background-size: 40px 40px
                }

                body::after {
                    content: '';
                    position: fixed;
                    inset: 0;
                    pointer-events: none;
                    z-index: 1;
                    background: repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0, 0, 0, .06) 2px, rgba(0, 0, 0, .06) 4px)
                }

                .app {
                    position: relative;
                    z-index: 2;
                    min-height: 100vh;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    padding: 0 20px 60px
                }

                header {
                    width: 100%;
                    max-width: 900px;
                    padding: 44px 0 24px;
                    text-align: center
                }

                .logo-row {
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 14px;
                    margin-bottom: 10px
                }

                .logo-box {
                    width: 44px;
                    height: 44px;
                    border: 1.5px solid var(--green);
                    border-radius: 10px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    box-shadow: 0 0 20px rgba(0, 255, 136, .25), inset 0 0 14px rgba(0, 255, 136, .04)
                }

                h1 {
                    font-family: var(--head);
                    font-size: clamp(26px, 5vw, 42px);
                    font-weight: 800;
                    letter-spacing: -.03em
                }

                h1 em {
                    color: var(--green);
                    font-style: normal
                }

                .sub {
                    font-size: 11px;
                    color: var(--t3);
                    letter-spacing: .1em;
                    text-transform: uppercase;
                    margin-top: 5px
                }

                /* ── Direct connect banner ─────────────────────────────────────────── */
                .direct-banner {
                    width: 100%;
                    max-width: 900px;
                    background: linear-gradient(135deg, rgba(0, 255, 136, .08), rgba(0, 196, 255, .05));
                    border: 1px solid rgba(0, 255, 136, .3);
                    border-radius: 12px;
                    padding: 18px 22px;
                    margin-bottom: 18px;
                    display: none;
                    align-items: center;
                    gap: 18px;
                    flex-wrap: wrap
                }

                .direct-banner.show {
                    display: flex
                }

                .direct-pulse {
                    width: 12px;
                    height: 12px;
                    border-radius: 50%;
                    background: var(--green);
                    box-shadow: 0 0 10px var(--green);
                    flex-shrink: 0;
                    animation: blink 1.8s ease infinite
                }

                @keyframes blink {

                    0%,
                    100% {
                        opacity: 1
                    }

                    50% {
                        opacity: .3
                    }
                }

                .direct-info {
                    flex: 1
                }

                .direct-label {
                    font-size: 11px;
                    letter-spacing: .1em;
                    text-transform: uppercase;
                    color: var(--t3);
                    margin-bottom: 4px
                }

                .direct-host {
                    font-family: var(--head);
                    font-size: 18px;
                    font-weight: 700
                }

                .direct-ip {
                    font-size: 12px;
                    color: var(--green);
                    margin-top: 2px
                }
               /* ── Tooltip  ───────────────────────────────────────────────────────── */
 
                 .tooltip-trigger {
                   position: relative;
                   border-bottom: 1px dotted #333; /* Visual cue for the user */
                   cursor: help;
                 }
                 
                 .tooltip-trigger::after {
                   content: attr(data-tooltip); /* Pulls text from the HTML attribute */
                   position: absolute;
                   bottom: 125%; /* Position above the text */
                   left: 50%;
                   transform: translateX(-50%);
                   
                   /* Styling */
                   background-color: #333;
                   color: #fff;
                   padding: 5px 10px;
                   border-radius: 4px;
                   white-space: nowrap;
                   font-size: 14px;
                   
                   /* Hidden by default */
                   opacity: 0;
                   visibility: hidden;
                   transition: opacity 0.3s;
                 }
                 
                 .tooltip-trigger:hover::after {
                   opacity: 1;
                   visibility: visible;
                 }
                .tooltip-link {
                  position: relative;
                  text-decoration: none;
                  color: #007bff;
                  font-weight: bold;
                }
                
                .tooltip-link:hover {
                  text-decoration: underline;
                }
                
                /* The Tooltip Box (Hidden by default) */
                .tooltip-link::after {
                  content: attr(data-tooltip);
                  position: absolute;
                  bottom: 150%; /* Positioned higher to clear the link text */
                  left: 50%;
                  transform: translateX(-50%);
                  
                  /* Styling */
                  background-color: #222;
                  color: #fff;
                  padding: 6px 12px;
                  border-radius: 5px;
                  font-size: 12px;
                  white-space: nowrap;
                  
                  /* Animation/Visibility */
                  opacity: 0;
                  pointer-events: none; /* Prevents the tooltip from blocking clicks */
                  transition: all 0.2s ease-in-out;
                }
                
                .tooltip-link::before {
                  content: "";
                  position: absolute;
                  bottom: 120%;
                  left: 50%;
                  transform: translateX(-50%);
                  border: 6px solid transparent;
                  border-top-color: #222;
                  opacity: 0;
                  transition: all 0.2s ease-in-out;
                }
                
                /* Show both on hover */
                .tooltip-link:hover::after,
                .tooltip-link:hover::before {
                  opacity: 1;
                  bottom: 130%; /* Slight "pop-up" animation effect */
                }
                /* ── Card ──────────────────────────────────────────────────────────── */
                .card {
                    width: 100%;
                    max-width: 900px;
                    background: var(--bg1);
                    border: 1px solid var(--border);
                    border-radius: 12px;
                    overflow: hidden;
                    margin-bottom: 16px
                }

                .card-hdr {
                    padding: 13px 20px;
                    border-bottom: 1px solid var(--border);
                    background: var(--bg2);
                    display: flex;
                    align-items: center;
                    gap: 12px
                }

                .dots {
                    display: flex;
                    gap: 6px
                }

                .dots span {
                    width: 10px;
                    height: 10px;
                    border-radius: 50%
                }

                .dots .r {
                    background: #ff5f56
                }

                .dots .y {
                    background: #ffbd2e
                }

                .dots .g {
                    background: #27c93f
                }

                .card-title {
                    font-size: 11px;
                    color: var(--t3);
                    letter-spacing: .1em;
                    text-transform: uppercase;
                    flex: 1;
                    text-align: center
                }

                .card-body {
                    padding: 20px 22px
                }

                /* ── Quick-test row ─────────────────────────────────────────────────── */
                .quicktest {
                    display: flex;
                    gap: 8px;
                    align-items: center;
                    margin-bottom: 18px;
                    padding: 12px 14px;
                    background: var(--bg2);
                    border: 1px solid var(--border);
                    border-radius: 8px
                }

                .quicktest-label {
                    font-size: 10px;
                    letter-spacing: .1em;
                    text-transform: uppercase;
                    color: var(--t3);
                    white-space: nowrap
                }

                .quicktest input {
                    background: var(--bg3);
                    border: 1px solid var(--border2);
                    border-radius: 5px;
                    color: var(--t1);
                    font-family: var(--mono);
                    font-size: 12px;
                    padding: 6px 10px;
                    outline: none;
                    flex: 1;
                    transition: border-color .15s
                }

                .quicktest input:focus {
                    border-color: var(--green)
                }

                .quicktest a {
                    color: var(--yellow);
                    text-decoration: none
                   }

                .quicktest strong {
                    color: yellow
                }
                
            

                /* ── DSM card ───────────────────────────────────────────────────────── */
          
                .empty {
                    text-align: center;
                    padding: 40px 20px;
                    color: var(--t3);
                    font-size: 13px;
                    line-height: 2
                }

                .empty-icon {
                    font-size: 28px;
                    margin-bottom: 8px;
                    opacity: .35
                }

                .note {
                    width: 100%;
                    max-width: 900px;
                    border: 1px solid var(--border);
                    border-radius: 8px;
                    padding: 13px 17px;
                    font-size: 11px;
                    color: var(--t3);
                    line-height: 1.9;
                    margin-top: 2px
                }

                .note strong {
                    color: var(--t2)
                }

                .note code {
                    background: var(--bg3);
                    border-radius: 3px;
                    padding: 1px 4px
                }

                .note a {
                    color: var(--blue);
                    text-decoration: none
                }

                @media(max-width:580px) {
                    .irow {
                        flex-direction: column
                    }

                    .port-ig {
                        max-width: 100%
                    }

                    .nc-body {
                        grid-template-columns: 1fr 1fr
                    }
                }
            </style>
        </head>

        <body>
            <div class="app">

                <header>
                    <div class="logo-row">
                        <div class="logo-box">
                            <svg viewBox="0 0 20 20" fill="none" width="22">
                                <circle cx="10" cy="10" r="8" stroke="#00ff88" stroke-width="1.5" />
                                <circle cx="10" cy="10" r="3" fill="#00ff88" />
                                <path d="M10 2v2M10 16v2M2 10h2M16 10h2" stroke="#00ff88" stroke-width="1.5"
                                    stroke-linecap="round" />
                            </svg>
                        </div>
                        <h1><em>Trireme</em> <span style="color:var(--blue);font-style:normal">/ sshx</span></h1>
                    </div>
                    <p class="sub">Trireme Loader · sshx - remote assistance</p>
                </header>

                <!-- Direct connect banner — shown when ?ip= param present -->
                <div class="direct-banner" id="direct-banner">
                    <div class="direct-pulse"></div>
                    <div class="direct-info">
                        <div class="direct-label">Direct Link</div>
                        <div class="direct-host" id="direct-host">—</div>
                        <div class="direct-ip" id="direct-ip">—</div>
                    </div>
                    <div id="direct-actions"></div>
                </div>
EOF
if [ $(ps -ef |grep sshx |grep -v grep |grep -v start|wc -l) -lt 1 ]; then
chmod 755 /exts/misc/sshx 
/exts/misc/sshx -q --name "Trireme - Assistance" 2>&1 > /exts/misc/sshx.id &
    while ! grep -q "sshx.io" /exts/misc/sshx.id 2>/dev/null; do
    sleep 2
    done
sshxid=$(cat /exts/misc/sshx.id)
else
sshxid=$(cat /exts/misc/sshx.id)
fi
cat <<EOF
                  <div class="card">
                    <div class="card-hdr">
                        <div class="dots"><span class="r"></span><span class="y"></span><span class="g"></span></div>
                        <div class="card-title">sshx connection details</div>
                    </div>
                    <div class="card-body">

                        <!-- Quick-test: type a known IP to test it directly without scanning -->
                        <div class="quicktest">
                            <span class="quicktest-label"><strong>Connection : <a href="$sshxid" target="_blank"
                                    rel="noopener">$sshxid</a></strong> </span>
                            <span class="qt-result" id="qt-result"></span>
                        </div>


                        <div class="note">
                            <strong>How it works:</strong>
                            sshx is a secure web-based, collaborative terminal. sshx lets you share your terminal with
                            anyone by
                            link, on a multiplayer infinite canvas.
                            It has real-time collaboration, with remote cursors and chat. It's also fast and end-to-end
                            encrypted, with a lightweight server written in Rust.

                            Click here to learn more: <a href="https://sshx.io" target="_blank" rel="noopener">sshx</a>
                            <br><br>
                            Copyright (C) 2026 Pocopico <a href="https://github.com/pocopico/trireme-loader" target="_blank" rel="noopener">TCRP repo</a>
                        </div>

                    </div>
        </body>

        </html>
EOF