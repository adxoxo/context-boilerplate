"""
extract_design_tokens.py

Run this AFTER the brainstorm phase, BEFORE telling Claude Code to start building.

The script reads your design feeling answers from Section 3A of CLAUDE.md
and passes them to Gemini as context — so the extracted tokens actually
reflect the feeling you described, not just what's literally in the screenshots.

SETUP (one time):
  1. Get your free Gemini API key: https://aistudio.google.com → "Get API key"
  2. Create a .env file in your project root:
       GEMINI_API_KEY=your_key_here
  3. pip install requests

USAGE (per project):
  1. Fill in Section 3A of CLAUDE.md during brainstorm
  2. Create a /references folder and drop in 3-5 UI screenshots (PNG/JPG/WEBP)
  3. Run: python extract_design_tokens.py

OUTPUT:
  - design-tokens.json   raw token data
  - tailwind.config.ts   ready-to-use Tailwind theme

AFTER RUNNING:
  - Paste the printed summary into Section 3B of CLAUDE.md
  - Install the recommended Google Fonts in your layout.tsx
  - Cross-check key colors in browser DevTools if you need precision
  - Tell Claude Code: "Read CLAUDE.md and start Phase 1"
"""

import os
import re
import json
import base64
import requests
from pathlib import Path


# ── Load .env without any third-party package ─────────────────────────────────

def load_env():
    env_path = Path(".env")
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                os.environ.setdefault(key.strip(), value.strip())

load_env()

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise SystemExit(
        "❌  GEMINI_API_KEY not found.\n"
        "    Add it to a .env file:\n"
        "    GEMINI_API_KEY=your_key_here"
    )


# ── Config ────────────────────────────────────────────────────────────────────

REFERENCES_DIR  = Path("references")
CLAUDE_MD       = Path("CLAUDE.md")
OUTPUT_TOKENS   = Path("design-tokens.json")
OUTPUT_TAILWIND = Path("tailwind.config.ts")

# gemini-2.5-pro-preview = best reasoning + vision quality, what you want here
# gemini-2.0-flash       = faster, cheaper, still very good
# gemini-1.5-pro-latest  = fallback if the above aren't available on your key yet
GEMINI_MODEL = "gemini-2.5-pro-preview-05-06"

GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    f"{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
)

SUPPORTED_FORMATS = {
    ".png":  "image/png",
    ".jpg":  "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
}


# ── Read design feeling from CLAUDE.md Section 3A ────────────────────────────

def read_design_feeling():
    """
    Extracts the filled answers from Section 3A of CLAUDE.md.
    Returns a plain-text summary to inject into the Gemini prompt.
    If CLAUDE.md doesn't exist or 3A is empty, returns a fallback notice.
    """
    if not CLAUDE_MD.exists():
        print("⚠️   CLAUDE.md not found — skipping design feeling context.")
        return "No design feeling provided."

    content = CLAUDE_MD.read_text()

    # Grab everything between ### 3A. Design Feeling and the next ### heading
    match = re.search(
        r"### 3A\. Design Feeling(.*?)###",
        content,
        re.DOTALL
    )

    if not match:
        print("⚠️   Section 3A not found in CLAUDE.md — skipping design feeling context.")
        return "No design feeling provided."

    section = match.group(1)

    # Strip HTML comments (the placeholder instructions)
    section = re.sub(r"<!--.*?-->", "", section, flags=re.DOTALL)

    # Strip blank lines and leading/trailing whitespace
    lines = [l.strip() for l in section.splitlines() if l.strip()]
    feeling = "\n".join(lines)

    if not feeling:
        print("⚠️   Section 3A is empty — fill it in CLAUDE.md before running this script.")
        print("    Continuing without design feeling context...\n")
        return "No design feeling provided."

    print("🎯  Design feeling loaded from CLAUDE.md Section 3A.")
    return feeling


# ── Load screenshots from /references ────────────────────────────────────────

def load_screenshots():
    if not REFERENCES_DIR.exists():
        raise SystemExit(
            "❌  /references folder not found.\n"
            "    Create it and drop in 3-5 UI screenshots (PNG/JPG/WEBP)."
        )

    files = sorted([
        f for f in REFERENCES_DIR.iterdir()
        if f.suffix.lower() in SUPPORTED_FORMATS
    ])

    if not files:
        raise SystemExit(
            "❌  No images found in /references.\n"
            "    Add PNG, JPG, or WEBP screenshots of UIs you want to reference."
        )

    print(f"📸  Found {len(files)} screenshot(s): {', '.join(f.name for f in files)}")

    return [
        {
            "name":     f.name,
            "mimeType": SUPPORTED_FORMATS[f.suffix.lower()],
            "data":     base64.b64encode(f.read_bytes()).decode("utf-8"),
        }
        for f in files
    ]


