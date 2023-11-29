import requests
import json


with open('header.json', 'r') as file:
    headers = json.load(file)

response = requests.get('https://api.fintablo.ru/v1/moneybag', headers=headers).json()
print(response)
