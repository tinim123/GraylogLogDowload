import base64
import datetime
import requests
import json


def login(host: str, username: str, password: str) -> str:
    headers = {
        'Host': host,
        'Content-Length': '73',
        'Accept': 'application/json',
        'X-Requested-With': 'XMLHttpRequest',
        'X-Requested-By': 'XMLHttpRequest',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36',
        'Origin': 'http://{0}'.format(host),
        'Referer': 'http://{0}/'.format(host),
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'close',
    }
    json_data = {
        'username': username,
        'password': password,
        'host': host,
    }
    response = requests.post('http://{0}/api/system/sessions'.format(host), headers=headers, json=json_data, verify=False)
    if response.status_code != 200:
        raise Exception("Kullanici girisi yapilamadi")

    result = response.json()
    message_bytes = str("{0}:session".format(result["session_id"])).encode('ascii')
    base64_bytes = base64.b64encode(message_bytes)
    return base64_bytes.decode('ascii')

def create_export_job(host: str, auth: str) -> str:
    url = "http://{0}/api/views/export/6253f748098b25c1a3eb2ab9/9c15e050-dbcc-4306-9e9e-e140d5acdc17".format(host)
    payload = json.dumps({
        "execution_state": {
            "parameter_bindings": {}
        },
        "fields_in_order": [
            "timestamp",
            "source",
            "message"
        ]
    })
    headers = {
        'Authorization': 'Basic {0}'.format(auth),
        'Accept': 'text/csv',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-US,en;q=0.9,de;q=0.8,tr;q=0.7',
        'Connection': 'keep-alive',
        'Content-Length': '96',
        'Content-Type': 'application/json',
        'Host': host,
        'Origin': 'http://{0}'.format(host),
        'Referer': 'http://{0}/search'.format(host),
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36',
        'X-Requested-By': 'XMLHttpRequest',
        'X-Requested-With': 'XMLHttpRequest'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code != 200:
        raise Exception("Is olusturulamadi")

    return response.text

def download(host: str, auth: str, job_id: str) -> str:
    url = "http://{0}/api/views/search/messages/job/{1}/All-Messages-search-result.csv".format(host, job_id)
    headers = {
        'Host': host,
        'Authorization': 'Basic {0}'.format(auth),
        'Referer': 'http://{0}/search'.format(host),
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'close',
    }
    local_filename = "All-Messages-search-result-{0}.csv".format(datetime.datetime.now().strftime("%d_%m_%Y_%H_%M_%S"))
    with requests.get(url, headers=headers, verify=False, stream=True, timeout=999999) as r:
        if r.status_code != 200:
            raise Exception("Indirme islemi hatali")

        r.raise_for_status()
        with open("/root/Signed_Logs/dump/"+local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return local_filename


if __name__ == '__main__':
    host = "<IP Address for Graylog>"
    username = 'admin'
    password = '<Password>'

    print(datetime.datetime.now(), "Islem basladi")
    auth = login(host, username, password)
    job_id = create_export_job(host, auth)
    file_name = download(host, auth, job_id)
    print(datetime.datetime.now(), "Islem tamamlandi", file_name)