# ── Build the extraction prompt ───────────────────────────────────────────────

def build_prompt(design_feeling):
    return f"""
You are a design systems expert working with a developer who has defined a
clear emotional direction for their product.

DESIGN FEELING (defined by the product owner):
───────────────────────────────────────────────
{design_feeling}
───────────────────────────────────────────────

Your job: analyze ALL of the provided UI screenshots together and extract a
unified design token system. Use the design feeling above as your primary lens —
the tokens you extract should serve and reinforce that feeling, not just
literally copy what's in the screenshots.

For example: if the feeling is "warm and welcoming like a local cafe", lean
toward warmer color temperatures, softer shadows, and rounded corners —
even if the reference screenshots are slightly more neutral.

Return ONLY a valid JSON object. No explanation, no markdown fences. Raw JSON only.

Use this exact structure:
{{
  "meta": {{
    "aesthetic": "one sentence describing the visual style that serves the design feeling",
    "mood": "e.g. minimal, bold, playful, premium, editorial",
    "feelingAlignment": "one sentence explaining how these tokens serve the stated feeling",
    "recommendedHeadingFont": "specific Google Font — NOT Inter, Roboto, or Arial",
    "recommendedBodyFont": "specific Google Font name"
  }},
  "colors": {{
    "primary": "#hex",
    "secondary": "#hex",
    "accent": "#hex",
    "background": "#hex",
    "surface": "#hex",
    "border": "#hex",
    "text": {{
      "primary": "#hex",
      "secondary": "#hex",
      "muted": "#hex"
    }},
    "error": "#hex",
    "success": "#hex",
    "warning": "#hex"
  }},
  "typography": {{
    "fontFamily": {{
      "heading": "font name",
      "body": "font name"
    }},
    "fontSize": {{
      "xs": "12px", "sm": "14px", "base": "16px",
      "lg": "18px", "xl": "20px", "2xl": "24px",
      "3xl": "30px", "4xl": "36px", "5xl": "48px"
    }},
    "fontWeight": {{
      "normal": "400", "medium": "500",
      "semibold": "600", "bold": "700"
    }},
    "lineHeight": {{
      "tight": "1.2", "normal": "1.5", "relaxed": "1.75"
    }}
  }},
  "spacing": {{
    "xs": "4px", "sm": "8px", "md": "16px",
    "lg": "24px", "xl": "32px", "2xl": "48px", "3xl": "64px"
  }},
  "borderRadius": {{
    "sm": "4px", "md": "8px", "lg": "12px",
    "xl": "16px", "2xl": "24px", "full": "9999px"
  }},
  "shadows": {{
    "sm": "0 1px 3px rgba(0,0,0,0.1)",
    "md": "0 4px 12px rgba(0,0,0,0.15)",
    "lg": "0 8px 32px rgba(0,0,0,0.2)",
    "xl": "0 16px 48px rgba(0,0,0,0.25)"
  }},
  "animation": {{
    "durationFast": "150ms",
    "durationBase": "200ms",
    "durationSlow": "300ms",
    "easing": "ease-in-out"
  }}
}}

Additional rules:
- Be precise with hex color values
- Recommend distinctive, character-rich Google Fonts that match the feeling —
  never Inter, Roboto, Arial, or system-ui
- If the feeling implies dark theme, extract dark values
- Synthesize across ALL screenshots — not just one
- Let the feeling guide ambiguous decisions
"""


# ── Call Gemini vision API ────────────────────────────────────────────────────

def call_gemini(screenshots, design_feeling):
    image_parts = [
        {"inlineData": {"mimeType": s["mimeType"], "data": s["data"]}}
        for s in screenshots
    ]

    payload = {
        "contents": [{
            "parts": image_parts + [{"text": build_prompt(design_feeling)}]
        }],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 2048,
        }
    }

    print("🤖  Sending to Gemini Pro vision...")

    response = requests.post(GEMINI_URL, json=payload, timeout=60)

    if not response.ok:
        raise SystemExit(
            f"❌  Gemini API error {response.status_code}:\n{response.text}"
        )

    text = response.json()["candidates"][0]["content"]["parts"][0]["text"].strip()

    # Strip markdown fences if Gemini adds them anyway
    if text.startswith("```"):
        text = text.split("\n", 1)[-1]
    if text.endswith("```"):
        text = text.rsplit("```", 1)[0]

    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        raise SystemExit(
            f"❌  Could not parse Gemini response as JSON.\n"
            f"Raw response:\n{text}"
        )


# ── Generate tailwind.config.ts ───────────────────────────────────────────────

