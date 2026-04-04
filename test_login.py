import urllib.request
import urllib.parse
import json

url = 'http://127.0.0.1:8069/web/session/authenticate'
headers = {'Content-Type': 'application/json'}
data = {
    'jsonrpc': '2.0',
    'method': 'call',
    'params': {
        'db': 'aadit',
        'login': 'f20240248@dubai.bits-pilani.ac.in',
        'password': 'admin'
    }
}
req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers)
try:
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode('utf-8'))
        if 'error' in result:
             print("LOGIN FAILED:", result['error'])
        elif result.get('result', {}).get('uid'):
             print("LOGIN SUCCESSFUL! User ID:", result['result']['uid'])
        else:
             print("RESPONSE:", result)
except Exception as e:
    print("Request failed:", e)
