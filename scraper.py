import os
import asyncio
from playwright.async_api import async_playwright
import requests

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
URL_OBJETIVO = "https://tickets.oneboxtds.com"

def enviar_telegram(mensaje):
    url = f"https://api.telegram.org{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": mensaje, "parse_mode": "Markdown"}
    requests.post(url, data=payload)

async def check_tickets():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={'width': 1280, 'height': 800}
        )
        page = await context.new_page()
        
        try:
            await page.goto(URL_OBJETIVO, wait_until="commit", timeout=60000)
            
            # Esperamos a que aparezca cualquier texto de zona o el mapa
            await page.wait_for_selector("body", timeout=20000)
            await asyncio.sleep(12)
            
            content = await page.content()
            
            # Buscamos términos que aparecen cuando hay entradas cargadas
            detectado = any(x in content.upper() for x in ["TRIBUNA", "RIO", "MARCADOR", "GOL", "ZONA", "PRECIO"])
            
            if detectado and "AGOTADAS" not in content.upper():
                enviar_telegram(f"⚽ *¡ENTRADAS CELTA DETECTADAS!*\n\n🔗 [COMPRAR]({URL_OBJETIVO})")
                print("Éxito: Entradas encontradas y aviso enviado.")
            else:
                print("Página vacía de entradas o todo agotado.")
                
        except Exception as e:
            print(f"Error: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(check_tickets())
