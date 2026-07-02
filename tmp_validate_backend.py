import requests
import json

base = 'http://127.0.0.1:8000'
print('health', requests.get(base + '/health', timeout=5).status_code)

login_data = {'username': 'admin', 'password': 'admin'}
resp = requests.post(base + '/user/login', data=login_data, timeout=10)
print('login', resp.status_code, resp.text)
if resp.status_code != 200:
    raise SystemExit('login failed')

j = resp.json()
token = None
for key in ['token', 'access_token', 'accessToken']:
    if key in j.get('data', {}):
        token = j['data'][key]
        break
if token is None:
    token = j.get('token')
print('token', token[:20] + '...' if token else None)
headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}
body = {'user_content': '测试AI对话', 'session_id': 'verify-session'}
resp = requests.post(base + '/api/v1/chat/stream', json=body, headers=headers, stream=True, timeout=10)
print('stream status', resp.status_code, resp.headers.get('content-type'))
if resp.status_code != 200:
    print(resp.text)
else:
    count = 0
    for line in resp.iter_lines(decode_unicode=True):
        if line:
            print('LINE:', line)
            count += 1
        if count >= 6:
            break
