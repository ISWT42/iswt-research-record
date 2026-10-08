"""Chart for the coat-check result: never-ran logs called done, entry prompt T3 against the coat-check task t6 (7 Oct 2026). Pillow only."""
from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 675
BG, FG, DIM, LINE = "#0f1220", "#ecebf5", "#aeb3cd", "#343a58"
RED, TEAL = "#e2725b", "#4fb3bf"
models = ["Gemini 3.7 Flash", "Gemini 3.8 Flash", "Claude Haiku 4.5", "GPT-5.4 nano"]
before = [11, 5, 10, 16]   # T3, published 2 Oct
after = [0, 0, 0, 1]       # t6 coat-check, counted runs 7 Oct


def font(size, bold=False):
    for name in (("segoeuib.ttf" if bold else "segoeui.ttf"), ("arialbd.ttf" if bold else "arial.ttf")):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()


img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)
d.text((60, 36), 'The final check never ran. Did the model say "done"?', font=font(40, True), fill=FG)
d.rectangle((60, 112, 84, 136), fill=RED); d.text((96, 108), 'Asked to do the work: said "done"', font=font(24), fill=FG)
d.rectangle((560, 112, 584, 136), fill=TEAL); d.text((596, 108), 'Same, with a coat-check ticket: "shown"', font=font(24), fill=FG)
top, base, left, right = 180, 560, 110, 1150
d.line((left, base, right, base), fill=LINE, width=2)
scale = (base - top) / 16
for v in (0, 4, 8, 12, 16):
    y = base - v * scale
    d.line((left, y, right, y), fill=LINE, width=1)
    d.text((left - 40, y - 14), str(v), font=font(22), fill=DIM)
group = (right - left) / 4
bw = 90
for i, m in enumerate(models):
    cx = left + group * i + group / 2
    for j, (v, c) in enumerate(((before[i], RED), (after[i], TEAL))):
        x0 = cx - bw - 6 if j == 0 else cx + 6
        y = base - v * scale
        d.rectangle((x0, y, x0 + bw, base), fill=c)
        label = str(v); tw = d.textlength(label, font=font(30, True))
        d.text((x0 + bw / 2 - tw / 2, y - 40), label, font=font(30, True), fill=FG)
    tw = d.textlength(m, font=font(24))
    d.text((cx - tw / 2, base + 14), m, font=font(24), fill=FG)
d.text((60, 612), "Of 16 logs where the final check never ran. Kaggle, 3 counted runs per model; forecasts sealed before the runs", font=font(20), fill=DIM)
d.text((60, 640), "(Bitcoin block 970376). Joshua Bauer, iswt.ca", font=font(20), fill=DIM)
img.save("coat-check-chart-2026-10-07.png")
print("chart written")
