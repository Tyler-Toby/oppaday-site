"""Oppaday LinkedIn graphic template (1080x1080 JPG).
Usage: python3 make_graphic.py out.jpg "Headline text" "Support line 1" "Support line 2"
"""
import sys, textwrap
from PIL import Image, ImageDraw, ImageFont

W = H = 1080
BG, NAVY, RING, ORANGE, FOOT, SUB = "#ebf0f7", "#06118c", "#0d3299", "#fb5519", "#022ba7", "#1b2350"
B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
X = 61

def fit(font_path, text, width):
    s = 10
    while ImageFont.truetype(font_path, s + 1).getlength(text) <= width: s += 1
    return ImageFont.truetype(font_path, s)

def render(out, headline, sub1, sub2, footer="Build. Create. Automate. Optimize."):
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
    # logo mark: navy outer ring, orange inner ring
    cx, cy = 96, 96
    d.ellipse([cx-36, cy-36, cx+36, cy+36], outline=RING, width=7)
    d.ellipse([cx-22, cy-22, cx+22, cy+22], outline=ORANGE, width=7)
    f = fit(B, "OPPADAY", 296); top = f.getbbox("OPPADAY")
    d.text((153, cy - (top[1]+top[3])/2), "OPPADAY", font=f, fill=NAVY)
    # orange accent
    d.rectangle([X, 216, 171, 227], fill=ORANGE)
    # headline: 82px DejaVu Bold, shrink until it fits in 5 lines
    size = 82
    while True:
        hf = ImageFont.truetype(B, size)
        words, lines, cur = headline.split(), [], ""
        for w in words:
            t = (cur + " " + w).strip()
            if hf.getlength(t) <= 680: cur = t
            else: lines.append(cur); cur = w
        lines.append(cur)
        if len(lines) <= 5 or size <= 60: break
        size -= 4
    pitch = round(size * 93 / 82)
    y = 276 - hf.getbbox("H")[1]
    for ln in lines:
        d.text((X, y), ln, font=hf, fill=NAVY); y += pitch
    # supporting lines
    sf = ImageFont.truetype(R, 40); scap = sf.getbbox("H")[1]
    sy = max(791, y + 30)
    d.text((X, sy - scap), sub1, font=sf, fill=SUB)
    d.text((X, sy - scap + 56), sub2, font=sf, fill=SUB)
    # footer band
    d.rectangle([0, 929, W, H], fill=FOOT)
    ff = ImageFont.truetype(B, 40); bb = ff.getbbox(footer)
    d.text(((W-(bb[2]-bb[0]))/2 - bb[0], 1004.5 - (bb[1]+bb[3])/2), footer, font=ff, fill="white")
    im.save(out, "JPEG", quality=92, optimize=True)

if __name__ == "__main__":
    render(*sys.argv[1:5])
