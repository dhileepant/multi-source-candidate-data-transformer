import urllib.request, glob, json, os

boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
body = []

for p in glob.glob('inputs/*.pdf') + glob.glob('inputs/*.csv'):
    body.extend([
        f'--{boundary}'.encode('utf-8'),
        f'Content-Disposition: form-data; name=\"files\"; filename=\"{os.path.basename(p)}\"'.encode('utf-8'),
        b'Content-Type: application/octet-stream',
        b'',
        open(p, 'rb').read()
    ])

body.extend([
    f'--{boundary}'.encode('utf-8'),
    b'Content-Disposition: form-data; name=\"github_url\"',
    b'',
    b'https://github.com/dhileepant'
])

body.append(f'--{boundary}--'.encode('utf-8'))
body.append(b'')

data = b'\r\n'.join(body)
req = urllib.request.Request('http://127.0.0.1:5000/process', data=data, headers={
    'Content-Type': f'multipart/form-data; boundary={boundary}'
})
try:
    with urllib.request.urlopen(req) as response:
        res = json.loads(response.read().decode())
        print(res['stats'])
        for p in res['profiles']:
            if 'dhileepan' in str(p).lower():
                print(p.get('full_name'), '|', p.get('primary_email'), '|', p.get('phone'))
except Exception as e:
    print('Error:', e)
