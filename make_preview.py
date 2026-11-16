"""Oppaday link-preview graphic (1200x627 JPG) for og:image.
Usage: python3 make_preview.py out.jpg "Headline" "Support line"
"""
import sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 627
BG, NAVY, RING, ORANGE, FOOT, SUB = "#ebf0f7", "#06118c", "#0d3299", "#fb5519", "#022ba7", "#1b2350"
B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
X = 60

def fit(p, t, w):
    s = 10
    while ImageFont.truetype(p, s + 1).getlength(t) <= w: s += 1
    return ImageFont.truetype(p, s)

def wrap(f, text, w):
    lines, cur = [], ""
    for word in text.split():
        t = (cur + " " + word).strip()
        if f.getlength(t) <= w: cur = t
        else: lines.append(cur); cur = word
    lines.append(cur); return lines

def render(out, headline, sub, footer="Build. Create. Automate. Optimize."):
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
    cx = cy = 78
    d.ellipse([X, cy-26, X+52, cy+26], outline=RING, width=6)
    d.ellipse([X+10, cy-16, X+42, cy+16], outline=ORANGE, width=6)
    f = fit(B, "OPPADAY", 210); bb = f.getbbox("OPPADAY")
    d.text((X+70, cy-(bb[1]+bb[3])/2), "OPPADAY", font=f, fill=NAVY)
    d.rectangle([X, 140, X+90, 149], fill=ORANGE)
    size = 64
    while True:
        hf = ImageFont.truetype(B, size); lines = wrap(hf, headline, 1080)
        if len(lines) <= 3 or size <= 44: break
        size -= 4
    pitch = round(size * 1.13); y = 182 - hf.getbbox("H")[1]
    for ln in lines: d.text((X, y), ln, font=hf, fill=NAVY); y += pitch
    sf = ImageFont.truetype(R, 32)
    d.text((X, y + 22), sub, font=sf, fill=SUB)
    d.rectangle([0, 537, W, H], fill=FOOT)
    ff = ImageFont.truetype(B, 34); fb = ff.getbbox(footer)
    d.text(((W-(fb[2]-fb[0]))/2-fb[0], 582-(fb[1]+fb[3])/2), footer, font=ff, fill="white")
    im.save(out, "JPEG", quality=92, optimize=True)

if __name__ == "__main__":
    render(*sys.argv[1:4])
