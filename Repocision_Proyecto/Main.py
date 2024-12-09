#Comandos para probar todo incluidos en en documento



from flask import Flask, request, jsonify
import pandas as pd
from pymongo import MongoClient

# Inicializamos Flask y MongoDB
app = Flask(__name__)
client = MongoClient("mongodb://localhost:27017/")
db = client["LeyCaldera"]


#Implementación de la cual estoy paarticularmente orgulloso.
#Agarra las coordenadas que se le da en rango (Por ejemplo /importar/Juntas/A1:J10) y con esas coordenadas sabe dónde revisar el excel
#Por si alguna persona quiere importar un excel donde los valores no estén en el mismo lugar
@app.route('/importar/<string:File>/<string:rangos>', methods=['POST'])
def importar_datos(File, rangos):
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
        datos = pd.read_excel(archivo, header=None, usecols=columnas_excel, skiprows=filas_saltar, nrows=filas_leer) #Aqui es donde toma esos datos que le pasamos

        #Problablemente hay mejores maneras de hacer esto, pero se hizo lo que se pudo con el tiempo
        if File == "Hogares":
            datos.columns = [
                "Tipo de Beneficiario", "Hogar", "ID", "Tiempo de Vigencia", "Distrito",
                "Ubicacion", "Telefono", "Correo", "Puntaje", "Monto Solicitado"
            ]
        elif File == "Instituciones":
            datos.columns = [
                "Tipo de Beneficiario", "ID", "Tiempo de Vigencia", "Distrito",
                "Ubicacion", "Telefono", "Correo", "Descripcion", "Monto Solicitado"
            ]
        elif File == "Juntas":
            datos.columns = [
                "Tipo de Beneficiario", "Juntas", "ID", "Tiempo de Vigencia", "Distrito",
                "Ubicacion", "Telefono", "Correo", "Director", "Monto Solicitado"
            ]
        else:
            return jsonify({"error": f"La colección '{File}' no está soportada."}), 400

        file_db = db[File]
        file_db.insert_many(datos.to_dict(orient="records"))
        return jsonify({"message": f"Datos importados exitosamente a la colección '{File}'."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500



# Aqui se inserta manualmente
@app.route('/insertar/<string:File>', methods=['POST'])
def insertar_datos(File):
    try:

        datos = request.get_json()


        if not datos:
            return jsonify({"error": "Falta el cuerpo de la solicitud con los datos"}), 400


        if isinstance(datos, dict):
            datos = [datos]


        file_db = db[File]
        resultado = file_db.insert_many(datos)

        return jsonify({
            "message": f"Datos insertados exitosamente",
            "inserted_ids": [str(id) for id in resultado.inserted_ids]
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500





@app.route('/obtener_datos/<string:coleccion>', methods=['GET'])
def obtener_datos(coleccion):
    try:
        if coleccion not in ["Hogares", "Instituciones", "Juntas"]:
            return jsonify({"error": f"La colección '{coleccion}' no está soportada."}), 400


        datos = db[coleccion].find({}, {"Tipo de Beneficiario": 1, "Monto Solicitado": 1, "_id": 0})
        resultados = list(datos)

        return jsonify(resultados), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)