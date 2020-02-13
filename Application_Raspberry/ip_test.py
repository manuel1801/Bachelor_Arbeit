import requests
from time import sleep

while True:

    print(requests.get('https://api.ipify.org').text)
    sleep(1)
