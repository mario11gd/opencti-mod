import subprocess
import sys

def instalar_paquete(paquete):
    try:
        __import__(paquete)
        print(f"El paquete {paquete} ya está instalado.")
    except ImportError:
        print(f"El paquete {paquete} no está instalado. Instalando...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", paquete])

instalar_paquete("app")
from app import app

@app.route("/prueba")
def prueba():
    print("Funciona")

