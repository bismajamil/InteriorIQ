import os, io, requests
import gradio as gr
from groq import Groq
from PIL import Image

# ─── Load API key from HF Secrets (set in Space Settings → Variables & Secrets) ──
GROQ_KEY = os.environ.get("GROQ_API_KEY", "")

# ─── Image Generation via Pollinations.ai (FREE, no API key needed) ──────────
def generate_image_pollinations(prompt):
    try:
        encoded_prompt = requests.utils.quote(prompt)
        url = (
            f"https://image.pollinations.ai/prompt/{encoded_prompt}"
            f"?width=1024&height=768&model=flux&nologo=true&enhance=true"
        )
        response = requests.get(url, timeout=60)
        if response.status_code == 200:
            return Image.open(io.BytesIO(response.content))
        else:
            print(f"⚠️ Pollinations returned status: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Image generation error: {e}")
        return None

# ─── Main Logic ───────────────────────────────────────────────────────────────
def generate_design(width, height, length, room_type, style, budget, user_prompt):
    if not GROQ_KEY:
        return (
            "❌ GROQ_API_KEY is not set.\n\n"
            "Go to your Hugging Face Space → Settings → Variables & Secrets → "
            "Add a new secret named GROQ_API_KEY and paste your Groq API key.",
            None,
        )

    extra = f"\nSpecial requirements: {user_prompt}" if user_prompt else ""

    # ── Text via Groq ──────────────────────────────────────────────────────────
    try:
        client = Groq(api_key=GROQ_KEY)
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"You are a world-class interior designer.\n"
                        f"Design a stunning {style} {room_type} for a Pakistani client.\n"
                        f"Room: {width}ft wide × {length}ft long × {height}ft ceiling.\n"
                        f"Budget: {budget} (in Pakistani Rupees - PKR).{extra}\n\n"
                        f"Reply with exactly these 5 sections using these emoji headers:\n"
                        f"🛋️ FURNITURE LAYOUT\n"
                        f"🎨 COLOR PALETTE\n"
                        f"💡 LIGHTING DESIGN\n"
                        f"🌿 DECOR & FINISHING TOUCHES\n"
                        f"✅ PRO TIPS\n\n"
                        f"Be specific, inspiring, and practical. "
                        f"Mention exact product styles and color hex codes where helpful.\n"
                        f"Give all cost estimates in Pakistani Rupees (PKR / Rs.)."
                    ),
                }
            ],
        )
        design_text = resp.choices[0].message.content
    except Exception as e:
        return f"❌ Text generation error: {str(e)}", None

    # ── Image via Pollinations.ai ──────────────────────────────────────────────
    image_prompt = (
        f"photorealistic interior design render, {style} style {room_type}, "
        f"{width} by {length} feet room, high quality, soft natural lighting, "
        f"Architectural Digest quality, 4K detail, no people"
        + (f", {user_prompt}" if user_prompt else "")
    )
    image = generate_image_pollinations(image_prompt)

    return design_text, image

