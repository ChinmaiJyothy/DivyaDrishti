import urllib.request, ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
try:
    r = urllib.request.urlopen('http://localhost:3000/charts', context=ctx, timeout=30)
    print('status', r.status)
    print(r.read(4000).decode('utf-8', 'replace'))
except Exception as e:
    print('fetch error', e)
