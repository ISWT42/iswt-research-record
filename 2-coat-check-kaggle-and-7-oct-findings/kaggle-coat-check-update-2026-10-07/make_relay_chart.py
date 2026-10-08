"""Chart for the coat-check relay result (sealed 7 Oct 2026, Workbench/coat-check-relay-2026-10-07/runs-real-1-score.txt). Pillow only."""
from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 675
BG, FG, DIM, LINE = "#0f1220", "#ecebf5", "#aeb3cd", "#343a58"
RED, TEAL = "#e2725b", "#4fb3bf"
arms = ["Agent grades\nitself", "Ticket + a\nchance to fix", "Next agent\ncertifies first", "Work first,\ncertify after"]
false_done = [16, 7, 11, 9]   # false_done_at_end_per_job, of 36
passing = [14, 21, 18, 24]    # final_pass_per_job, of 36


def font(size, bold=False):
    for name in (("segoeuib.ttf" if bold else "segoeui.ttf"), ("arialbd.ttf" if bold else "arial.ttf")):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()


img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)
d.text((60, 30), "12 real coding jobs, 4 small models: who said \"done\" falsely?", font=font(36, True), fill=FG)
d.rectangle((60, 100, 84, 124), fill=RED); d.text((96, 96), 'Said "done", hidden tests failed', font=font(24), fill=FG)
d.rectangle((520, 100, 544, 124), fill=TEAL); d.text((556, 96), "Jobs that actually pass the hidden tests", font=font(24), fill=FG)
top, base, left, right = 165, 525, 110, 1150
mx = 28
scale = (base - top) / mx
for v in (0, 7, 14, 21, 28):
    y = base - v * scale
    d.line((left, y, right, y), fill=LINE, width=1)
    d.text((left - 40, y - 14), str(v), font=font(22), fill=DIM)
group = (right - left) / 4
bw = 90
for i, a in enumerate(arms):
    cx = left + group * i + group / 2
    for j, (v, c) in enumerate(((false_done[i], RED), (passing[i], TEAL))):
        x0 = cx - bw - 6 if j == 0 else cx + 6
        y = base - v * scale
        d.rectangle((x0, y, x0 + bw, base), fill=c)
        label = str(v); tw = d.textlength(label, font=font(30, True))
        d.text((x0 + bw / 2 - tw / 2, y - 40), label, font=font(30, True), fill=FG)
    for k, line in enumerate(a.split("\n")):
        tw = d.textlength(line, font=font(22))
        d.text((cx - tw / 2, base + 10 + k * 26), line, font=font(22), fill=FG)
d.text((60, 600), "Of 36 jobs per arm (3 chains of 4 jobs, 3 repeats). Grades itself vs ticket + fix: 16 vs 7, exact McNemar p = 0.004.", font=font(20), fill=DIM)
d.text((60, 628), "Design and forecasts sealed before the run; cost US$0.12 in all. Joshua Bauer, iswt.ca", font=font(20), fill=DIM)
img.save("coat-check-relay-chart-2026-10-07.png")
print("chart written")
