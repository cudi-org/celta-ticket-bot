import cloudscraper
import requests
import os
import re

# URL alternativa (API de sesión)
URL_PARTIDO = "https://tickets.oneboxtds.com/rccelta/products/2730371/prices?viewCode=V_blockmap"
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
PRECIO_ALERTA = 200
PRECIO_CHOLLO = 45

def enviar_telegram(mensaje):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": mensaje, "parse_mode": "Markdown"}
    requests.post(url, data=payload)

def check_tickets():
    # Intentamos con una sesión simulada completa
    session = requests.Session()
    scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False}, sess=session)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'es-ES,es;q=0.9',
        'Origin': 'https://tickets.oneboxtds.com',
        'Referer': 'https://tickets.oneboxtds.com/rccelta/select/2730371?viewCode=V_blockmap'
    }
    
    try:
        # Hacemos una petición previa a la home para pillar cookies
        scraper.get("https://tickets.oneboxtds.com/rccelta/select/2730371", headers=headers, timeout=15)
        
        # Ahora vamos a por los precios
        response = scraper.get(URL_PARTIDO, headers=headers, timeout=15)
        
        if response.status_code == 200:
            print("¡CONEXIÓN EXITOSA!")
            precios = re.findall(r'"amount":\s*(\d+)', response.text)
            
            if not precios: # Si no es JSON puro, buscamos números sueltos
                precios = re.findall(r'(\d+)€', response.text) or re.findall(r'(\d+)\s*€', response.text)

            precios_encontrados = [int(p) for p in precios if 15 <= int(p) <= 400]
            
            if precios_encontrados:
                min_precio = min(precios_encontrados)
                print(f"Precio detectado: {min_precio}€")
                
                if min_precio <= PRECIO_CHOLLO:
                    enviar_telegram(f"🚨🚨 ¡CHOLLO! Entradas a *{min_precio}€*")
                elif min_precio <= PRECIO_ALERTA:
                    enviar_telegram(f"⚽ Entradas Celta: *{min_precio}€*")
            else:
                print("No hay precios disponibles en este momento.")
        else:
            print(f"Error {response.status_code}. OneBox nos sigue bloqueando.")
            # Si falla, mandamos un aviso una sola vez para saberlo
            # enviar_telegram("⚠️ El bot está siendo bloqueado por la web del Celta.")
            
    except Exception as e:
        print(f"Fallo crítico: {e}")

if __name__ == "__main__":
    check_tickets()
