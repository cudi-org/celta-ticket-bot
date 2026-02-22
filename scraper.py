import cloudscraper
from bs4 import BeautifulSoup
import requests
import os

# Configuración
URL_PARTIDO = "https://tickets.oneboxtds.com/rccelta/select/2730371?viewCode=V_blockmap"
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
PRECIO_LIMITE = 40 

def enviar_telegram(mensaje):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": mensaje}
    requests.post(url, data=payload)

def check_tickets():
    scraper = cloudscraper.create_scraper()
    response = scraper.get(URL_PARTIDO)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        precios_encontrados = []
        
        for elemento in soup.find_all(string=True):
            if '€' in elemento:
                try:
                    valor = int(''.join(filter(str.isdigit, elemento)))
                    if 10 < valor < 500: # Filtro para evitar errores de lectura
                        precios_encontrados.append(valor)
                except:
                    continue
        
        if precios_encontrados:
            min_precio = min(precios_encontrados)
            if min_precio <= PRECIO_LIMITE:
                enviar_telegram(f"⚽ ¡Entradas Celta! Precio detectado: {min_precio}€\nLink: {URL_PARTIDO}")
        else:
            print("No se detectan precios aún.")
    else:
        print(f"Error de acceso: {response.status_code}")

if __name__ == "__main__":
    check_tickets()
