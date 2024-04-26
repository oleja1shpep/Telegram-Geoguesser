#!/usr/bin/env bash
set -eu

FUNCTION_ID=d4etua5b0mijijqgq8gs
FOLDER_ID=b1glcpkpn3f5vds58u09
SA_ID=ajeb525m5vdpts9m5mv3
DB_USER=mongo
DB_HOST=rc1b-wup2eco8flkg4voi.mdb.yandexcloud.net:27018
DB_NAME=users
URL_SITE=https://test-geoguessr.website.yandexcloud.net
NETWORK_ID=enp7bbt5mhb8gi39rtvs

PYTHONVER=3.11

zip function.zip requirements.txt
cd ./TelegramBot
zip -r ../function.zip index.py backend
cd ..

yc serverless function version create \
    --function-id $FUNCTION_ID \
    --runtime python${PYTHONVER/./} \
    --folder-id $FOLDER_ID \
    --entrypoint index.handler \
    --memory 256MB \
    --environment TOKEN=$TOKEN,TOKEN_STATIC=$TOKEN_STATIC,DB_USER=$DB_USER,DB_HOST=$DB_HOST,DB_PASS=$DB_PASS,DB_NAME=$DB_NAME,URL_SITE=$URL_SITE,YAGPT_APIKEY=$YAGPT_APIKEY \
    --execution-timeout 2m \
    --source-path function.zip \
    --service-account-id $SA_ID \
    --network-id $NETWORK_ID