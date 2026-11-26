import os

from dotenv import load_dotenv
from flask import Flask, jsonify
from pymongo import MongoClient
from pymongo.collation import Collation

load_dotenv()

# Conexion
client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("DB_NAME")]
aprendices = db[os.getenv("COLLECTION_NAME")]  

# Ignora mayúsculas/minúsculas y tildes
COL = Collation(locale="es", strength=1)

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
#muestra tildes y ñ correctamente
app.json.ensure_ascii = False   
app.json.sort_keys = False


def proj(*campos):
    """Proyección sin _id con los campos indicados."""
    p = {c: 1 for c in campos}
    p.update(NO_ID)
    return p


#1 Consulta
@app.route("/api/cantidadAprendices")
def cantidad_aprendices():
    cantidad=aprendices.count_documents({})
    return jsonify({"CantidadAprendices": cantidad})

#2 Consulta
@app.route("/api/cantidadAprendices/<nivel>")
def cantidad_por_nivel(nivel):
    cantidad=aprendices.count_documents({F_NIVEL: nivel}, collation=COL)
    return jsonify({"CantidadAprendices": cantidad,
                    "Nivel de formacion": nivel.upper()})

#3 Consulta
@app.route("/api/programas/<nivel>")
def programas_por_nivel(nivel):
    lista=aprendices.distinct(F_PROGRAMA, {F_NIVEL: nivel}, collation=COL)
    return jsonify({"nivel de formacion": nivel.upper(),
                    "programas": sorted(lista)})

#4 Consulta
@app.route("/api/certificados/<programa>")
def certificados(programa):
    filtro={F_PROGRAMA: programa, F_ESTADO_APRENDIZ: "Certificado"}
    cursor=aprendices.find(filtro, proj(F_FICHA, F_NOMBRE, F_AP1, F_AP2),
                            collation=COL)
    return jsonify({"Programa": programa,
                    "Aprendices_Certificados": list(cursor)})

#5 Consulta
@app.route("/api/porCertificar/<int:ficha>/<int:cantidad>")
def por_certificar(ficha, cantidad):
    filtro = {F_FICHA: ficha, F_ESTADO_APRENDIZ: "Por certificar"}
    cursor = (aprendices
              .find(filtro,
                    proj(F_FICHA, F_PROGRAMA, F_IDENT, F_NOMBRE, F_AP1, F_AP2),
                    collation=COL)
              .sort(F_AP1, -1)
              .limit(cantidad))
    return jsonify({"Cantidad de Aprendices por Certificar": list(cursor)})

#6 Consulta
@app.route("/api/terminadaUnificacion/<programa>")
def terminada_unificacion(programa):
    filtro = {F_PROGRAMA: programa,
              F_ESTADO_FICHA: "Terminada por unificación"}
    cursor = aprendices.find(
        filtro, proj(F_FICHA, F_IDENT, F_NOMBRE, F_AP1, F_AP2), collation=COL)
    return jsonify({"Programa": programa,
                    "Estado de la ficha": "Terminada por unificación",
                    "Aprendices": list(cursor)})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)