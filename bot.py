import requests
import sys
import yaml
import time
import itertools
import json

# Baca file yaml untuk mendapatkan token, channel_id dan delay
with open('config.yaml') as f:
    config = yaml.safe_load(f)

TOKEN = config['token']
CHANNEL_ID = config['channel_id']
SEND_DELAY = config['send_delay']
DELETE_DELAY = config['delete_delay']

# Baca file teks untuk mendapatkan pesan
with open('chat.txt') as f:
    lines = f.readlines()

# Buat iterator yang berulang
lines_cycle = itertools.cycle(lines)

# URL untuk mengirim pesan
url = f"https://discord.com/api/v9/channels/{CHANNEL_ID}/messages"

# Header untuk permintaan
headers = {
    "Authorization": TOKEN,
    "Content-Type": "application/json"
}

# Mendapatkan informasi pengguna
user_response = requests.get("https://discord.com/api/v9/users/@me", headers=headers)
username = user_response.json()['username']

while True:
    # Pilih pesan berikutnya dalam siklus
    message = next(lines_cycle)

    # Data untuk permintaan
    data = {
        "content": message
    }

    # Kirim pesan
    response = requests.post(url, headers=headers, json=data)

    # Jika ada kesalahan, cetak dan keluar dari loop
    if response.status_code != 200:
        print(f"Error: {response.status_code}, {response.text}")
        
        # Jika error adalah rate limit, tunggu sebelum mencoba lagi
        if response.status_code == 429:
            retry_after = json.loads(response.text)['retry_after']
            print(f"Rate limit hit. Waiting for {retry_after} seconds.")
            time.sleep(retry_after)
            continue

        sys.exit(1)

    # Cetak respon status
    print(f"Pesan '{message.strip()}' berhasil dikirim oleh {username}.")

    # Tunggu selama delay pengiriman sebelum menghapus pesan
    time.sleep(SEND_DELAY)

    # Dapatkan ID pesan
    message_id = response.json()['id']

    # URL untuk menghapus pesan
    delete_url = f"https://discord.com/api/v9/channels/{CHANNEL_ID}/messages/{message_id}"

    # Hapus pesan
    delete_response = requests.delete(delete_url, headers=headers)

    # Jika ada kesalahan, cetak dan keluar dari loop
    while delete_response.status_code != 204:
        print(f"Error: {delete_response.status_code}, {delete_response.text}")
        
        # Jika error adalah rate limit, tunggu sebelum mencoba lagi
        if delete_response.status_code == 429:
            retry_after = json.loads(delete_response.text)['retry_after']
            print(f"Rate limit hit. Waiting for {retry_after} seconds.")
            time.sleep(retry_after)
            # Coba hapus pesan lagi
            delete_response = requests.delete(delete_url, headers=headers)
        else:
            sys.exit(1)

    # Cetak respon status
    print(f"Pesan '{message.strip()}' berhasil dihapus oleh {username}.")

    # Tunggu selama delay penghapusan sebelum mengirim pesan berikutnya
    time.sleep(DELETE_DELAY)