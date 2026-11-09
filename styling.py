"""Presentation only: shared pink palette, Helvetica and a tiny SVG study mascot."""
CSS = '''<style>
html, body, [data-testid="stApp"], input, textarea, button,
[data-testid="stMarkdownContainer"], [data-baseweb="select"], h1,h2,h3 {
 font-family:"Helvetica Neue",Helvetica,Arial,sans-serif;
}
.block-container {max-width:1480px;padding-top:4rem;}
[data-testid="stAppViewContainer"], [data-testid="stHeader"] {background:#FFF0F6;}
h1 {letter-spacing:-1.5px;} h2,h3 {letter-spacing:-.4px;}
.eyebrow {color:#E85D9F;font-size:12px;font-weight:700;letter-spacing:2px;}
[data-testid="stVerticalBlockBorderWrapper"] {border-radius:20px;background:white;box-shadow:0 5px 20px #50344708;}
.st-key-strategy_card, .st-key-diagram_card {background:white;border-radius:20px;box-shadow:0 5px 20px #50344708;}
.stButton button, .stFormSubmitButton button {border-radius:16px;border:1px solid #FFD6E8;box-shadow:0 3px 8px #E85D9F0D;}
[data-testid="stExpander"], [data-testid="stForm"] {background:white;border:1px solid #FFD6E8;border-radius:18px;}
[data-baseweb="tab-highlight"] {background:#E85D9F;}
[data-testid="stProgress"] [role="progressbar"] > div {background:#E85D9F;}
[data-testid="stAlert"] {border-radius:14px;}
[data-testid="stAlert"][data-baseweb="notification"] {color:#503447;}
.mascot {position:fixed;bottom:16px;right:18px;z-index:50;pointer-events:none;width:65px;}
.math {font-family:"Helvetica Neue",Helvetica,Arial,"STIX Two Math","Cambria Math",sans-serif;}
.sparkles {color:#E85D9F;font-size:24px;animation:twinkle 1s ease-in-out 3;}
@keyframes twinkle {50% {opacity:.4;transform:translateY(-4px);}}
@media(prefers-reduced-motion:reduce){.sparkles {animation:none;}}
@media(max-width:700px){.mascot{width:42px;bottom:8px;right:8px;}}
</style>'''
MASCOT = '''<div class="mascot" role="img" aria-label="A little bunny study companion">
<svg viewBox="0 0 100 110" xmlns="http://www.w3.org/2000/svg">
<ellipse cx="34" cy="25" rx="12" ry="23" fill="#FFFFFF" stroke="#E85D9F" stroke-width="2"/>
<ellipse cx="66" cy="25" rx="12" ry="23" fill="#FFFFFF" stroke="#E85D9F" stroke-width="2"/>
<ellipse cx="34" cy="24" rx="5" ry="15" fill="#FFD6E8"/><ellipse cx="66" cy="24" rx="5" ry="15" fill="#FFD6E8"/>
<ellipse cx="50" cy="61" rx="40" ry="33" fill="white" stroke="#E85D9F" stroke-width="2"/>
<circle cx="36" cy="57" r="3" fill="#503447"/><circle cx="64" cy="57" r="3" fill="#503447"/>
<ellipse cx="25" cy="68" rx="7" ry="4" fill="#FFD6E8"/><ellipse cx="75" cy="68" rx="7" ry="4" fill="#FFD6E8"/>
<path d="M45 68 Q50 75 55 68" fill="none" stroke="#503447" stroke-width="2"/>
<path d="M22 82 Q36 77 50 85 Q64 77 78 82 L78 103 Q64 98 50 106 Q36 98 22 103Z" fill="#EBDCF8" stroke="#A78DBD" stroke-width="2"/>
<path d="M50 85V105" stroke="#A78DBD" stroke-width="2"/></svg></div>'''
