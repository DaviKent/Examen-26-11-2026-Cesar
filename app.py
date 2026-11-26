import os

from dotenv import load_dotenv
from flask import Flask, jsonify
from pymongo import MongoClient
from pymongo.collation import Collation

load_dotenv()

# ---------------------------------------------------------------
# Conexión (los valores salen del archivo .env)
# ---------------------------------------------------------------
client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("DB_NAME")]               # CURSOS_CTPI_2026-SUNOMBRE
aprendices = db[os.getenv("COLLECTION_NAME")]   # APRENDICES_SUAPELLIDO

# Ignora mayúsculas/minúsculas y tildes (Formacion == FORMACIÓN)
COL = Collation(locale="es", strength=1)

# ---------------------------------------------------------------
# Nombres de los campos en tu colección.
# AJUSTA los que no coincidan con los encabezados de tu CSV
# (míralos en MongoDB Compass).
# ---------------------------------------------------------------
F_FICHA = "FICHA"
F_NOMBRE = "NOMBRE"
F_AP1 = "PRIMER_APELLIDO"
F_AP2 = "SEGUNDO_APELLIDO"
F_PROGRAMA = "PROGRAMA"
F_NIVEL = "NIVEL_DE_FORMACION"
F_ESTADO_APRENDIZ = "ESTADO_APRENDIZ"
F_ESTADO_FICHA = "ESTADO_FICHA"
F_IDENT = "NUMERO_DOCUMENTO"

NO_ID = {"_id": 0}

app = Flask(__name__)
app.json.ensure_ascii = False      #muestra tildes y ñ correctamente
app.json.sort_keys = False


def proj(*campos):
    """Proyección sin _id con los campos indicados."""
    p = {c: 1 for c in campos}
    p.update(NO_ID)
    return p


#1 Cantidad de aprendices
@app.route("/api/cantidadAprendices")
def cantidad_aprendices():
    cantidad = aprendices.count_documents({})
    return jsonify({"CantidadAprendices": cantidad})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)