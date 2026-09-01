from flask import Flask
import requests, time, threading, os
from datetime import datetime

app = Flask(__name__)

IOL_USER = os.environ.get("IOL_USER")
IOL_PASS = os.environ.get("IOL_PASS")
PESOS_POR_COMPRA = 19000

def obtener_token():
    r = requests.post("https://api.invertironline.com/token",
        data={"username": IOL_USER, "password": IOL_PASS, "grant_type": "password"})
    return r.json()["access_token"]

def comprar_todo(token, disponible):
    h = {"Authorization": f"Bearer {token}"}
    # Trae precio real de AAPL
    try:
        rp = requests.get("https://api.invertironline.com/api/v2/bCBA/Titulos/AAPL/Cotizacion", headers=h).json()
        precio = rp.get('ultimoPrecio', 18000)
    except:
        precio = 18000
    
    cantidad = int(disponible // precio)
    if cantidad < 1: cantidad = 1
    
    data = {"mercado": "bCBA", "simbolo": "AAPL", "cantidad": cantidad, "precio": precio, "validez": datetime.now().strftime("%Y-%m-%d"), "tipo": "inmediata"}
    r = requests.post("https://api.invertironline.com/api/v2/operar/comprar", json=data, headers=h)
    print(f"COMPRA COMPUESTA: {cantidad} x AAPL => {r.text}")

def loop_cazador():
    print("✅ CAZADOR V-FINAL COMPUESTO 24/7 INICIADO - TODO ADENTRO")
    token = obtener_token()
    while True:
        try:
            h = {"Authorization": f"Bearer {token}"}
            r = requests.get("https://api.invertironline.com/api/v2/estadocuenta", headers=h).json()
            disponible = r.get('disponible', 0)
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Saldo: ${disponible}")

            while disponible >= PESOS_POR_COMPRA:
                comprar_todo(token, disponible)
                # vuelve a consultar saldo
                r = requests.get("https://api.invertironline.com/api/v2/estadocuenta", headers=h).json()
                disponible = r.get('disponible', 0)
                time.sleep(5)

        except Exception as e:
            print(f"Error: {e} - reconectando...")
            time.sleep(30)
            try: token = obtener_token()
            except: pass
        time.sleep(60)

@app.route('/')
def home():
    return "CAZADOR V-FINAL VIVO - TODO INVERTIDO COMPUESTO OK"

threading.Thread(target=loop_cazador, daemon=True).start()
