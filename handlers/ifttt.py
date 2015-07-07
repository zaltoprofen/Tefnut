from urllib.request import urlopen, Request
from urllib.parse import urlencode
from datetime import datetime
import json
import logging

log = logging.getLogger(__name__)

def construct_clap_ifttt(ifttt_key):
    clapper = IFTTTClapper(ifttt_key)
    def clap_ifttt(name, weather):
        if weather['rainfall'] != 0:
            event = 'begin_raining'
        else:
            event = 'stop_raining'
        clapper.clap(event, name)
    return clap_ifttt

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
        req = Request(url, payload.encode('utf-8'), {'Content-Type': 'application/json'})
        return clapping(req).status == 200
