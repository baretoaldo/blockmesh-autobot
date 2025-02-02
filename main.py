import requests
import time
import os
import threading
import random
from datetime import datetime
from colorama import init, Fore, Style

init(autoreset=True)

# Banner
def print_banner():
    banner = f"""
{Fore.CYAN}{Style.BRIGHT}╔══════════════════════════════════════════════╗
║          BlockMesh Network AutoBot           ║
║     Github: https://github.com/IM-Hanzou     ║
║      Welcome and do with your own risk!      ║
╚══════════════════════════════════════════════╝
"""
    print(banner)

# Fungsi untuk memformat proxy dari IP:PORT:USER:PASS ke HTTP proxy
def format_proxy(proxy_string):
    parts = proxy_string.split(":")
    
    if len(parts) == 4:  # Format IP:PORT:USER:PASS
        ip, port, user, password = parts
        proxy_dict = {
            "http": f"http://{user}:{password}@{ip}:{port}",
            "https": f"http://{user}:{password}@{ip}:{port}"
        }
    elif len(parts) == 2:  # Format IP:PORT tanpa autentikasi
        ip, port = parts
        proxy_dict = {
            "http": f"http://{ip}:{port}",
            "https": f"http://{ip}:{port}"
        }
    else:
        print(f"{Fore.RED}Invalid proxy format: {proxy_string}")
        return None, None
    
    return proxy_dict, ip

# Fungsi untuk mengambil informasi IP dari proxy
def get_ip_info(ip_address):
    try:
        response = requests.get(f"https://ipwhois.app/json/{ip_address}")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as err:
        print(f"{Fore.RED}Failed to get IP info: {err}")
        return None

# Fungsi untuk login ke API dengan proxy
def authenticate(proxy, email, password):
    proxy_config, ip_address = format_proxy(proxy)
    
    if proxy_config is None:
        print(f"{Fore.RED}Skipping invalid proxy: {proxy}")
        return None, None
    
    login_data = {"email": email, "password": password}
    
    try:
        response = requests.post(
            "https://api.blockmesh.xyz/api/get_token",
            json=login_data,
            headers={"content-type": "application/json"},
            proxies=proxy_config
        )
        response.raise_for_status()
        auth_data = response.json()
        api_token = auth_data.get("api_token")
        
        print(f"{Fore.GREEN}[{datetime.now().strftime('%H:%M:%S')}] Login successful | {ip_address}")
        return api_token, ip_address
    except requests.RequestException as err:
        print(f"{Fore.RED}[{datetime.now().strftime('%H:%M:%S')}] Login failed | {ip_address}: {err}")
        return None, None

# Fungsi untuk mengirim uptime report
def send_uptime_report(api_token, ip_addr, proxy):
    proxy_config, _ = format_proxy(proxy)
    if proxy_config is None:
        return
    
    formatted_url = f"https://app.blockmesh.xyz/api/report_uptime?email={email_input}&api_token={api_token}&ip={ip_addr}"
    
    try:
        response = requests.post(formatted_url, proxies=proxy_config)
        response.raise_for_status()
        print(f"{Fore.GREEN}[{datetime.now().strftime('%H:%M:%S')}] PING successful | {ip_addr}")
    except requests.RequestException as err:
        print(f"{Fore.RED}[{datetime.now().strftime('%H:%M:%S')}] Failed to PING | {ip_addr}: {err}")

# Fungsi utama yang menjalankan proses proxy
def process_proxy(proxy):
    first_run = True
    while True:
        if first_run:
            api_token, ip_address = authenticate(proxy, email_input, password_input)
            first_run = False
        else:
            api_token, ip_address = authenticate(proxy, email_input, password_input)

        if api_token:
            proxy_config, _ = format_proxy(proxy)
            ip_info = get_ip_info(ip_address)
            
            time.sleep(random.randint(60, 120))  # Tunggu sebelum submit
            
            send_uptime_report(api_token, ip_address, proxy)
            time.sleep(random.randint(900, 1200))  # Delay antar laporan uptime

        time.sleep(10)

# Menampilkan banner
print_banner()

# Input email dan password pengguna
email_input = input(f"{Fore.LIGHTBLUE_EX}Enter Email: {Style.RESET_ALL}")
password_input = input(f"{Fore.LIGHTBLUE_EX}Enter Password: {Style.RESET_ALL}")

# Memuat daftar proxy dari file
proxy_list_path = "proxies.txt"
proxies_list = []

if os.path.exists(proxy_list_path):
    with open(proxy_list_path, "r") as file:
        proxies_list = file.read().splitlines()
        print(f"{Fore.GREEN}[✓] Loaded {len(proxies_list)} proxies from proxies.txt")
else:
    print(f"{Fore.RED}[×] proxies.txt not found!")
    exit()

# Fungsi utama
def main():
    print(f"\n{Style.BRIGHT}Starting ...")
    threads = []
    for proxy in proxies_list:
        thread = threading.Thread(target=process_proxy, args=(proxy,))
        thread.daemon = True
        threads.append(thread)
        thread.start()
        time.sleep(1)
    
    print(f"{Fore.GREEN}[{datetime.now().strftime('%H:%M:%S')}] [✓] DONE! Delay before next cycle. Not Stuck! Just wait and relax...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Stopping ...")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"{Fore.RED}An error occurred: {str(e)}")
