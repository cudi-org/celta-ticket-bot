import os
import asyncio
from playwright.async_api import async_playwright
import requests

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
URL_OBJETIVO = "https://tickets.oneboxtds.com"

def enviar_telegram(mensaje, foto_path=None):
    if not TOKEN or not CHAT_ID:
        print("Error: TELEGRAM_TOKEN o CHAT_ID no configurados.")
        return
    
    url_base = f"https://api.telegram.org{TOKEN}"
    try:
        if foto_path:
            with open(foto_path, "rb") as f:
                requests.post(f"{url_base}/sendPhoto", data={"chat_id": CHAT_ID, "caption": mensaje}, files={"photo": f})
        else:
            requests.post(f"{url_base}/sendMessage", data={"chat_id": CHAT_ID, "text": mensaje, "parse_mode": "Markdown"})
    except Exception as e:
        print(f"Error enviando a Telegram: {e}")

async def check_tickets():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={'width': 1280, 'height': 800}
        )
        page = await context.new_page()
        
        try:
            print("Navegando a la web del Celta...")
            await page.goto(URL_OBJETIVO, wait_until="networkidle", timeout=60000)
            await asyncio.sleep(15)
            
            foto = "debug_celta.png"
            await page.screenshot(path=foto)
            
            content = await page.content()
            palabras = ["TRIBUNA", "RIO", "MARCADOR", "GOL", "PRECIO", "DISPONIBLE", "SELECT"]
            detectado = any(x in content.upper() for x in palabras)
            
            if detectado and "AGOTADAS" not in content.upper():
                enviar_telegram(f"⚽ *¡ENTRADAS DETECTADAS!*\n\n🔗 [LINK]({URL_OBJETIVO})", foto)
            else:
                enviar_telegram("⚠️ No veo entradas en el código, pero te mando foto:", foto)
                
        except Exception as e:
            print(f"Fallo: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(check_tickets())
