import os
import asyncio
from playwright.async_api import async_playwright
import requests

TOKEN = os.getenv("TELEGRAM_TOKEN", "").strip()
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()
URL_OBJETIVO = "https://tickets.oneboxtds.com"

def enviar_telegram(mensaje):
    if not TOKEN or not CHAT_ID:
        return
    url = f"https://api.telegram.org{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": mensaje}
    try:
        requests.post(url, data=payload, timeout=10)
    except:
        pass

async def check_tickets():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
        page = await context.new_page()
        
        try:
            await page.goto(URL_OBJETIVO, wait_until="commit", timeout=60000)
            await asyncio.sleep(15)
            
            content = (await page.content()).upper()
            
            # Si el código HTML contiene estas palabras y NO contiene "AGOTADAS"
            if any(x in content for x in ["TRIBUNA", "RIO", "MARCADOR", "GOL"]) and "AGOTADAS" not in content:
                enviar_telegram("HAY ENTRADAS DISPONIBLES: " + URL_OBJETIVO)
            else:
                print("No se detectan entradas.")
                
        except Exception as e:
            # Si hay CUALQUIER error, enviamos mensaje de texto plano
            enviar_telegram("ERROR EN EL BOT: " + str(e)[:50])
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(check_tickets())

