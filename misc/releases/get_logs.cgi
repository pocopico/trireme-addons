#!/usr/bin/env sh
echo "Content-Type: text/html"
echo ""

cat <<EOF
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600&family=Syne:wght@400;700;800&display=swap" rel="stylesheet">
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
            --t1: #e8edf3;
            --t2: #8a9ab0;
            --t3: #4a5a70;
            --mono: 'JetBrains Mono', monospace;
            --head: 'Syne', sans-serif;
        }

        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

        html, body {
            background: transparent;
            color: var(--t1);
            font-family: var(--mono);
            height: 100vh;
            overflow: hidden;
            display: flex;
        }

        .app-layout {
            height: 100vh;
            width: 100vw;
            display: flex;
            flex-direction: row;
        }

        .sidebar {
            width: 280px;
            background: var(--bg1);
            border-right: 1px solid var(--border);
            display: flex;
            flex-direction: column;
            padding: 20px;
            overflow-y: auto;
        }

        .sidebar h3 {
            font-family: var(--head);
            font-size: 16px;
            margin-bottom: 20px;
            color: var(--blue);
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        .main-content {
            flex: 1;
            display: flex;
            flex-direction: column;
            background: var(--bg0);
            padding: 20px;
            overflow-y: auto;
        }

        .nav-link {
            display: block;
            padding: 10px 14px;
            margin-bottom: 8px;
            background: var(--bg2);
            border: 1px solid var(--border);
            border-radius: 8px;
            color: var(--t2);
            text-decoration: none;
            font-size: 13px;
            transition: all 0.2s ease;
            cursor: pointer;
        }

        .nav-link:hover {
            background: var(--bg3);
            border-color: var(--green);
            color: var(--t1);
        }

        .nav-link.active {
            background: rgba(0, 255, 136, 0.05);
            border-color: var(--green);
            color: var(--green);
        }

        .log-content {
            display: none;
            background: var(--bg1);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 20px;
            height: 100%;
            overflow-y: auto;
            box-shadow: inset 0 0 20px rgba(0,0,0,0.5);
        }

        .log-content pre {
            font-family: var(--mono);
            font-size: 12px;
            color: var(--t2);
            white-space: pre-wrap;
            line-height: 1.5;
        }

        .log-header {
            font-family: var(--head);
            color: var(--blue);
            font-size: 14px;
            margin-bottom: 16px;
            padding-bottom: 10px;
            border-bottom: 1px dashed var(--border2);
        }

        /* Initial empty state for main content */
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

    </style>
    <script>
        function showLog(id, element) {
            // Hide all log contents
            document.querySelectorAll('.log-content').forEach(el => el.style.display = 'none');
            // Hide empty state
            const emptyState = document.getElementById('empty-state');
            if(emptyState) emptyState.style.display = 'none';

            // Show selected log content
            document.getElementById(id).style.display = 'block';

            // Update active styling
            document.querySelectorAll('.nav-link').forEach(el => el.classList.remove('active'));
            if(element) element.classList.add('active');
        }
    </script>
</head>
<body>
    <div class="app-layout">
        <div class="sidebar">
            <h3>Log Files</h3>
EOF

count=0
for file in /var/log/* /exts/*log; do
    if [ -f "$file" ]; then
        count=$((count + 1))
        filename=$(basename "$file")
        echo "<div class='nav-link' onclick=\"showLog('log-$count', this)\">$filename</div>"
    fi
done

echo "        </div>"
echo "        <div class='main-content'>"
echo "            <div id='empty-state' class='empty-state'>"
echo "                <div class='empty-icon'>"
echo "                    <svg viewBox='0 0 24 24' fill='none' width='48' stroke='currentColor' stroke-width='1' stroke-linecap='round' stroke-linejoin='round'>"
echo "                        <path d='M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z'></path>"
echo "                        <polyline points='14 2 14 8 20 8'></polyline>"
echo "                        <line x1='16' y1='13' x2='8' y2='13'></line>"
echo "                        <line x1='16' y1='17' x2='8' y2='17'></line>"
echo "                        <polyline points='10 9 9 9 8 9'></polyline>"
echo "                    </svg>"
echo "                </div>"
echo "                <h2>Select a log file</h2>"
echo "            </div>"

count=0
for file in /var/log/* /exts/*log; do
    if [ -f "$file" ]; then
      count=$((count + 1))
      filename=$(basename "$file")
        
      echo "<div id='log-$count' class='log-content'>"
      echo "<div class='log-header'>$filename</div>"
      
      echo "<pre style='margin-top:10px;'>"
      if [ ! -s "$file" ]; then
          echo "[File is empty]"
      else
          cat "$file" 2>/dev/null | /exts/misc/sed 's/&/\&amp;/g; s/</\&lt;/g; s/>/\&gt;/g'
      fi
      
      echo "</pre>"
      echo "</div>"
    fi
done

echo "        </div>"
echo "    </div>"
echo "</body>"
echo "</html>"