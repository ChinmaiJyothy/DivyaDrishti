import json, urllib.request, time, sys
body = json.dumps({'email':'admin@example.com','password':'TestPass123!'}).encode()
req = urllib.request.Request('http://localhost:8000/api/v1/auth/login', data=body, headers={'Content-Type':'application/json'}, method='POST')
token = json.loads(urllib.request.urlopen(req, timeout=10).read())['access_token']
req2 = urllib.request.Request('http://localhost:8000/api/v1/conversations', data=json.dumps({'title':'test','domain':'career'}).encode(), headers={'Content-Type':'application/json','Authorization':'Bearer '+token}, method='POST')
conv = json.loads(urllib.request.urlopen(req2, timeout=10).read())
url = 'http://localhost:8000/api/v1/chat/' + str(conv['id'])
req3 = urllib.request.Request(url, data=json.dumps({'content':'What are my career prospects?','language':'en'}).encode(), headers={'Content-Type':'application/json','Authorization':'Bearer '+token,'Accept':'text/event-stream'}, method='POST')
start = time.time()
r = urllib.request.urlopen(req3, timeout=30)
out = open('verification/sse_dump.txt','wb')
while True:
    chunk = r.read(1024)
    if not chunk:
        break
    out.write(chunk)
    if b'"event": "done"' in chunk or b'event: done' in chunk:
        break
    if time.time() - start > 15:
        break
out.close()
print('saved', time.time()-start, 'bytes', out.tell())
