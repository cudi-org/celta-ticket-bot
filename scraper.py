import requests
import os
import re

URL_API = "http://178.255.227.10"
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
PRECIO_ALERTA = 200
PRECIO_CHOLLO = 45

def enviar_telegram(mensaje):
    url = f"https://api.telegram.org{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": mensaje, "parse_mode": "Markdown"}
    requests.post(url, data=payload)

def check_tickets():
    headers = {
        "Host": "tickets.oneboxtds.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://tickets.oneboxtds.com",
        "Referer": "https://tickets.oneboxtds.com"
    }
    
    try:
        response = requests.get(URL_API, headers=headers, timeout=20)
        
        if response.status_code == 200:
            content = response.text
            precios = re.findall(r'"amount":\s*(\d+)', content)
            
            if not precios:
                precios = re.findall(r'(\d+)€', content) or re.findall(r'(\d+)\s*€', content)

            precios_encontrados = [int(p) for p in precios if 15 <= int(p) <= 400]
            
            if precios_encontrados:
                min_precio = min(precios_encontrados)
                if min_precio <= PRECIO_CHOLLO:
                    enviar_telegram(f"🚨🚨 ¡CHOLLO CELTA! Entradas a *{min_precio}€*")
                elif min_precio <= PRECIO_ALERTA:
                    enviar_telegram(f"⚽ Entradas Celta: *{min_precio}€*")
            else:
                print("No hay precios disponibles.")
        else:
            print(f"Error {response.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_tickets()
