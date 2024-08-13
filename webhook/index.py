import json
from database import MongoDB
from dotenv import load_dotenv

database = MongoDB()

load_dotenv()

def handler(event, context):
    # Обработка входящих данных
    data = json.loads(event['body'])

    if 'method' not in data:
         return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
            },
            'body': "test text"
        }

    if data['method'] == 'set':
        database.set_test(data['key'], data['data'])
        response_data = {"message": "ok_set", "input": data}
    else:
        get_data = database.get_test(data['key'])
        response_data = {"message": "ok_get", "input": get_data}
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
        },
        'body': json.dumps(response_data)
    }