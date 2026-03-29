import re

with open("static/css/style.css", "r", encoding="utf-8") as f:
    css = f.read()

# Add root variables at the top
root_vars = """@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&family=Inter:wght@300;400;500;600&display=swap');

:root {
    /* Vibrant Warm Professional Palette */
    --bg-main: #1C1917; /* Warm Dark Space Gray */
    --bg-gradient: radial-gradient(circle at top left, #292524, #1C1917 70%);
    --card-bg: rgba(41, 37, 36, 0.7);
    --card-hover: rgba(68, 64, 60, 0.8);
    --nav-bg: linear-gradient(90deg, #1C1917, #292524);
    
    --text-light: #FAFAF9;
    --text-muted: #A8A29E;
    
    --accent-orange: #F97316; /* Vibrant Warm Orange */
    --accent-yellow: #F59E0B; /* Amber */
    --accent-teal: #14B8A6; /* Teal / Turquoise */
    --accent-blue: #38BDF8; /* Kept for legacy */
    
    --success: #10B981; /* Emerald */
    --danger: #EF4444; /* Red */
    
    --sidebar-bg: #292524;
    --table-header: #44403C;
    --table-row-hover: #292524;
}

body {
    font-family: 'Outfit', 'Inter', sans-serif;
    color: var(--text-light);
    background: var(--bg-gradient);
}
"""

# Replace top imports and body
css = re.sub(r"@import url\([^\)]+\);\n+", "", css)
css = re.sub(r"body\s*\{[^}]+\}", root_vars, css, count=1)

# Replace all the hardcoded colors
replacements = {
    "#1e293b": "var(--sidebar-bg)",
    "#0f172a": "var(--bg-main)",
    "rgba(30, 41, 59, 0.7)": "var(--card-bg)",
    "rgba(30, 41, 59, 0.8)": "var(--card-bg)",
    "rgba(255, 255, 255, 0.05)": "rgba(255, 255, 255, 0.08)",
    "rgba(0,0,0,0.4)": "rgba(0,0,0,0.5)",
    "#38bdf8": "var(--accent-orange)",
    "#818cf8": "var(--accent-yellow)",
    "#94a3b8": "var(--text-muted)",
    "#22c55e": "var(--success)",
    "#ef4444": "var(--danger)",
    "#e2e8f0": "var(--text-light)",
    "#334155": "var(--table-header)",
    "#475569": "var(--table-header)",
    "linear-gradient(45deg,#38bdf8,#818cf8)": "linear-gradient(45deg, var(--accent-orange), var(--accent-yellow))",
    "linear-gradient(90deg,#0f172a,#1e293b)": "var(--nav-bg)"
}

for old, new in replacements.items():
    css = css.replace(old, new)


# Modify specific .saving-card class if it doesn't exist
if ".saving-card" not in css:
    css += "\n\n.saving-card {\n    border-left: 6px solid var(--accent-yellow);\n}\n"

if "--bg-gradient" not in css:
    pass

with open("static/css/style.css", "w", encoding="utf-8") as f:
    f.write(css)
