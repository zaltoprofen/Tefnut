from clapper import ApiClapper, Coordinate
from datetime import timedelta
from chrono import Chrono
import json
import logging

log = logging.getLogger(__name__)

class Tefnut(object):
    def __init__(self, api_clapper, venues):
        self.handlers = []
        self.api_clapper = api_clapper
        self.venues = venues
        self.prev = dict(map(lambda x:(x[0], None), venues))

    def add_handler(self, handler):
        self.handlers.append(handler)

    def fire(self, *args, **kwargs):
        for h in self.handlers:
            h(*args, **kwargs)

    def trigger(self):
        for n, c in self.venues:
            cw = self.api_clapper.request(c)
            if self.prev[n] is None:
                self.prev[n] = cw
            if cw['date'] <= self.prev[n]['date']:
                continue
            if cw['rainfall'] != 0.0 and self.prev[n]['rainfall'] == 0.0:
                self.fire(name=n, weather=cw)
            if cw['rainfall'] == 0.0 and self.prev[n]['rainfall'] != 0.0:
                self.fire(name=n, weather=cw)
            self.prev[n] = cw

def load_handler(module_name, class_name, cons_args=[], cons_kwargs={}):
    import importlib
    module = importlib.import_module(module_name)
    klazz = module.__getattribute__(class_name)
    return klazz(*cons_args, **cons_kwargs)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    with open('config.json') as fp:
        conf = json.load(fp)
    appid = conf['appid']
    def map_to_venue(obj):
        return obj['name'], Coordinate(**obj['coordinate'])
    venues = list(map(map_to_venue, conf['venues']))
    ac = ApiClapper(appid)
    t = Tefnut(ac, venues)
    for h in conf['handlers']:
        hdlr = load_handler(**h)
        t.add_handler(hdlr)
    ch = Chrono(t.trigger, timedelta(minutes=5), first_fire=True)
