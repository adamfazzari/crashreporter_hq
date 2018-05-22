import json
import geohash
import requests
from sqlalchemy import Column, Integer, String

from .. import db, app

GEOHASH_PRECISION = 5

class UploadRequest(db.Model):
    __tablename__ = 'upload_requests'
    geohash = Column(String(5), primary_key=True)
    crash_reports = Column(Integer, default=0, unique=False)
    usage_stats = Column(Integer, default=0, unique=False)

    def __init__(self, geohash):
        self.geohash = geohash
        self.usage_stats = 0
        self.crash_reports = 0

    @staticmethod
    def convert_ip_to_location(ip_address):
        api_key = app.config.get("IP_STACK_API_KEY", None)
        if api_key is None:
            return None
        r = requests.get("http://api.ipstack.com/{}?access_key={}".format(ip_address, api_key))
        if r.status_code == 200:
            j = json.loads(r.content)
            lat, lon = j.get('latitude', None), j.get('longitude', None)
            if lat is None or lon is None:
                return None
            try:
                return geohash.encode(lat, lon)[:GEOHASH_PRECISION]
            except Exception as e:
                return None
        return None

    @classmethod
    def from_ip_address(cls, ip_address):
        geohash = UploadRequest.convert_ip_to_location(ip_address)
        if geohash is not None:
            return cls(geohash)
        return None

    @staticmethod
    def get_by_geohash(geohash):
        q = UploadRequest.query.filter(UploadRequest.geohash == geohash[:GEOHASH_PRECISION])
        ret = q.first()
        return ret

    @staticmethod
    def get_by_ip_address(ip_address):
        geohash = UploadRequest.convert_ip_to_location(ip_address)
        if geohash is None:
            return None
        return UploadRequest.get_by_geohash(geohash)
