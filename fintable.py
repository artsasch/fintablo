import requests
import re
import imaplib
from email import message_from_bytes
from bs4 import BeautifulSoup
import time


# --------- Авторизовываемся в финтабло ---------
headers = {
    'Accept': 'application/json',
    'Authorization': 'Bearer t1.xygWDg6kKNBSuG5UYfTxcZJNXJaXUJmMzyTUq'
}

# Запрашиваем список контрагентов для уточнения уникальноного id счета
partner_list = requests.get('https://api.fintablo.ru/v1/partner',
                             headers=headers).json()

# Запрашиваем список счетов для уточнения уникальноного id счета
accounts_list = requests.get('https://api.fintablo.ru/v1/moneybag',
                             headers=headers).json()
# Создаем словарь для подставновки типа операция
d = {'Списание': "outcome", 'Зачисление': "income",'Перевод':"transfer"}

#Подключаемся к почтовому серверу
server = imaplib.IMAP4_SSL('imap.yandex.ru', 993)
server.login('pay@advaga.agency', 'zknwiwflwxkppeiy')

#Выбираем папку с письмами в нужном нам формате
server.select('ALFA')
# search = server.uid('search',None,'UNSEEN')

typ, data = server.search(None, 'UNSEEN')
# print(data)
for num in data[0].split():
    print('meow')
    typ, message_data = server.fetch(num, '(RFC822)')
    message = message_from_bytes(message_data[0][1])
    # print(data)
    # print(message)
    # print('Message %s\n%s\n' % (num, message_data[0][1]))
    for part in message.walk():
        if part.get_content_maintype() == 'multipart':
            continue
        if not part.get('Content-Disposition'):
            continue
        file_name = part.get_filename()
        bytes = part.get_payload(decode=True)
        charset = part.get_content_charset('UTF-8')
        chars = bytes.decode(charset, 'replace')
        print(chars)
        Bs_data = BeautifulSoup(chars, "xml")
        b_iban= Bs_data.find('bAccount')    #Номер счета, по которому узнаем id
        b_date = Bs_data.find('Tdate')  #Дата
        # b_time = Bs_data.find('Ttime')
        b_type = Bs_data.find('Ttype')  #тип операции на русском
        b_amount = Bs_data.find('amount')   #сумма операции
        b_partner = Bs_data.find('pName')   #имя контрагента
        b_code = Bs_data.find('pCode')   #инн контрагента
        b_details = Bs_data.find('details') #назначение платежа
        b_partaccount = Bs_data.find('pAccount') #счет контрагента

        # Преобразуем xml в text
        account_iban = b_iban.get_text() #Номер счета, по которому узнаем id
        date = b_date.get_text()    #Дата
        # time = b_time.get_text()
        type = d.get(b_type.get_text()) #тип операции на английском
        amount = b_amount.get_text()    #сумма операции
        agent_name = b_partner.get_text()    #имя контрагента
        match = re.search(r'\d+', b_code.get_text())
        agent_inn = match[0] if match else ''  # инн контрагента
        details = b_details.get_text() #назначение платежа
        partaccount = b_partaccount.get_text() #счет контрагента

        print(account_iban,date,type,amount,agent_name,agent_inn,details)

        # вычисляем id счета, по которой прошла операция
        for index in range(len(accounts_list['items'])):
            gid_counter = accounts_list['items'][index]
            if gid_counter['number'] == account_iban:
                id_ac = gid_counter['id']
                break
        else:
                print('ERROR')
        print(id_ac)

        # вычисляем id контрагента
        if agent_inn == '':
            id_partn = ''
            details = b_details.get_text() + '1_ИНН контрагента_' + agent_inn + '2_Название контрагента_' + agent_name + '3_Номер счета контрагента_' + partaccount
        else:
            for index in range(len(partner_list['items'])):
                gid_counter = partner_list['items'][index]
                if gid_counter['inn'] == agent_inn:
                    id_partn = gid_counter['id']
                    break
            else:
                if agent_name == '':
                    details = b_details.get_text() + '1_ИНН контрагента_' + agent_inn + '2_Название контрагента_' + agent_name + '3_Номер счета контрагента_' + partaccount
                    id_partn = ''
                else:
                    new_partner = {
                        "name": agent_name,
                        "inn": agent_inn}
                    create_partner = requests.post('https://api.fintablo.ru/v1/partner', json=new_partner, headers=headers).json()
                    print(create_partner)
                    id_partn = create_partner['items'][0]['id']
                    time.sleep(5)

        print(id_partn)

        value = amount
        moneybagId = id_ac
        group = type
        date = date
        description = details
        partnerId = id_partn

        # data to be sent to api
        data = {
            "value": value,
            "moneybagId": moneybagId,
            "group": type,
            "description": description,
            "partnerId": partnerId,
            "date": date}

        postrequest = requests.post('https://api.fintablo.ru/v1/transaction', json=data, headers=headers).json()
        print(postrequest)