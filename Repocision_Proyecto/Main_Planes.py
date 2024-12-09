
from flask import Flask, request, jsonify
import pandas as pd
from pymongo import MongoClient


from flask import Flask, request, jsonify
from pymongo import MongoClient

app = Flask(__name__)

# Configuración de la base de datos
client = MongoClient('mongodb://localhost:27017/')
db = client['LeyCaldera']


@app.route('/insertar_plan_asignado', methods=['POST'])
def insertar_plan_asignado():
    try:
        datos = request.get_json()
        if not datos:
            return jsonify({"error": "No se proporcionaron datos para insertar"}), 400

        # Insertar los datos en la colección Plan_Asignado
        db["Plan_Asignado"].insert_one(datos)
        return jsonify({"message": "Datos insertados exitosamente en la colección 'Plan_Asignado'."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/insertar_detalles', methods=['POST'])
def insertar_detalles():
    try:

        datos = request.get_json()
        if not datos:
            return jsonify({"error": "No se proporcionaron datos para insertar"}), 400


        db["Detalles"].insert_one(datos)
        return jsonify({"message": "Datos insertados exitosamente en la colección 'Detalles'."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500







@app.route('/importar_plan_asignado/<string:rangos>', methods=['POST'])
def importar_plan_asignado(rangos):
    try:
        archivo = request.args.get('archivo')
        if not archivo:
            return jsonify({"error": "Falta el parámetro 'archivo'"}), 400


        columnas, filas = rangos.split(':')
        inicio_columna, inicio_fila = columnas[0], int(columnas[1:])
        fin_columna, fin_fila = filas[0], int(filas[1:])
        columnas_excel = f"{inicio_columna}:{fin_columna}"
        filas_saltar = inicio_fila - 1
        filas_leer = fin_fila - inicio_fila + 1


        datos_plan_asignado = pd.read_excel(
            archivo, header=None, usecols=columnas_excel, skiprows=filas_saltar, nrows=filas_leer
        )


        datos_plan_asignado.columns = [
            "Codigo del Plan Asignado", "Institucion", "Encargado", "Periodo", "Descripcion del Proyecto"
        ]


        db["Plan_Asignado"].insert_many(datos_plan_asignado.to_dict(orient="records"))
        return jsonify({"message": "Datos importados exitosamente a la colección 'Plan_Asignado'."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/importar_detalles/<string:rangos>', methods=['POST'])
def importar_detalles(rangos):
    try:
        archivo = request.args.get('archivo')
        if not archivo:
            return jsonify({"error": "Falta el parámetro 'archivo'"}), 400


        columnas, filas = rangos.split(':')
        inicio_columna, inicio_fila = columnas[0], int(columnas[1:])
        fin_columna, fin_fila = filas[0], int(filas[1:])
        columnas_excel = f"{inicio_columna}:{fin_columna}"
        filas_saltar = inicio_fila - 1
        filas_leer = fin_fila - inicio_fila + 1

        # Leer los datos del Excel
        datos_detalles = pd.read_excel(
            archivo, header=None, usecols=columnas_excel, skiprows=filas_saltar, nrows=filas_leer
        )


        datos_detalles.columns = [
            "Detalle", "Prevedor", "Cantidad", "Precio Unitario", "Sub Total"
        ]


        db["Detalles"].insert_many(datos_detalles.to_dict(orient="records"))
        return jsonify({"message": "Datos importados exitosamente a la colección 'Detalles'."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500






if __name__ == '__main__':
    app.run(debug=True)
