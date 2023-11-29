from bs4 import BeautifulSoup
from imapclient import IMAPClient
import requests
import imaplib
import email
import time
import json
import ssl
import re


with open('email_credentials.json', 'r') as file:
    email_credentials = json.load(file)

EMAIL = email_credentials['EMAIL']
PASSWORD = email_credentials['PASSWORD']
IMAP_SERVER = email_credentials['IMAP_SERVER']


transaction_groups = {'Списание': 'outcome',
                      'Зачисление': 'income',
                      'Перевод': 'transfer'}

with open('headers.json', 'r') as file:
    headers = json.load(file)

PARTNER_URL = 'https://api.fintablo.ru/v1/partner'
MONEYBAG_URL = 'https://api.fintablo.ru/v1/moneybag'
TRANSACTION_URL = 'https://api.fintablo.ru/v1/transaction'

partner_list = requests.get(PARTNER_URL, headers=headers).json()
accounts_list = requests.get(MONEYBAG_URL, headers=headers).json()


def get_text(bs_data, tag_name):
    tag = bs_data.find(tag_name)
    return tag.get_text() if tag else None


def find_account_id(iban):
    for item in accounts_list['items']:
        if item['number'] == iban:
            return item['id']
    print('Failed to calculate the id of the account for which the transaction took place.')
    return None


def find_or_create_partner(inn, name):
    partner_list = requests.get(PARTNER_URL, headers=headers).json()
    for item in partner_list['items']:
        if item['inn'] == inn:
            print('inn:', item['inn'])
            return item['id']
        if item['name'] == name:
            print('id:', item['id'])
            return item['id']

    if not name:
        return None

    if inn == "000000000":
        response = requests.post(PARTNER_URL, json={"name": name}, headers=headers).json()
        print("name: ", name)
        return response['items'][0]['id']

    new_partner = {
        "name": name,
        "inn": inn
    }
    response = requests.post(PARTNER_URL, json=new_partner, headers=headers).json()
    print("inn: ", inn)
    print("name: ", name)
    print(response)
    return response['items'][0]['id']


def extract_nds(details_content):
    match = re.search(r'НДС.*?(\d{1,2})\s?%', details_content)
    if match:
        return int(match.group(1))
    return None


def process_email(data):
    email_message = email.message_from_bytes(data[b'RFC822'])

    for part in email_message.walk():
        if part.get_content_maintype() == 'multipart':
            continue
        if not part.get('Content-Disposition'):
            continue

        decoded_content = part.get_payload(decode=True).decode(part.get_content_charset('UTF-8'), 'replace')
        bs_data = BeautifulSoup(decoded_content, "xml")

        account_iban = get_text(bs_data, 'bAccount')
        date = get_text(bs_data, 'Tdate')
        type_ = transaction_groups.get(get_text(bs_data, 'Ttype'))
        amount = get_text(bs_data, 'amount')
        agent_name = get_text(bs_data, 'pName')
        agent_inn_match = re.search(r'\d+', get_text(bs_data, 'pCode') or '')
        agent_inn = agent_inn_match[0] if agent_inn_match else ''
        details = get_text(bs_data, 'details')
        partaccount = get_text(bs_data, 'pAccount')

        if not agent_name:
            agent_name = 'Нет контрагента'
        if not agent_inn:
            agent_inn = 9999999999

        nds = extract_nds(details)

        print('<details>', details, '</details>')

        id_ac = find_account_id(account_iban)

        if not agent_inn:
            details += f'1_ИНН контрагента_{agent_inn}2_Название контрагента_{agent_name}3_Номер счета контрагента_{partaccount}'



        id_partn = find_or_create_partner(agent_inn, agent_name)

        transaction_data = {
            "value": amount,
            "moneybagId": id_ac,
            "group": type_,
            "description": details,
            "partnerId": id_partn,
            "date": date,
            "nds": nds
        }

        response = requests.post(TRANSACTION_URL, json=transaction_data, headers=headers).json()
        print(response)


def idle_and_wait_for_email():
    while True:
        with IMAPClient(IMAP_SERVER) as client:
            try:
                client.login(EMAIL, PASSWORD)
                client.select_folder('Inbox')
                print("Waiting for new emails...")

                client.idle()
                responses = client.idle_check(timeout=600)
                client.idle_done()

                for msg_id in client.search(['UNSEEN']):
                    data = client.fetch([msg_id], ['RFC822'])
                    process_email(data[msg_id])

            except (imaplib.IMAP4.abort, imaplib.IMAP4.error, ssl.SSLEOFError, ConnectionResetError) as e:
                print(f"Connection issue: {e}. Reconnecting...")
                try:
                    client.logout()
                except:
                    pass
                time.sleep(10)


if __name__ == '__main__':
    try:
        idle_and_wait_for_email()
    except KeyboardInterrupt:
        print("\nExiting...")