def generate_tailwind_config(tokens):
    c  = tokens.get("colors", {})
    ct = c.get("text", {})
    t  = tokens.get("typography", {})
    ff = t.get("fontFamily", {})
    fs = t.get("fontSize", {})
    fw = t.get("fontWeight", {})
    lh = t.get("lineHeight", {})
    r  = tokens.get("borderRadius", {})
    s  = tokens.get("shadows", {})
    a  = tokens.get("animation", {})
    m  = tokens.get("meta", {})

    def q(val, fallback=""):
        return f'"{val or fallback}"'

    def dict_to_ts(d, indent=8):
        lines = []
        for k, v in d.items():
            key = f'"{k}"' if not k.isidentifier() or k[0].isdigit() else k
            lines.append(f'{" " * indent}{key}: {q(v)},')
        return "\n".join(lines)

    return f"""\
import type {{ Config }} from "tailwindcss";

// Auto-generated by extract_design_tokens.py
// Aesthetic        : {m.get("aesthetic", "")}
// Mood             : {m.get("mood", "")}
// Feeling          : {m.get("feelingAlignment", "")}
// Heading font     : {ff.get("heading", "")}
// Body font        : {ff.get("body", "")}

const config: Config = {{
  darkMode: ["class"],
  content: [
    "./src/**/*.{{ts,tsx}}",
    "./app/**/*.{{ts,tsx}}",
    "./components/**/*.{{ts,tsx}}",
  ],
  theme: {{
    extend: {{
      colors: {{
        primary:    {q(c.get("primary"))},
        secondary:  {q(c.get("secondary"))},
        accent:     {q(c.get("accent"))},
        background: {q(c.get("background"))},
        surface:    {q(c.get("surface"))},
        border:     {q(c.get("border"))},
        text: {{
          primary:   {q(ct.get("primary"))},
          secondary: {q(ct.get("secondary"))},
          muted:     {q(ct.get("muted"))},
        }},
        error:   {q(c.get("error"))},
        success: {q(c.get("success"))},
        warning: {q(c.get("warning"))},
      }},
      fontFamily: {{
        heading: [{q(ff.get("heading"))}, "sans-serif"],
        body:    [{q(ff.get("body"))}, "sans-serif"],
        sans:    [{q(ff.get("body"))}, "sans-serif"],
      }},
      fontSize: {{
{dict_to_ts(fs)}
      }},
      fontWeight: {{
{dict_to_ts(fw)}
      }},
      lineHeight: {{
{dict_to_ts(lh)}
      }},
      borderRadius: {{
{dict_to_ts(r)}
      }},
      boxShadow: {{
{dict_to_ts(s)}
      }},
      transitionDuration: {{
        fast: {q(a.get("durationFast", "150ms"))},
        base: {q(a.get("durationBase", "200ms"))},
        slow: {q(a.get("durationSlow", "300ms"))},
      }},
    }},
  }},
  plugins: [],
}};

export default config;
"""


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("\n🎨  Design Token Extractor — Powered by Gemini\n")

    design_feeling = read_design_feeling()
    screenshots    = load_screenshots()
    tokens         = call_gemini(screenshots, design_feeling)

    OUTPUT_TOKENS.write_text(json.dumps(tokens, indent=2))
    print("✅  design-tokens.json written")

    OUTPUT_TAILWIND.write_text(generate_tailwind_config(tokens))
    print("✅  tailwind.config.ts written")

    # Print summary for pasting into CLAUDE.md Section 3B
    m  = tokens.get("meta", {})
    c  = tokens.get("colors", {})
    ff = tokens.get("typography", {}).get("fontFamily", {})

    print()
    print("─" * 56)
    print("📋  PASTE THIS INTO CLAUDE.md  →  Section 3B Tokens")
    print("─" * 56)
    print(f"Aesthetic:        {m.get('aesthetic', 'n/a')}")
    print(f"Mood:             {m.get('mood', 'n/a')}")
    print(f"Feeling aligned:  {m.get('feelingAlignment', 'n/a')}")
    print(f"Heading font:     {ff.get('heading', 'n/a')}")
    print(f"Body font:        {ff.get('body', 'n/a')}")
    print(f"Primary:          {c.get('primary', 'n/a')}")
    print(f"Secondary:        {c.get('secondary', 'n/a')}")
    print(f"Accent:           {c.get('accent', 'n/a')}")
    print(f"Background:       {c.get('background', 'n/a')}")
    print(f"Surface:          {c.get('surface', 'n/a')}")
    print(f"Border:           {c.get('border', 'n/a')}")
    print("─" * 56)
    print()
    print("⚠️   NEXT STEPS:")
    print("  1. Paste the summary above into Section 3B of CLAUDE.md")
    print("  2. Add heading + body fonts to layout.tsx via Google Fonts")
    print("  3. Cross-check key colors in browser DevTools if needed")
    print("  4. Tell Claude Code: 'Read CLAUDE.md and start Phase 1'\n")


if __name__ == "__main__":
    main()
