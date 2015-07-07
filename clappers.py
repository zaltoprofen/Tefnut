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

class IFTTTClapper(object):
    _endpoint = 'https://maker.ifttt.com/trigger/{event}/with/key/{ifttt_key}'
    def __init__(self, ifttt_key):
        self._key = ifttt_key

    def clap(self, event, value1=None, value2=None, value3=None, clapping=urlopen):
        log.debug('clapping IFTTT: event: %s, values=(%s, %s, %s)',
                  event, value1, value2, value3)
        url = self._endpoint.format(event=event, ifttt_key=self._key)
        payload_obj = {}
        if value1 is not None:
            payload_obj['value1'] = value1
        if value2 is not None:
            payload_obj['value2'] = value2
        if value3 is not None:
            payload_obj['value3'] = value3
        payload = json.dumps(payload_obj)
        req = Request(url, payload, {'Content-Type': 'application/json'})
        return clapping(req).status == 200
