#!/usr/bin/env python3
"""Renders the pictures in the README from the real app, running in the MatrixBOX simulator.

    pip install pillow git+https://github.com/MatrixBOX-dev/simulator
    git clone https://github.com/MatrixBOX-dev/matrixbox
    python3 tools/render_docs.py matrixbox

With playwright installed (pip install playwright, playwright install chromium) it also
takes the screenshot of the settings page. The logo animation is recorded from the
simulator's frame stream, with a made-up example logo.
"""
import json, os, shutil, subprocess, sys, tempfile, time, urllib.request
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
SCALE = 6


def station(name, sid, walk):
    return {"name": name, "country": "de", "operator": "vbb", "id": sid, "walk": walk, "on": 1}


ALEX = station("Alexanderplatz", "de:11000:900100003", 4)
HBF = station("Hauptbahnhof", "de:11000:900003201", 9)
ZOO = station("Zoologischer Garten", "de:11000:900023201", 0)
BASE = {"source": "own", "host": "127.0.0.1", "port": 9090, "stations": [ALEX, HBF, ZOO], "intro": 0, "blink": "off", "walk": "show",
        "ticker_dev": 1}       # the ticker shows the demo server's service notice


def shot(app, tmp, name, frames=60, **changes):
    """One frame of the app with these settings, as a 128x32 image."""
    cfg = dict(BASE)
    cfg.update(changes)
    seed = os.path.join(tmp, name + ".json")
    out = os.path.join(tmp, name + ".png")
    with open(seed, "w") as f: json.dump(cfg, f)
    subprocess.run(["matrixbox", "screenshot", app, "--settings", seed, "--rename-settings", "departuresplus.json",
                    "--size", "X", "--after-frames", str(frames), "--gamma", "3", "-o", out],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return Image.open(out).convert("RGB").resize((128, 32), Image.NEAREST)


def led(im):
    """Draws the frame as round LEDs with a little glow, inside a dark housing."""
    s = SCALE
    w, h = im.size
    lit = Image.new("RGB", (w * s, h * s), (0, 0, 0))
    off = Image.new("RGB", (w * s, h * s), (7, 7, 9))
    dl = ImageDraw.Draw(lit)
    do = ImageDraw.Draw(off)
    px = im.load()
    for y in range(h):
        for x in range(w):
            box = (x * s + 1, y * s + 1, x * s + s - 1, y * s + s - 1)
            do.ellipse(box, fill=(20, 20, 23))
            if sum(px[x, y]) > 24: dl.ellipse(box, fill=px[x, y])
    glow = lit.filter(ImageFilter.GaussianBlur(s * 0.7)).point(lambda v: v * 0.55)
    face = ImageChops.lighter(ImageChops.add(off, glow), lit)
    pad = 3 * s
    panel = Image.new("RGB", (w * s + 2 * pad, h * s + 2 * pad), (255, 255, 255))
    ImageDraw.Draw(panel).rounded_rectangle((0, 0, panel.width - 1, panel.height - 1), radius=2 * s, fill=(26, 26, 30))
    panel.paste(face, (pad, pad))
    return panel


def font(size):
    for path in ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
                 "/usr/share/fonts/truetype/freefont/FreeSans.ttf", "/Library/Fonts/Arial.ttf", "C:/Windows/Fonts/arial.ttf"):
        if os.path.exists(path): return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def bold(size):
    for path in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
                 "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf", "/Library/Fonts/Arial Bold.ttf", "C:/Windows/Fonts/arialbd.ttf"):
        if os.path.exists(path): return ImageFont.truetype(path, size)
    return font(size)


