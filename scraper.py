import os
import asyncio
from playwright.async_api import async_playwright
import requests

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
URL_OBJETIVO = "https://tickets.oneboxtds.com"

def enviar_telegram(mensaje, foto_path=None):
    url_base = f"https://api.telegram.org{TOKEN}/"
    if foto_path:
        with open(foto_path, "rb") as f:
            requests.post(url_base + "sendPhoto", data={"chat_id": CHAT_ID, "caption": mensaje}, files={"photo": f})
    else:
        requests.post(url_base + "sendMessage", data={"chat_id": CHAT_ID, "text": mensaje, "parse_mode": "Markdown"})

async def check_tickets():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={'width': 1280, 'height': 800}
        )
        page = await context.new_page()
        
        try:
            print("Navegando...")
            await page.goto(URL_OBJETIVO, wait_until="networkidle", timeout=60000)
            
            # Espera generosa para que el mapa y los precios carguen
            await asyncio.sleep(15)
            
            # Guardamos una captura de pantalla para ver qué ve el bot
            foto = "debug_celta.png"
            await page.screenshot(path=foto)
            
            content = await page.content()
            
            # Buscamos indicios de entradas (añado más palabras clave)
            palabras_clave = ["TRIBUNA", "RIO", "MARCADOR", "GOL", "PRECIO", "DISPONIBLE", "SELECT", "ZONA"]
            detectado = any(x in content.upper() for x in palabras_clave)
            
            if detectado:
                enviar_telegram(f"⚽ *¡ENTRADAS CELTA!* [Link]({URL_OBJETIVO})", foto)
            else:
                # Si no detecta nada, nos manda la foto de todas formas para investigar
                enviar_telegram("⚠️ No he detectado texto de entradas. Mira la foto:", foto)
                
        except Exception as e:
            print(f"Error: {e}")
            enviar_telegram(f"❌ Error en el bot: {str(e)}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(check_tickets())