# ─── CSS ──────────────────────────────────────────────────────────────────────
css = """
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;400;600;700&family=Outfit:wght@300;400;500;600&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; }

:root {
    --gold:        #BFA16A;
    --gold-light:  #E8D5A3;
    --gold-dark:   #7A6234;
    --surface:     rgba(255,251,242,0.96);
    --surface-2:   rgba(250,245,232,0.85);
    --border:      rgba(191,161,106,0.22);
    --text:        #1C160A;
    --text-muted:  #6B5E3E;
    --radius-lg:   20px;
    --radius-md:   12px;
    --shadow-card: 0 8px 40px rgba(120,90,30,0.13);
}

@media (prefers-color-scheme: dark) {
    :root {
        --surface:    rgba(14,12,8,0.97);
        --surface-2:  rgba(22,18,10,0.92);
        --border:     rgba(191,161,106,0.18);
        --text:       #F5ECD7;
        --text-muted: #A89060;
    }
}

body, .gradio-container {
    font-family: 'Outfit', sans-serif !important;
    background: var(--surface) !important;
    color: var(--text) !important;
    min-height: 100vh;
}

.gradio-container {
    max-width: 1180px !important;
    margin: 0 auto !important;
    padding: 32px 24px 48px !important;
}

footer, .gr-footer, .footer, .built-with,
#footer, gradio-app > .wrap > footer,
svg.svelte-1kyws56 { display: none !important; }

#header-zone {
    text-align: center;
    padding: 40px 0 36px;
    position: relative;
}
#header-zone::after {
    content: '';
    display: block;
    width: 80px; height: 2px;
    background: linear-gradient(90deg, transparent, var(--gold), transparent);
    margin: 20px auto 0;
}
#app-title {
    font-family: 'Cormorant Garamond', serif !important;
    font-size: clamp(2.4rem, 5vw, 3.6rem) !important;
    font-weight: 600 !important;
    letter-spacing: -0.02em !important;
    line-height: 1.1 !important;
    background: linear-gradient(135deg, var(--gold-dark) 0%, var(--gold) 45%, var(--gold-light) 100%) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
    margin-bottom: 10px !important;
}
#app-subtitle {
    font-size: 1rem !important;
    color: var(--text-muted) !important;
    font-weight: 300 !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
}

.section-label {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.05rem;
    font-weight: 600;
    color: var(--gold);
    letter-spacing: 0.08em;
    text-transform: uppercase;
    border-bottom: 1px solid var(--border);
    padding-bottom: 10px;
    margin-bottom: 16px !important;
}

.gr-group, .gr-box, .gr-panel,
div[data-testid="column"] > div {
    background: var(--surface-2) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-lg) !important;
    box-shadow: var(--shadow-card) !important;
    padding: 24px !important;
}

label > span:first-child,
.gr-form label span {
    font-family: 'Outfit', sans-serif !important;
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    color: var(--gold) !important;
    margin-bottom: 6px !important;
    display: block !important;
}

input[type="number"],
input[type="text"],
input[type="password"],
textarea, select {
    font-family: 'Outfit', sans-serif !important;
    font-size: 0.94rem !important;
    background: var(--surface) !important;
    color: var(--text) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
    padding: 11px 14px !important;
    transition: border-color 0.25s, box-shadow 0.25s !important;
    width: 100% !important;
}
input:focus, textarea:focus, select:focus {
    border-color: var(--gold) !important;
    box-shadow: 0 0 0 4px rgba(191,161,106,0.12) !important;
    outline: none !important;
}

button.primary, .gr-button-primary, #gen-btn {
    font-family: 'Outfit', sans-serif !important;
    font-size: 1rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    background: linear-gradient(135deg, var(--gold-dark) 0%, var(--gold) 60%, var(--gold-light) 100%) !important;
    color: #fff !important;
    border: none !important;
    border-radius: var(--radius-md) !important;
    padding: 15px 40px !important;
    cursor: pointer !important;
    width: 100% !important;
    transition: transform 0.15s, box-shadow 0.2s !important;
    box-shadow: 0 4px 20px rgba(191,161,106,0.38) !important;
    margin-top: 8px !important;
}
button.primary:hover, .gr-button-primary:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 28px rgba(191,161,106,0.45) !important;
}
button.primary:active { transform: translateY(0) !important; }

textarea[readonly] {
    font-size: 0.9rem !important;
    line-height: 1.8 !important;
    background: var(--surface) !important;
}
img, .gr-image img {
    border-radius: var(--radius-lg) !important;
    box-shadow: var(--shadow-card) !important;
    width: 100% !important;
    object-fit: cover !important;
}
.gr-row { gap: 24px !important; }

::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--gold); border-radius: 99px; }
"""

# ─── UI ───────────────────────────────────────────────────────────────────────
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

with gr.Blocks(css=css, theme=gr.themes.Base()) as demo:

    gr.HTML("""
    <div id="header-zone">
      <div id="app-title">✦ InteriorIQ ✦</div>
      <div id="app-subtitle">AI-Powered Interior Design Studio — Pakistan Edition</div>
    </div>
    """)

    with gr.Row():
        # ── Left: inputs ──────────────────────────────────────────────────────
        with gr.Column(scale=5):
            gr.HTML('<div class="section-label">📐 Room Dimensions</div>')
            with gr.Row():
                width  = gr.Number(label="Width (ft)",   value=12, minimum=5)
                length = gr.Number(label="Length (ft)",  value=15, minimum=5)
                height = gr.Number(label="Ceiling (ft)", value=9,  minimum=6)

            gr.HTML('<div class="section-label" style="margin-top:20px">🏠 Design Brief</div>')
            room_type = gr.Dropdown(
                ["Living Room", "Bedroom", "Home Office", "Kitchen",
                 "Dining Room", "Bathroom", "Studio Apartment"],
                label="Room Type", value="Living Room",
            )
            style = gr.Dropdown(
                ["Modern", "Minimalist", "Luxury", "Classic", "Bohemian",
                 "Industrial", "Japandi", "Coastal", "Dark Academia"],
                label="Design Style", value="Modern",
            )
            budget = gr.Textbox(
                label="Budget (PKR — Pakistani Rupees)",
                placeholder="e.g. Rs. 50,000 | Rs. 2,00,000 | Rs. 5 Lakh | Premium",
            )
            user_prompt = gr.Textbox(
                label="Special Requests (optional)",
                placeholder="e.g. built-in shelving, statement fireplace, work-from-home corner…",
                lines=2,
            )
            gen_btn = gr.Button("✦ Generate My Design", variant="primary", elem_id="gen-btn")

        # ── Right: outputs ────────────────────────────────────────────────────
        with gr.Column(scale=6):
            gr.HTML('<div class="section-label">🎨 Generated Room Visual</div>')
            image_out = gr.Image(label="", height=320, show_label=False)

            gr.HTML('<div class="section-label" style="margin-top:20px">📋 Design Plan</div>')
            text_out = gr.Textbox(label="", lines=20, show_label=False)

    gen_btn.click(
        fn=generate_design,
        inputs=[width, height, length, room_type, style, budget, user_prompt],
        outputs=[text_out, image_out],
    )

# ─── Entry point ─────────────────────────────────────────────────────────────
demo.launch()