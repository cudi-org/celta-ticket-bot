import requests
import os

IPS_ORIGEN = ["54.154.43.114", "52.51.125.210", "99.80.101.18", "34.249.200.190"]
PATH_API = "/rccelta/products/2730371/prices?viewCode=V_blockmap"
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def enviar_telegram(mensaje):
    url = f"https://api.telegram.org{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": mensaje, "parse_mode": "Markdown"}
    requests.post(url, data=payload)

def check_tickets():
    headers = {
        "Host": "tickets.oneboxtds.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Origin": "https://tickets.oneboxtds.com"
    }

    for ip in IPS_ORIGEN:
        # Probamos con HTTPS (puerto 443) y desactivando la verificación de certificado
        url = f"https://{ip}{PATH_API}"
        try:
            print(f"Intentando conectar a {ip}...")
            response = requests.get(url, headers=headers, timeout=10, verify=False)
            
            if response.status_code == 200:
                data = response.json()
                sectores = []
                for zona in data:
                    libres = zona.get("availability", {}).get("available", 0)
                    if libres > 0:
                        nombre = zona.get("name", "Zona")
                        precio = "N/A"
                        rates = zona.get("rates", [])
                        # Corrección: rates es una lista, hay que coger el primer elemento
                        if rates and len(rates) > 0:
                            precio = rates[0].get("price", {}).get("total", "N/A")
                        sectores.append(f"✅ *{nombre}*\n      💰 {precio}€ | 🎫 {libres} libres")

                if sectores:
                    mensaje = "⚽ *ENTRADAS CELTA DETECTADAS*\n\n" + "\n".join(sectores)
                    mensaje += "\n\n🔗 [COMPRAR](https://tickets.oneboxtds.com)"
                    enviar_telegram(mensaje)
                    print(f"¡Éxito con IP {ip}!")
                    return
                else:
                    print(f"IP {ip} conectada pero no hay entradas.")
            else:
                print(f"IP {ip} respondió con error {response.status_code}")
        except Exception as e:
            print(f"Fallo en IP {ip}: {e}")

if __name__ == "__main__":
    check_tickets()

