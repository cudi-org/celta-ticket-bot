import requests
import os

URL_API = "http://178.255.227.10"
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def enviar_telegram(mensaje):
    url = f"https://api.telegram.org{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": mensaje, "parse_mode": "Markdown"}
    requests.post(url, data=payload)

def check_tickets():
    session = requests.Session()
    
    headers = {
        "Host": "tickets.oneboxtds.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "es-ES,es;q=0.9",
        "Origin": "https://tickets.oneboxtds.com",
        "Referer": "https://tickets.oneboxtds.com",
        "Connection": "keep-alive"
    }
    
    try:
        session.get("http://178.255.227.10", headers=headers, timeout=20)
        
        response = session.get(URL_API, headers=headers, timeout=20)
        
        if response.status_code == 200:
            try:
                data = response.json()
                sectores_libres = []
                
                for zona in data:
                    libres = zona.get("availability", {}).get("available", 0)
                    if libres > 0:
                        nombre = zona.get("name", "Zona")
                        precio = "N/A"
                        rates = zona.get("rates", [])
                        if rates and isinstance(rates, list):
                            # Accedemos al primer elemento de la lista 'rates'
                            precio = rates[0].get("price", {}).get("total", "N/A")
                        
                        sectores_libres.append(f"✅ *{nombre}*\n      💰 {precio}€ | 🎫 {libres} libres")

                if sectores_libres:
                    mensaje = "⚽ *ENTRADAS CELTA DETECTADAS*\n\n" + "\n".join(sectores_libres)
                    mensaje += "\n\n🔗 [COMPRAR](https://tickets.oneboxtds.com)"
                    enviar_telegram(mensaje)
                    print("Éxito: Mensaje enviado.")
                else:
                    print("Todo agotado.")
            except:
                print("Error: El servidor no devolvió JSON. Posible bloqueo.")
                print(f"Contenido recibido: {response.text[:200]}")
        else:
            print(f"Error de servidor: {response.status_code}")
            
    except Exception as e:
        print(f"Fallo en la ejecución: {e}")

if __name__ == "__main__":
    check_tickets()
