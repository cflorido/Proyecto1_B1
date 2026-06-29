from flask import Flask, jsonify, render_template, request, send_from_directory
from pathlib import Path
import pandas as pd
import requests

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

app = Flask(
    __name__,
    template_folder=str(TEMPLATES_DIR),
    static_folder=str(STATIC_DIR),
)
API_URL = "http://127.0.0.1:8000"

# ------------ Frontend Routes ------------
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/classify')
@app.route('/clasificar')
def classify_page():
    return render_template('classify.html')

@app.route('/classify-file')
@app.route('/clasificarArchivo')
def classify_file_page():
    return render_template('classify_batch.html')

@app.route('/retrain')
@app.route('/reentreno')
def retrain_page():
    return render_template('retrain.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(app.static_folder, 'favicon.ico', mimetype='image/vnd.microsoft.icon')

# ------------ API Interaction Routes ------------

@app.route('/classify-submit', methods=["POST"])
@app.route('/clasificarEnvio', methods=["POST"])
def classify_submit():
    id_noticia = request.form.get("id")  
    titulo = request.form.get("titulo")
    cuerpo = request.form.get("cuerpo")
    fecha = request.form.get("fecha") 
    
    payload = {
        "ID": id_noticia,  
        "Titulo": titulo,
        "Descripcion": cuerpo,
        "Fecha": fecha  
    }
    try:
        response = requests.post(f"{API_URL}/predict/", json=payload)
        response.raise_for_status()  
        result = response.json()
        clasificacion = "Verdadero" if result["prediction"] == 1 else "Falso"
        probabilidades = result.get("probabilidades", [0, 0])
        response_dict = {
            "titulo": titulo,
            "cuerpo": cuerpo,
            "clasificacion": clasificacion,
            "ProbVerdadera": probabilidades[1],
            "ProbFalsa": probabilidades[0]
        }
    except requests.exceptions.RequestException:
        response_dict = {"error": "No se pudo conectar con la API"}

    return render_template('classify.html', results=response_dict)

def validate_file(file):
    """Verifica si el archivo es válido (CSV no vacío)"""
    if 'file' not in request.files:
        return "No ha enviado el archivo"
    if file.filename == '':
        return "No ha seleccionado un archivo"
    if not file.filename.lower().endswith('.csv'):
        return "Solo se permiten archivos de tipo CSV"
    return None 

@app.route('/classify-file-submit', methods=["POST"])
@app.route('/clasificarEnvioArchivo', methods=["POST"])
def classify_file_submit():
    file = request.files.get('file')
    error = validate_file(file)
    if error:
        return jsonify({"error": error}), 400

    try:
        df = pd.read_csv(file, sep=";")

        noticias = df.to_dict(orient="records")
        response = requests.post(f"{API_URL}/predictMany", json=noticias)
        response.raise_for_status()
        resultados = response.json()
        response_list = []

        for i, item in enumerate(noticias):
            clasificacion = "Verdadero" if resultados["predictions"][i] == 1 else "Falso"
            probabilidades = resultados["probabilidades"][i]
            response_list.append({
                "titulo": item.get("Titulo", "Sin título"),
                "cuerpo": item.get("Descripcion", "Sin descripción"),
                "clasificacion": clasificacion,
                "ProbVerdadera": probabilidades[1],
                "ProbFalsa": probabilidades[0]
            })
    except pd.errors.ParserError:
        return jsonify({"error": "Error al leer el archivo CSV. Verifica el formato."}), 400
    except requests.exceptions.RequestException:
        return jsonify({"error": "No se pudo conectar con la API"}), 500

    return render_template('classify_batch.html', results=response_list)

@app.route('/retrain-submit', methods=["POST"])
@app.route('/reentrenar', methods=["POST"])
def retrain_submit():
    file = request.files.get('file')

    if not file:
        return jsonify({"error": "No se proporcionó ningún archivo"}), 400

    try:
        df = pd.read_csv(file, sep=";")

        df.rename(columns=lambda x: x.strip(), inplace=True)


        columnas_requeridas = {"ID", "Label", "Titulo", "Descripcion", "Fecha"}
        if not columnas_requeridas.issubset(df.columns):
            return jsonify({"error": "El archivo CSV no tiene las columnas requeridas"}), 400


        df["ID"] = df["ID"].astype(str)
        df["Label"] = df["Label"].astype(int)
        df["Fecha"] = df["Fecha"].astype(str)
        df["Titulo"] = df["Titulo"].astype(str)
        df["Descripcion"] = df["Descripcion"].astype(str)

   
        datos = df.to_dict(orient="records")


        response = requests.post(f"{API_URL}/retrain/", json=datos)
        response.raise_for_status()
        result = response.json()


        formatted_response = {
            "Train_F1": f"{result['Training Metrics']['F1']*100:.2f}%",
            "Train_Recall": f"{result['Training Metrics']['Recall']*100:.2f}%",
            "Train_Precision": f"{result['Training Metrics']['Precision']*100:.2f}%",
            "Train_Accuracy": f"{result['Training Metrics']['Accuracy']*100:.2f}%",
            "Val_F1": f"{result['Validation Metrics']['F1']*100:.2f}%",
            "Val_Recall": f"{result['Validation Metrics']['Recall']*100:.2f}%",
            "Val_Precision": f"{result['Validation Metrics']['Precision']*100:.2f}%",
            "Val_Accuracy": f"{result['Validation Metrics']['Accuracy']*100:.2f}%"
        }
    except pd.errors.ParserError:
        return jsonify({"error": "Error al leer el archivo CSV. Verifica el formato."}), 400
    except ValueError as e:
        return jsonify({"error": f"Error en los datos del CSV: {str(e)}"}), 400
    except requests.exceptions.RequestException:
        return jsonify({"error": "No se pudo conectar con la API"}), 500
    
    return render_template('retrain.html', results=formatted_response)

# ------------ Main ------------
if __name__ == '__main__':
    app.run(debug=True)
