# -*- coding: utf-8 -*-
"""ÜSTAD KENAN // SİBER OPERASYON MERKEZİ — ekran görüntüsü üretici (Chrome headless + CDP)
Kullanım: python ekran-cek.py
Çıktı: ekranlar/00-kapak · 01-whitehat · 02-blackops · 03-holo · 04-synthwave · 05-dort-surum
       · 06-kimlik · 07-cephe · 08-egitim · 09-yayin · 10-radyo · 11-mobil
"""
import asyncio, base64, json, os, subprocess, sys, tempfile, time, urllib.request
import websockets
from PIL import Image, ImageDraw, ImageFont

S = os.path.dirname(os.path.abspath(__file__))
CIKTI = os.path.join(S, "ekranlar")
CH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

SURUMLER = [
    ("index.html", "01-whitehat", "WHITE HAT", (0, 255, 156)),
    ("Ustad-Kenan-Cyber-BlackOps.html", "02-blackops", "BLACK-OPS", (255, 59, 92)),
    ("Ustad-Kenan-Cyber-Holo.html", "03-holo", "HOLO", (0, 212, 255)),
    ("Ustad-Kenan-Cyber-Synthwave.html", "04-synthwave", "SYNTHWAVE", (255, 60, 200)),
]
BOLUMLER = [("kimlik", "06-kimlik"), ("cephe", "07-cephe"), ("egitim", "08-egitim"),
            ("yayin", "09-yayin"), ("radyo", "10-radyo")]


