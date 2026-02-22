import cloudscraper
from bs4 import BeautifulSoup
import requests
import os

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
    scraper = cloudscraper.create_scraper()
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'es-ES,es;q=0.9',
        'Referer': 'https://rccelta.es/'
    }
    
    try:
        response = scraper.get(URL_PARTIDO, headers=headers)
        
        if response.status_code == 200:
            print("¡Conexión exitosa!")
            # Al ser una API, buscamos precios en el texto crudo
            texto = response.text
            precios_encontrados = []
            
            # Buscamos números que parezcan precios en el JSON/HTML
            import re
            # Busca números seguidos o precedidos de € o dentro de campos de precio
            posibles_precios = re.findall(r'\d+(?:\.\d+)?', texto)
            
            for p in posibles_precios:
                valor = int(float(p))
                # Filtramos para que sean precios realistas de entradas
                if 15 <= valor <= 300: 
                    precios_encontrados.append(valor)
            
            if precios_encontrados:
                min_precio = min(precios_encontrados)
                print(f"Precio detectado: {min_precio}€")
                
                if min_precio <= PRECIO_CHOLLO:
                    msg = f"🚨🚨 ¡CHOLLO DETECTADO! 🚨🚨\n\nEntradas por solo *{min_precio}€*.\nLink: https://rccelta.es/entradas/"
                    enviar_telegram(msg)
                elif min_precio <= PRECIO_ALERTA:
                    msg = f"⚽ Entradas Celta disponibles: *{min_precio}€*\nLink: https://rccelta.es/entradas/"
                    enviar_telegram(msg)
            else:
                print("No se encontraron precios en el contenido.")
                
        else:
            print(f"Error: {response.status_code}. La web sigue bloqueando el acceso.")
            
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")

if __name__ == "__main__":
    check_tickets()
