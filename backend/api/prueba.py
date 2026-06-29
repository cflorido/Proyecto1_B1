import requests


API_URL = "http://127.0.0.1:8000/predict/"


data = {
    "Titulo": "Nuevo escándalo político en el gobierno",
    "Descripcion": "El presidente fue acusado de corrupción en un reciente informe.",
    "Fecha": "2025-03-27"
}


response = requests.post(API_URL, json=data)


print("Código de estado:", response.status_code)
print("Respuesta JSON:", response.json())
