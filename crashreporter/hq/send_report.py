__author__ = 'calvin'

import requests


def upload_to_hq(fileobject):
    files = {"files": fileobject}
    r = requests.post("http://127.0.0.1:5000/upload", files=files)
    return r

if __name__ == '__main__':

    f = open('./crashreport117.html', 'rb')
    r = upload_to_hq(f)
    aqsd=3