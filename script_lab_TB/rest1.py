from time import sleep
import requests
import json
import random
tb_protocol = "http"
tb_host = "localhost"
tb_port = "8080"
device_token = "IcWrmKiKl3KNgRlSDode" # device's token
url = f"{tb_protocol}://{tb_host}:{tb_port}/api/v1/{device_token}/telemetry"
header = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
msg = { "temperature": 0 }

try:
 while True:
    msg["temperature"] = random.randint(0,100)
    data_json = json.dumps(msg)
    http_response = requests.post(url=url,data=data_json,headers=header)
    if http_response.status_code == 200:
        print(f"send data to ThingsBoard: {data_json}")
        sleep(10)
    else:
        print("ERRORE HTTP")
except requests.exceptions.ConnectionError as e:
 print("Request Exception", e)
except KeyboardInterrupt:
 pass
except Exception as e:
 print("General Exception: ", e)
