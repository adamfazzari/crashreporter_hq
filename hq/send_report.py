__author__ = 'calvin'

import requests

files = {"files": open('./crashreport117.html', 'rb')}
r = requests.post("http://127.0.0.1:5000/upload", files=files)
print r.text