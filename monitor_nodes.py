import aiohttp
import asyncio
import requests
import subprocess
import time

BASIC_PORT = 10001
IP = "152.53.13.105"
COUNT_NODES = 9  # Количество узлов
CHECK_INTERVAL = 60  # Интервал между проверками (в секундах)
MAX_CONNECTIONS = 10000  # Лимит соединений
URL = "https://rewards.autobotocean.com/api/node-check"

def GetToken():
    """Получаем токен с сайта."""
    response = requests.get("https://rewards.autobotocean.com/")
    lines = response.text.split("\n")
    for line in lines:
        if "var initialToken" in line:
            return line[line.index("'") + 1: -2]  # Извлекаем токен

XAT = GetToken()  # Получаем токен при запуске

HEADERS = {
    'Content-Type': 'application/json',
    'X-Access-Token': XAT,
}

async def send_request(session, http_port, p2p_port):
    """Отправляем запрос и обрабатываем ответ."""
    data = {
        "nodeIp": IP,
        "httpPort": http_port,
        "p2pPort": p2p_port,
    }
    try:
        async with session.post(URL, json=data) as response:
            status = response.status
            text = await response.json()
            node_running = text.get("nodeRunning", False)
            print(f"HTTP {http_port} | P2P {p2p_port} -> Status: {status}, Response: {text}")
            return node_running, http_port
    except Exception as ex:
        print(f"Error with {http_port}:{p2p_port} -> {ex}")
        return False, http_port  # Если ошибка, считаем ноду неактивной

async def check_nodes():
    """Проверяем все ноды и перезапускаем неактивные."""
    inactive_nodes = []

    async with aiohttp.ClientSession(headers=HEADERS) as session:
        tasks = [
            send_request(session, BASIC_PORT + 10 * i, BASIC_PORT + 1 + 10 * i)
            for i in range(COUNT_NODES)
        ]
        results = await asyncio.gather(*tasks)

    # Обрабатываем результаты проверки
    for node_running, port in results:
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

async def monitor_nodes():
    """Запускаем мониторинг нод с проверкой раз в минуту."""
    while True:
        print("\nЗапускаем проверку нод...")
        await check_nodes()
        print(f"Ждем {CHECK_INTERVAL} секунд до следующей проверки...\n")
        await asyncio.sleep(CHECK_INTERVAL)

def start_monitoring():
    """Запускаем мониторинг в бесконечном цикле."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(monitor_nodes())
    except KeyboardInterrupt:
        print("Завершение программы...")
    finally:
        loop.close()

if __name__ == "__main__":
    start_monitoring()
