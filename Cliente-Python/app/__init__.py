from flask import Flask

app = Flask(__name__)

# Configurar la clave secreta
app.secret_key = "clave_secreta_super_segura"  # Cambia esto por algo único y seguro

# Importar rutas después de inicializar `app`
from app.routes.routes import *
