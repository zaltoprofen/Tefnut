from urllib.request import urlopen, Request
import json

class LogicomaTefnut(object):
    def __init__(self, endpoint):
        self._endpoint = endpoint

    def __call__(self, name, weather):
        txt = "begin raining at %s" if weather['rainfall'] != 0.0 \
                else "stop raining at %s"
        payload_obj = {
                "username": "Logicoma - Tefnut",
                "text": txt % name,
                "icon_emoji": ":logicoma:"}
        payload = json.dumps(payload_obj).encode('utf-8')
        r = Request(self._endpoint, payload, {'Content-Type': 'applicaion/json'})
        return urlopen(r).status == 200