def encode_logo(img, W, H):
    """The same steps as the settings page: fit, drop dark pixels, up to 14 colours, 4 bits a pixel."""
    img = img.convert("RGBA")
    iw, ih = img.size
    k = min(W / iw, H / ih)
    w, h = round(iw * k), round(ih * k)
    c = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    c.alpha_composite(img.resize((w, h), Image.LANCZOS), ((W - w) // 2, (H - h) // 2))
    cnt = {}; ky = []
    for r, g, b, a in c.getdata():
        if a < 128 or r + g + b < 60: ky.append(-1); continue
        q = (r >> 4) << 8 | (g >> 4) << 4 | b >> 4
        ky.append(q); cnt[q] = cnt.get(q, 0) + 1
    pal = [[(q >> 8) * 17, (q >> 4 & 15) * 17, (q & 15) * 17] for q in sorted(cnt, key=lambda q: -cnt[q])[:14]]
    px = []
    for q in ky:
        if q < 0: px.append(0); continue
        R, G, B = (q >> 8) * 17, (q >> 4 & 15) * 17, (q & 15) * 17
        px.append(1 + min(range(len(pal)), key=lambda j: (pal[j][0] - R) ** 2 * 3 + (pal[j][1] - G) ** 2 * 4 + (pal[j][2] - B) ** 2 * 2))
    out = bytearray([76, W & 255, W >> 8, H & 255, H >> 8, len(pal)])
    for p in pal: out += bytes(p)
    if len(px) % 2: px.append(0)
    for i in range(0, len(px), 2): out.append(px[i] << 4 | px[i + 1])
    return bytes(out)


def example_logo():
    """A made-up operator: a teal badge with a route line, EXAMPLE TRANSIT."""
    z = 4
    im = Image.new("RGBA", (128 * z, 32 * z), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    teal = (0, 170, 160, 255); white = (255, 255, 255, 255); lime = (190, 230, 60, 255)
    d.rounded_rectangle((2 * z, 2 * z, 30 * z, 30 * z), radius=6 * z, fill=teal)
    d.line([(7 * z, 22 * z), (13 * z, 22 * z), (19 * z, 10 * z), (25 * z, 10 * z)], fill=white, width=3 * z, joint="curve")
    for x, y in ((7, 22), (25, 10)): d.ellipse(((x - 3) * z, (y - 3) * z, (x + 3) * z, (y + 3) * z), fill=lime)
    d.text((36 * z, 1 * z), "EXAMPLE", font=bold(13 * z), fill=white)
    d.text((37 * z, 18 * z), "TRANSIT", font=bold(10 * z), fill=lime)
    return encode_logo(im, 128, 32)


def frame_stream(seconds, at, action):
    """Frames from the simulator's frame stream, a WebSocket on port 9191, for `seconds`.
    `action` runs `at` seconds in. -> [(time, 128x32 image)]"""
    import base64, socket, struct
    s = socket.create_connection(("127.0.0.1", 9191), timeout=5)
    s.sendall(("GET / HTTP/1.1\r\nHost: 127.0.0.1:9191\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n"
               "Sec-WebSocket-Key: " + base64.b64encode(os.urandom(16)).decode() + "\r\nSec-WebSocket-Version: 13\r\n\r\n").encode())
    buf = b""
    while b"\r\n\r\n" not in buf: buf += s.recv(4096)
    buf = buf.split(b"\r\n\r\n", 1)[1]
    s.settimeout(0.2)
    frames = []
    t0 = time.time(); done = False
    while time.time() - t0 < seconds:
        if not done and time.time() - t0 >= at:
            action(); done = True
        try:
            got = s.recv(65536)
            if not got: break
            buf += got
        except socket.timeout:
            pass
        while len(buf) >= 2:
            n = buf[1] & 127; hl = 2
            if n == 126:
                if len(buf) < 4: break
                n = struct.unpack(">H", buf[2:4])[0]; hl = 4
            elif n == 127:
                if len(buf) < 10: break
                n = struct.unpack(">Q", buf[2:10])[0]; hl = 10
            if len(buf) < hl + n: break
            op = buf[0] & 15; data = buf[hl:hl + n]; buf = buf[hl + n:]
            if op == 2 and data[:1] == b"\xf3":
                w, h = struct.unpack("<HH", data[2:6])
                frames.append((time.time(), Image.frombytes("RGB", (w, h), data[8:8 + w * h * 3])))
    s.close()
    return frames


def logo_gif(app):
    """The example logo coming in by zooming and pulsing, recorded from the running app."""
    env = dict(os.environ, MATRIXBOX_SIMULATOR_GAMMA="3")
    proc = subprocess.Popen(["matrixbox", "app", app, "--size", "X", "--reset"], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    def call(path, data=None):
        r = urllib.request.Request("http://127.0.0.1:8080" + path, data=data, method="POST" if data is not None else "GET")
        return urllib.request.urlopen(r, timeout=10).read()
    try:
        for attempt in range(40):
            time.sleep(1)
            try:
                call("/api/state")
                break
            except Exception:
                pass
        call("/api/config", json.dumps(dict(BASE, logo_secs=6, logo_anim="zoom", logo_pulse="glow")).encode())
        call("/api/logo", example_logo().hex().encode())
        time.sleep(8)
        frames = frame_stream(11, 1.2, lambda: call("/api/set?logo=1"))
    finally:
        proc.terminate()
    imgs = []; durs = []
    for i, (t, im) in enumerate(frames):
        ms = int(round(((frames[i + 1][0] if i + 1 < len(frames) else t + 1.0) - t) * 1000))
        if imgs and (durs[-1] < 90 or im.tobytes() == imgs[-1].tobytes()):      # about ten pictures a second keep the file small
            if durs[-1] < 90: imgs[-1] = im
            durs[-1] += ms
            continue
        imgs.append(im); durs.append(ms)
    if len(imgs) < 10:
        print("too few frames for the logo animation, skipping it")
        return
    pics = [led(im).resize((400, 114), Image.LANCZOS).quantize(colors=64, method=Image.Quantize.MAXCOVERAGE, dither=Image.Dither.NONE) for im in imgs]
    pics[0].save(os.path.join(DOCS, "logo.gif"), save_all=True, append_images=pics[1:],
                 duration=[max(20, round(d / 10) * 10) for d in durs], loop=0, optimize=True)


def sheet(items, columns=2):
    """A white sheet of captioned panels."""
    f = font(22)
    cell = led(items[0][1])
    gap = 34
    cap = 40
    rows = (len(items) + columns - 1) // columns
    out = Image.new("RGB", (columns * cell.width + (columns + 1) * gap, rows * (cell.height + cap + gap) + gap), (255, 255, 255))
    d = ImageDraw.Draw(out)
    for i, (text, im) in enumerate(items):
        x = gap + (i % columns) * (cell.width + gap)
        y = gap + (i // columns) * (cell.height + cap + gap)
        d.text((x + 4, y), text, fill=(40, 40, 46), font=f)
        out.paste(led(im), (x, y + cap))
    return out


def displays(app, tmp):
    title = dict(intro=10, frames=25)
    hero = [(shot(app, tmp, "t1", **title), 1500), (shot(app, tmp, "d1"), 3000),
            (shot(app, tmp, "t2", stations=[HBF, ZOO, ALEX], **title), 1500), (shot(app, tmp, "d2", stations=[HBF, ZOO, ALEX]), 3000),
            (shot(app, tmp, "t3", stations=[ZOO, ALEX, HBF], **title), 1500), (shot(app, tmp, "d3", stations=[ZOO, ALEX, HBF]), 3000)]
    frames = [led(im).quantize(colors=128, dither=Image.Dither.NONE) for im, ms in hero]
    frames[0].save(os.path.join(DOCS, "rotation.gif"), save_all=True, append_images=frames[1:],
                   duration=[ms for im, ms in hero], loop=0)
    sheet([
        ("Station title with its lines and the walking time", hero[0][0]),
        ("Line signets, clock, date and the operator's service notice", hero[1][0]),
        ("Large text: two departures, status row below", shot(app, tmp, "large", font="large", stations=[ZOO, ALEX, HBF])),
        ("Compact text: five rows", shot(app, tmp, "compact", font="compact", status="off", stations=[HBF, ZOO, ALEX])),
        ("One mixed list of all stations", shot(app, tmp, "merged", mode="merged")),
        ("Real-time mark behind live departures, no date", shot(app, tmp, "live", live="wave", live_anim=0, st_date="off")),
        ("Colored text instead of signets, times as 3'", shot(app, tmp, "text", badge="text", time_fmt="tick", stations=[ZOO, ALEX, HBF])),
        ("Any LED tone, here white, and no date", shot(app, tmp, "white", tone="white", st_date="off", stations=[HBF, ZOO, ALEX])),
    ]).save(os.path.join(DOCS, "display.png"))
    A, H, Z = ALEX, HBF, ZOO
    sheet([
        ("Station row on top, status row below", shot(app, tmp, "srow", srow="top", srow_time=1, stations=[A, H, Z])),
        ("Status row on top, clock on the right, icons left", shot(app, tmp, "sttop", st_pos="top", clock_pos="right", st_ticker=0, st_icons="left",
                                                                 icon1="wc", icon1_c="red", icon2="washer", icon2_c="green", stations=[Z, A, H])),
        ("Icons set by Home Assistant", shot(app, tmp, "icons", st_ticker=0, icon1="wc", icon1_c="red", icon2="battery", icon2_c="green",
                                            icon3="sun", icon3_c="yellow", stations=[H, Z, A])),
        ("A color per element", shot(app, tmp, "colors", c_time="#00ff66", c_dest="white", c_clock="#33aaff", c_date="#33aaff", st_bright=1,
                                    c_ticker="#ff66cc", stations=[A, H, Z])),
        ("Bold text", shot(app, tmp, "bold", font_bold=1, stations=[Z, A, H])),
        ("Letters as icons, cut out of a box", shot(app, tmp, "box", st_ticker=0, st_icon_text="box", icon1="/WC", icon1_c="red",
                                                   icon2="/OK", icon2_c="green", icon3="battery", icon3_c="green", ink_black="@BUS", stations=[H, Z, A])),
    ]).save(os.path.join(DOCS, "features.png"))


def settings_page(app):
    """Screenshot of the settings page, served by the app itself."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("playwright is not installed, skipping the settings page")
        return
    proc = subprocess.Popen(["matrixbox", "app", app, "--size", "X", "--reset"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for attempt in range(40):
            time.sleep(1)
            try:
                urllib.request.urlopen("http://127.0.0.1:8080/api/state", timeout=3).read()
                break
            except Exception:
                pass
        req = urllib.request.Request("http://127.0.0.1:8080/api/config", data=json.dumps(dict(BASE, intro=2)).encode(), method="POST")
        urllib.request.urlopen(req, timeout=10).read()
        time.sleep(12)
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path=os.environ.get("DP_CHROME") or None)
            page = browser.new_page(viewport={"width": 500, "height": 1500}, device_scale_factor=1.5)
            page.goto("http://127.0.0.1:8080/")
            page.wait_for_timeout(4000)
            page.screenshot(path=os.path.join(DOCS, "settings.png"))
            browser.close()
    finally:
        proc.terminate()


def main():
    if len(sys.argv) != 2: sys.exit(__doc__)
    app = os.path.join(os.path.abspath(sys.argv[1]), "apps", "departuresplus")
    shutil.copytree(os.path.join(ROOT, "departuresplus"), app, dirs_exist_ok=True)
    os.makedirs(DOCS, exist_ok=True)
    server = subprocess.Popen([sys.executable, os.path.join(ROOT, "tools", "demo_server.py")])
    time.sleep(1)
    try:
        with tempfile.TemporaryDirectory() as tmp:
            displays(app, tmp)
        settings_page(app)
        try: logo_gif(app)
        except Exception as e: print("logo animation skipped:", e)
    finally:
        server.terminate()


if __name__ == "__main__":
    main()
