import subprocess
import sys

def instalar_paquete(paquete):
    try:
        __import__(paquete)
        print(f"El paquete {paquete} ya está instalado.")
    except ImportError:
        print(f"El paquete {paquete} no está instalado. Instalando...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", paquete])

instalar_paquete("flask")
from flask import Flask

app = Flask(__name__)

@app.route("/prueba")
def prueba():
    print("Funciona")
    return "Todo correcto"

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5000,debug=True)