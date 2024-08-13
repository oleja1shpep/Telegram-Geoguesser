import requests
import json

def send_data_to_backend(data):
    url = 'https://functions.yandexcloud.net/d4e3l97hmqij0jekpe3t'
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(data))
    
    # Проверка статуса ответа
    if response.status_code == 200:
        response_data = response.json()
        print(response_data)
    else:
        print(f'Error: {response.status_code}\n {response.text}')

# Пример вызова функции для отправки данных
data = {
        "method": "get",
        "key": "key"
    }

send_data_to_backend(data)

