import requests
base = 'http://127.0.0.1:8000'
print('health', requests.get(base + '/health', timeout=10).status_code)
resp = requests.post(base + '/user/login', data={'username': 'admin', 'password': '123456'}, timeout=10)
print('login_status', resp.status_code)
print(resp.text)
