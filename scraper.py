import os
import asyncio
from playwright.async_api import async_playwright
import requests

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
URL_OBJETIVO = "https://tickets.oneboxtds.com"

def enviar_telegram(mensaje, foto_path=None):
    if not TOKEN or not CHAT_ID:
        return
    
    t = TOKEN.strip()
    c = CHAT_ID.strip()
    
    try:
        if foto_path:
            url = f"https://api.telegram.org{t}/sendPhoto"
            with open(foto_path, "rb") as f:
                requests.post(url, data={"chat_id": c, "caption": mensaje}, files={"photo": f}, timeout=20)
        else:
            url = f"https://api.telegram.org{t}/sendMessage"
            requests.post(url, data={"chat_id": c, "text": mensaje, "parse_mode": "Markdown"}, timeout=20)
    except:
        pass

async def check_tickets():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={'width': 1280, 'height': 800}
        )
        page = await context.new_page()
        
        try:
            await page.goto(URL_OBJETIVO, wait_until="networkidle", timeout=60000)
            await asyncio.sleep(15)
            
            foto = "debug.png"
            await page.screenshot(path=foto)
            
            content = await page.content()
            palabras = ["TRIBUNA", "RIO", "MARCADOR", "GOL", "PRECIO", "DISPONIBLE"]
            detectado = any(x in content.upper() for x in palabras)
            
            if detectado and "AGOTADAS" not in content.upper():
                enviar_telegram(f"⚽ *ENTRADAS CELTA!*\n\n[LINK]({URL_OBJETIVO})", foto)
            else:
                enviar_telegram("INFO: Foto del estado actual:", foto)
                
        except:
            pass
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(check_tickets())
