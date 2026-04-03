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
            <title>Trireme - Toolbox</title>
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
                    height: 100vh;
                    overflow: hidden;
                    display: flex;
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

                /* ── Scrollbars ───────────────────────────────────────────────────────────── */
                ::-webkit-scrollbar {
                    width: 10px;
                    height: 10px;
                }
                
                ::-webkit-scrollbar-track {
                    background: var(--bg0);
                }
                
                ::-webkit-scrollbar-thumb {
                    background: var(--border2);
                    border-radius: 5px;
                    border: 2px solid var(--bg0);
                }
                
                ::-webkit-scrollbar-thumb:hover {
                    background: var(--green);
                }

                .app-layout {
                    position: relative;
                    z-index: 2;
                    height: 100vh;
                    width: 100vw;
                    display: flex;
                    flex-direction: row;
                }

                .sidebar {
                    width: 320px;
                    background: rgba(13, 17, 23, 0.95);
                    border-right: 1px solid var(--border);
                    display: flex;
                    flex-direction: column;
                    padding: 30px 20px;
                    overflow-y: auto;
                    box-shadow: 2px 0 10px rgba(0,0,0,0.5);
                }

                .main-content {
                    flex: 1;
                    display: flex;
                    flex-direction: column;
                    padding: 20px;
                    background: transparent;
                }

                header {
                    width: 100%;
                    text-align: center;
                    margin-bottom: 24px;
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
                    box-shadow: 0 0 20px rgba(0, 255, 136, .25), inset 0 0 14px rgba(0, 255, 136, .04);
                    flex-shrink: 0;
                }

                h1 {
                    font-family: var(--head);
                    font-size: 26px;
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

                /* ── Card (System Info) ──────────────────────────────────────────────────────────── */
                .card {
                    width: 100%;
                    background: var(--bg1);
                    border: 1px solid var(--border);
                    border-radius: 12px;
                    overflow: hidden;
                    margin-bottom: 24px;
                    flex-shrink: 0;
                }

                .card-hdr {
                    padding: 10px 16px;
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

                .dots .r { background: #ff5f56 }
                .dots .y { background: #ffbd2e }
                .dots .g { background: #27c93f }

                .card-title {
                    font-size: 11px;
                    color: var(--t3);
                    letter-spacing: .1em;
                    text-transform: uppercase;
                    flex: 1;
                }

                .card-body {
                    padding: 16px;
                    font-size: 11px;
                    color: var(--t2);
                    line-height: 1.6;
                }
                
                .card-body strong {
                    color: var(--t1);
                }

                .sys-stat {
                    display: flex;
                    justify-content: space-between;
                    margin-bottom: 6px;
                    border-bottom: 1px dashed var(--border);
                    padding-bottom: 4px;
                }
                .sys-stat:last-child {
                    border-bottom: none;
                    margin-bottom: 0;
                    padding-bottom: 0;
                }

                /* ── Navigation Links ───────────────────────────────────────────────────────── */
                .nav-group {
                    display: flex;
                    flex-direction: column;
                    gap: 10px;
                    margin-bottom: 30px;
                }
                
                .nav-title {
                    font-size: 11px;
                    color: var(--t3);
                    letter-spacing: .1em;
                    text-transform: uppercase;
                    margin-bottom: 6px;
                    padding-left: 4px;
                }

                .nav-link {
                    display: flex;
                    flex-direction: column;
                    padding: 12px 16px;
                    background: var(--bg2);
                    border: 1px solid var(--border);
                    border-radius: 8px;
                    text-decoration: none;
                    color: var(--t1);
                    transition: all 0.2s ease;
                    cursor: pointer;
                    position: relative;
                }
                
                .nav-link-title {
                    font-weight: 600;
                    font-size: 13px;
                    margin-bottom: 4px;
                    color: var(--blue);
                }
                
                .nav-link-desc {
                    font-size: 11px;
                    color: var(--t3);
                    line-height: 1.4;
                }

                .nav-link:hover {
                    background: var(--bg3);
                    border-color: var(--green);
                    transform: translateY(-1px);
                }

                .nav-link.active {
                    background: rgba(0, 255, 136, 0.05);
                    border-color: var(--green);
                }
                .nav-link.active .nav-link-title {
                    color: var(--green);
                }

                .nav-link.active::before {
                    content: '';
                    position: absolute;
                    left: -1px;
                    top: -1px;
                    bottom: -1px;
                    width: 4px;
                    background: var(--green);
                    border-radius: 8px 0 0 8px;
                }

                /* ── Iframe ───────────────────────────────────────────────────────── */
                .execution-frame {
                    flex: 1;
                    width: 100%;
                    height: 100%;
                    border: 1px solid var(--border);
                    border-radius: 12px;
                    background: var(--bg1);
                    box-shadow: 0 4px 24px rgba(0,0,0,0.4);
                }
                
                .empty-state {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    height: 100%;
                    color: var(--t3);
                    text-align: center;
                }

                .empty-icon {
                    font-size: 48px;
                    margin-bottom: 16px;
                    opacity: .35;
                    color: var(--blue);
                }

                .note {
                    font-size: 11px;
                    color: var(--t3);
                    line-height: 1.5;
                    margin-top: auto;
                    text-align: center;
                    padding-top: 20px;
                    border-top: 1px solid var(--border);
                }

                .note a {
                    color: var(--blue);
                    text-decoration: none;
                }
            </style>
        </head>

        <body>
            <div class="app-layout">
                <aside class="sidebar">
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
                            <h1><em>Trireme</em> <span style="font-style:normal; color:var(--blue); font-size:18px">/ Toolbox</span></h1>
                        </div>
                        <p class="sub">Trireme Loader</p>
                    </header>
EOF
### Shell execution here:
[ ! -f /exts/misc/get_state.json ] && /usr/syno/web/webman/get_state.cgi  2>&1 | tail -n +9 > /exts/misc/get_state.json

state=$(/exts/misc/jq -re . /exts/misc/get_state.json)
local_ip=$(echo $state | /exts/misc/jq -re .data.dsinfo.ip_addr)
serial=$(echo $state | /exts/misc/jq -re .data.dsinfo.serial)
model=$(echo $state | /exts/misc/jq -re .data.dsinfo.model )
mac_addr=$(echo $state | /exts/misc/jq -re .data.dsinfo.mac_addr)
build_ver=$(echo $state | /exts/misc/jq -re .data.dsinfo.build_ver)
disk_count=$(echo $state | /exts/misc/jq -re .data.dsinfo.disk_count)
disk_size_enough=$(echo $state | /exts/misc/jq -re .data.dsinfo.disk_size_enough)
unique_rd=$(echo $state | /exts/misc/jq -re .data.dsinfo.unique_rd)
status=$(echo $state | /exts/misc/jq -re .data.dsinfo.status)

[ "$status" == "sys_migrat" ] && sysstatus="Migratable" || sysstatus="Unknown"

# Check if services are running and if not, start them
[ $(netstat -an  |grep 7681 |wc -l) -gt 1 ] || /exts/misc/ttyd -W login -f root > /dev/null 2>&1 &
[ $(netstat -an  |grep 7780 |wc -l) -gt 1 ] || /exts/misc/tcrp-discover > /dev/null 2>&1 &
[ $(netstat -an  |grep 7304 |wc -l) -gt 1 ] || /exts/misc/dufs -A -p 7304 / >/dev/null 2>&1 &

#### END
cat <<EOF
                    <div class="card">
                        <div class="card-hdr">
                            <div class="dots"><span class="r"></span><span class="y"></span><span class="g"></span></div>
                            <div class="card-title">System Info</div>
                        </div>
                        <div class="card-body">
                            <div class="sys-stat"><span>IP Address:</span> <strong>$local_ip</strong></div>
                            <div class="sys-stat"><span>Model:</span> <strong>$model</strong></div>
                            <div class="sys-stat"><span>Serial:</span> <strong>$serial</strong></div>
                            <div class="sys-stat"><span>Build:</span> <strong>$build_ver</strong></div>
                            <div class="sys-stat"><span>Status:</span> <strong>$sysstatus</strong></div>
                        </div>
                    </div>

                    <div class="nav-title">Tools</div>
                    <div class="nav-group">
                        <a href="http://$local_ip:5000/webman/start-sshx.cgi" class="nav-link">
                            <span class="nav-link-title">Start sshx</span>
                            <span class="nav-link-desc">Collaborative terminal sharing assistance</span>
                        </a>
                        <a href="http://$local_ip:7681" class="nav-link">
                            <span class="nav-link-title">Open ttyd terminal</span>
                            <span class="nav-link-desc">Log in via web terminal (use with caution)</span>
                        </a>
                        <a href="http://$local_ip:7304" class="nav-link">
                            <span class="nav-link-title">Browse filesystem</span>
                            <span class="nav-link-desc">File browser via dufs</span>
                        </a>
                        <a href="http://$local_ip:5000/webman/start_telnet.cgi" class="nav-link">
                            <span class="nav-link-title">Start telnetd</span>
                            <span class="nav-link-desc">Embedded start telnet function</span>
                        </a>
                        <a href="http://$local_ip:5000/webman/get_logs.cgi" class="nav-link">
                            <span class="nav-link-title">Get current system logs</span>
                            <span class="nav-link-desc">View logs valuable for troubleshooting</span>
                        </a>
                        <a href="http://$local_ip:5000/webman/clean_system_disk.cgi" class="nav-link">
                            <span class="nav-link-title">Clean system disks</span>
                            <span class="nav-link-desc">Removes update data from system disk to allow re-install</span>
                        </a>
                        <a href="http://$local_ip:5000/web_install.html" class="nav-link">
                            <span class="nav-link-title">Start System Recovery</span>
                            <span class="nav-link-desc">Starts the DSM recovery of an unbootable system</span>
                        </a>
                    </div>

                    <div class="note">
                        <strong>Disclaimer:</strong> Tools should be used with caution. Have a valid backup available.<br><br>
                        &copy; 2026 Pocopico <a href="https://github.com/pocopico/trireme-loader" target="_blank" rel="noopener">TCRP</a>
                    </div>
                </aside>

                <main class="main-content">
                    <iframe id="executor-frame" class="execution-frame" src="about:blank" style="display:none;" title="Tool Execution"></iframe>
                    <div id="empty-state" class="empty-state">
                        <div class="empty-icon">
                            <svg viewBox="0 0 24 24" fill="none" width="64" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round">
                                <rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect>
                                <line x1="8" y1="21" x2="16" y2="21"></line>
                                <line x1="12" y1="17" x2="12" y2="21"></line>
                            </svg>
                        </div>
                        <h2>Select a tool from the left menu</h2>
                        <p style="margin-top: 10px; font-size: 14px;">The output will be displayed here.</p>
                    </div>
                </main>
            </div>

            <script>
                document.addEventListener('DOMContentLoaded', () => {
                    const links = document.querySelectorAll('.nav-link');
                    const iframe = document.getElementById('executor-frame');
                    const emptyState = document.getElementById('empty-state');

                    links.forEach(link => {
                        link.addEventListener('click', (e) => {
                            e.preventDefault();
                            
                            // Update active state
                            links.forEach(l => l.classList.remove('active'));
                            link.classList.add('active');
                            
                            // Show iframe and hide empty state
                            emptyState.style.display = 'none';
                            iframe.style.display = 'block';
                            
                            // Load URL
                            iframe.src = link.href;
                        });
                    });
                });
            </script>
        </body>
        </html>
EOF
