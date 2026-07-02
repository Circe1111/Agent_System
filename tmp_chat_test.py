import urllib.request
import json

print('START')

req = urllib.request.Request(
    'http://127.0.0.1:8000/api/v1/chat/stream',
    method='OPTIONS'
)
req.add_header('Origin', 'http://localhost:5173')
req.add_header('Access-Control-Request-Method', 'POST')
req.add_header('Access-Control-Request-Headers', 'content-type,authorization')
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        print('OPTIONS', resp.status)
        print(resp.getheaders())
        print(resp.read().decode('utf-8', 'ignore'))
except Exception as e:
    print('OPTIONS ERROR', type(e).__name__, e)

print('NOW POST')
data = json.dumps({'user_content': 'test message', 'session_id': 'test-session'}).encode('utf-8')
req = urllib.request.Request(
    'http://127.0.0.1:8000/api/v1/chat/stream',
    data=data,
    headers={'Content-Type': 'application/json'},
    method='POST'
)
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        print('POST', resp.status)
        print(resp.getheader('content-type'))
        print(resp.read(200).decode('utf-8', 'ignore'))
except Exception as e:
    print('POST ERROR', type(e).__name__, e)
