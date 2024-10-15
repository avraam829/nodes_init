import requests
import subprocess
import time
import socket

BASIC_PORT = 10001
URL = "https://rewards.autobotocean.com/api/node-check"

def get_local_ip():
    """Получение IP-адреса текущего устройства."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        s.connect(('8.8.8.8', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def get_token():
    """Получаем токен с сайта."""
    response = requests.get("https://rewards.autobotocean.com/")
    lines = response.text.split("\n")
    for line in lines:
        if "var initialToken" in line:
            token = line[line.index("'") + 1: -2]  # Извлекаем токен
            print("Получен новый токен.")
            return token
    print("Не удалось получить токен.")
    return ""

def send_request(http_port, p2p_port):
    """Отправляем запрос и обрабатываем ответ."""
    data = {
        "nodeIp": IP,
        "httpPort": http_port,
        "p2pPort": p2p_port,
    }
    try:
        response = requests.post(URL, json=data, headers=HEADERS)
        status = response.status_code
        text = response.json()
        node_running = text.get("nodeRunning", False)
        print(f"HTTP {http_port} | P2P {p2p_port} -> Status: {status}, Response: {text}")
        return node_running, http_port
    except Exception as ex:
        print(f"Error with {http_port}:{p2p_port} -> {ex}")
        return False, http_port  # Если ошибка, считаем ноду неактивной

def check_nodes():
    """Проверяем все ноды и перезапускаем неактивные."""
    inactive_nodes = []

    for i in range(COUNT_NODES):
        http_port = BASIC_PORT + 10 * i
        p2p_port = BASIC_PORT + 1 + 10 * i
        node_running, port = send_request(http_port, p2p_port)

        if not node_running:
            container_name = f"nodes_{(port - BASIC_PORT) // 10 + 1}"
            inactive_nodes.append(container_name)

    if inactive_nodes:
        print(f"Неактивные ноды: {inactive_nodes}")
        restart_nodes(inactive_nodes)
    else:
        print("Все ноды активны.")

def restart_nodes(containers):
    """Перезапускаем указанные Docker-контейнеры."""
    for container in containers:
        try:
            print(f"Перезапускаем контейнер {container}...")
            subprocess.run(["docker", "restart", container], check=True)
        except subprocess.CalledProcessError as ex:
            print(f"Ошибка при перезапуске контейнера {container}: {ex}")

def start_monitoring():
    """Запускаем мониторинг нод в бесконечном цикле."""
    global XAT, HEADERS

    while True:
        print("\nЗапрашиваем новый токен...")
        XAT = get_token()  # Запрашиваем новый токен
        HEADERS = {
            'Content-Type': 'application/json',
            'X-Access-Token': XAT,
        }
        print("Запускаем проверку нод...")
        check_nodes()
        print(f"Ждем {CHECK_INTERVAL} секунд до следующей проверки...\n")
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    IP = get_local_ip()  # Получаем локальный IP

    # Запрашиваем количество нод и интервал проверки у пользователя
    COUNT_NODES = int(input("Введите количество нод: "))
    CHECK_INTERVAL = int(input("Введите интервал между проверками (в секундах): "))

    try:
        start_monitoring()
    except KeyboardInterrupt:
        print("Завершение программы...")
