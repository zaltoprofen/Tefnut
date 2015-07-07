from urllib.request import urlopen, Request
from urllib.parse import urlencode
from datetime import datetime
import json
import logging

log = logging.getLogger(__name__)

class Coordinate(object):
    def __init__(self, longitude, latitude):
        self.longitude = longitude
        self.latitude = latitude

    def __str__(self):
        return '%f,%f' % (self.longitude, self.latitude)

class ApiClapper(object):
    _endpoint = 'http://weather.olp.yahooapis.jp/v1/place'
    def __init__(self, appid):
        self.appid = appid

    def request(self, coordinate, clap_http=urlopen):
        assert(isinstance(coordinate, Coordinate))
        log.debug('clapping Weather API: %s', str(coordinate))
        params = {
                'appid': self.appid,
                'coordinates': str(coordinate),
                'output': 'json',
                'interval': '5'}
        url = '%s?%s' % (self._endpoint, urlencode(params))
        with clap_http(url) as res:
            return self.get_observation(res.readall().decode('utf-8'))

    def get_observation(self, response):
        dat = json.loads(response)
        try:
            val = dat['Feature'][0]['Property']['WeatherList']['Weather'][0]
            log.debug('parsed: %s', val)
            return {'date': datetime.strptime(val['Date'], '%Y%m%d%H%M'),
                    'rainfall': val['Rainfall']}
        except KeyError:
            return None