async def main():
    os.makedirs(CIKTI, exist_ok=True)
    port = 9900 + (os.getpid() % 90)
    profil = os.path.join(tempfile.gettempdir(), "ops%d" % time.time())
    ilk = "file:///" + os.path.join(S, SURUMLER[0][0]).replace("\\", "/")
    p = subprocess.Popen([CH, "--headless=new", "--remote-debugging-port=%d" % port,
        "--user-data-dir=" + profil, "--window-size=1600,1000", "--no-first-run",
        "--allow-file-access-from-files", "--force-device-scale-factor=1", "--hide-scrollbars",
        "--mute-audio", ilk], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    u = None
    for _ in range(90):
        try:
            for t in json.load(urllib.request.urlopen("http://127.0.0.1:%d/json" % port, timeout=2)):
                if t.get("type") == "page" and t.get("webSocketDebuggerUrl"):
                    u = t["webSocketDebuggerUrl"]
            if u:
                break
        except Exception:
            pass
        time.sleep(0.4)
    if not u:
        print("HATA: sekme yok"); p.terminate(); return

    uretilen = {}
    try:
        async with websockets.connect(u, max_size=300 * 1024 * 1024) as ws:
            n = [0]
            async def cmd(m, **k):
                n[0] += 1
                await ws.send(json.dumps({"id": n[0], "method": m, "params": k}))
                while True:
                    r = json.loads(await ws.recv())
                    if r.get("id") == n[0]:
                        return r
            async def js(ifade):
                r = await cmd("Runtime.evaluate", expression=ifade, returnByValue=True, awaitPromise=True)
                return r.get("result", {}).get("result", {}).get("value")
            async def boyut(en, boy):
                await cmd("Emulation.setDeviceMetricsOverride", width=en, height=boy, deviceScaleFactor=1, mobile=(en < 600))
            async def cek(ad):
                s = await cmd("Page.captureScreenshot", format="png")
                yol = os.path.join(CIKTI, ad + ".png")
                open(yol, "wb").write(base64.b64decode(s["result"]["data"]))
                im = Image.open(yol)
                uretilen[ad] = yol
                print("  %-16s %s  %d bayt" % (ad, im.size, os.path.getsize(yol)))
                return yol
            async def git(dosya, bekle=3.0):
                await cmd("Page.navigate", url="file:///" + os.path.join(S, dosya).replace("\\", "/"))
                await asyncio.sleep(bekle)

            await cmd("Runtime.enable"); await cmd("Page.enable")
            await js("window.onerror=function(e){window.__h=(window.__h||[]).concat(String(e));}")
            await asyncio.sleep(3.5)

            # 4 sürüm — aynı bölüm, dört renk düzeni
            for dosya, ad, etiket, renk in SURUMLER:
                await boyut(1600, 1000)
                await git(dosya)
                await js("window.scrollTo(0,0)")
                await asyncio.sleep(1.2)
                await cek(ad)
                h = await js("String(window.__h || 'yok')")
                if h != "yok":
                    print("     ! JS hatası:", h[:150])

            # index bölümleri
            await git("index.html")
            for bid, ad in BOLUMLER:
                g = await js("(() => { const e = document.getElementById('%s'); if (!e) return 'yok'; e.scrollIntoView({block:'start'}); return 'tamam'; })()" % bid)
                await asyncio.sleep(2.4)
                await cek(ad)
                print("     (%s: %s)" % (bid, g))

            # mobil
            await boyut(430, 932)
            await js("window.scrollTo(0,0)")
            await asyncio.sleep(2.0)
            await cek("11-mobil")
    finally:
        p.terminate()

    # 05-dort-surum.png — 2x2 vitrin
    GW, GH = 780, 487
    VEN, VBOY = GW * 2 + 20 * 3, GH * 2 + 20 * 3 + 74
    v = Image.new("RGB", (VEN, VBOY), (2, 6, 4))
    dv = ImageDraw.Draw(v)
    fb = ImageFont.truetype("C:/Windows/Fonts/consolab.ttf", 30)
    fk = ImageFont.truetype("C:/Windows/Fonts/consolab.ttf", 20)
    dv.text((22, 20), "ÜSTAD KENAN // SİBER OPERASYON MERKEZİ  ·  4 SÜRÜM", font=fb, fill=(0, 255, 156))
    for i, (dosya, ad, etiket, renk) in enumerate(SURUMLER):
        im = Image.open(uretilen[ad]).convert("RGB").resize((GW, GH), Image.LANCZOS)
        x = 20 + (i % 2) * (GW + 20)
        y = 74 + (i // 2) * (GH + 20)
        v.paste(im, (x, y))
        dv.rectangle([x, y, x + GW, y + GH], outline=renk, width=3)
        w = dv.textlength(etiket, font=fk)
        dv.rectangle([x + 12, y + 12, x + 26 + w, y + 44], fill=(0, 0, 0))
        dv.text((x + 18, y + 18), etiket, font=fk, fill=renk)
    v.save(os.path.join(CIKTI, "05-dort-surum.png"))
    print("05-dort-surum.png", v.size)

    # 00-kapak.png
    ana = Image.open(uretilen["01-whitehat"]).convert("RGB")
    mob = Image.open(uretilen["11-mobil"]).convert("RGB")
    G, Y = 1920, 1080
    k = Image.new("RGB", (G, Y), (2, 8, 5))
    dk = ImageDraw.Draw(k)
    for i in range(160):
        a = int(70 - i * 0.42)
        if a <= 0:
            break
        dk.line([(i * 12, 150), (i * 12 + 12, 150)], fill=(0, a, int(a * 0.62)), width=4)
    dk.rectangle([0, 0, G - 1, Y - 1], outline=(0, 90, 55), width=3)
    fb = ImageFont.truetype("C:/Windows/Fonts/consolab.ttf", 46)
    fo = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 21)
    fk2 = ImageFont.truetype("C:/Windows/Fonts/consolab.ttf", 19)
    fkt = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 18)
    dk.text((52, 26), "ÜSTAD KENAN // SİBER OPERASYON MERKEZİ", font=fb, fill=(0, 255, 156))
    dk.text((56, 92), "11 bölüm · 4 renk sürümü · matrix yağmuru · tek dosya · çevrimdışı açılır", font=fo, fill=(150, 200, 180))
    a1 = ana.copy(); a1.thumbnail((980, 620), Image.LANCZOS)
    k.paste(a1, (52, 170))
    dk.rectangle([52, 170, 52 + a1.width, 170 + a1.height], outline=(0, 140, 90), width=3)
    m1 = mob.copy(); m1.thumbnail((236, 620), Image.LANCZOS)
    x2 = 52 + a1.width + 24
    k.paste(m1, (x2, 170))
    dk.rectangle([x2, 170, x2 + m1.width, 170 + m1.height], outline=(0, 140, 90), width=3)
    px = x2 + m1.width + 26
    dk.rounded_rectangle([px, 170, G - 52, 170 + a1.height], radius=10, fill=(5, 12, 9), outline=(0, 70, 50), width=2)
    dk.text((px + 20, 188), "BÖLÜMLER", font=fk2, fill=(0, 255, 156))
    dk.line([(px + 20, 218), (G - 72, 218)], fill=(0, 70, 50), width=1)
    satirlar = [("Kimlik Kayıtları", "savunma profili"), ("Cephe Haritası", "tehdit görünümü"),
                ("Sertifika Deposu", "eğitim belgeleri"), ("Operasyon Günlüğü", "kayıt defteri"),
                ("Savunma Eğitimi", "adım adım dersler"), ("Etik & Felsefe", "beyaz şapka ilkeleri"),
                ("Güvenli Hat", "iletişim hattı"), ("Canlı Yayın", "TV odası"),
                ("Radyo Dinle", "istasyon listesi"), ("Operasyon Takvimi", "planlama"),
                ("4 renk sürümü", "white hat · black-ops · holo · synthwave")]
    yy = 232
    for a, b in satirlar:
        dk.text((px + 20, yy), "▸", font=fk2, fill=(0, 200, 130))
        dk.text((px + 40, yy), a, font=fk2, fill=(226, 240, 236))
        w = dk.textlength(a, font=fk2)
        dk.text((px + 46 + w, yy + 1), b, font=fkt, fill=(140, 168, 158))
        yy += 33
    dk.text((52, Y - 42), "matrix yağmuru + tarama çizgileri · tek dosya HTML · internetsiz çalışır", font=fkt, fill=(120, 150, 140))
    dk.text((G - 340, Y - 42), "© 2026 ÜSTAD KENAN KUZUCU", font=fkt, fill=(110, 140, 130))
    k.save(os.path.join(CIKTI, "00-kapak.png"))
    print("00-kapak.png üretildi")

asyncio.run(main())
