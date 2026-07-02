import requests
base = 'http://127.0.0.1:8000'
resp = requests.post(base + '/user/login', data={'username': 'admin', 'password': '123456'}, timeout=10)
token = resp.json()['data']['token']
headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
body = {'user_content': '请直接回复：AI已恢复', 'session_id': 'verify-session'}
stream = requests.post(base + '/api/v1/chat/stream', headers=headers, json=body, stream=True, timeout=60)
print('stream_status', stream.status_code)
print('content_type', stream.headers.get('content-type'))
for line in stream.iter_lines(decode_unicode=True):
    if line:
        print(line)
