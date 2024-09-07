import json
import logging
from database import MongoDB
from dotenv import load_dotenv

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('TEST')
logger.setLevel(logging.DEBUG)

database = MongoDB()

load_dotenv()

MODES = ['msk', 'spb', 'rus', 'usa', 'wrld', 'easy']

def handler(event, context):
    logger.info(event)
    if event['httpMethod'] == 'OPTIONS':
        return {
            'statusCode': 204,
            'headers': {
                "Allow": "GET, POST, OPTIONS, PUT, DELETE",
                "Content-Length": "0",
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "https://geoguessr-site.website.yandexcloud.net",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS, PUT, DELETE",
                "Access-Control-Allow-Headers": "Content-Type, Authorization"
            },
            'body': None
        }
    # Обработка входящих данных
    data = json.loads(event['body'])

    if 'method' not in data or data['method'] not in ['end_solo_game', 'get_test', 'set_test']:
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
            },
            'body': "Wrong method"
        }
    if data['method'] == 'end_solo_game':
        if any(list(map(lambda field: field not in data, ['tele_id', 'seed', 'mode', 'fields']))):
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                },
                'body': "Request doesn't have some fields"
            }
        elif any(list(map(lambda field: field not in data['fields'], ["x_correct", "y_correct", "x_player", "y_player", "color_scheme"]))):
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                },
                'body': "Request doesn't have some fields in data['fields']"
            }
        if data['mode'] not in MODES:
            response_data = {"status": False, "message": f"Wrong mode: {data['mode']} doesn't exist"}
        elif not database.is_active_session(data['tele_id'], data['mode']):
            response_data = {"status": False, "message": f"Game finished or user does not exists."}
        else:
            database.end_solo_game(data)
            # database.start_solo_game(data['tele_id'], data['mode'])
            response_data = {"status": True, "message": f"OK"}
    elif data['method'] == 'get_test':
        get_data = database.get_test(data['tele_id'])
        response_data = {"message": "ok_get", "out": json.dumps(get_data)}
    elif data['method'] == 'set_test':
        database.set_test(data['tele_id'], data['mode'], data['seed_msk'], data['track_changes'])
        response_data = {"message": "ok_set", "input": data}
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
        },
        'body': json.dumps(response_data)
    }
