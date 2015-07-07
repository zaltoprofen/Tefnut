from datetime import datetime, timedelta
import time
from threading import Thread, Event
import logging

log = logging.getLogger(__name__)

class Chrono(object):
    def __init__(self, handler, interval, max_tick=timedelta(seconds=60), first_fire=False, daemon=False, fork=False):
        if not isinstance(interval, timedelta):
            raise TypeError()
        self._interval = interval
        if first_fire:
            self._next_fire = datetime.now()
        else:
            self._next_fire = datetime.now() + interval
        self._max_tick = max_tick
        self._handler = handler
        self._stop = Event()
        self._fork = fork
        self._thread = Thread(target=self._tick)
        self._thread.setDaemon(daemon)
        self._thread.start()
        log.debug('started chrono: %s interval: %s', self, interval)

    def _tick(self):
        while not self._stop.is_set():
            log.debug('ticking chrono: %s', self)
            n = datetime.now()
            w = min(self._max_tick, self._next_fire - n)
            if w <= timedelta():
                log.debug('firing chrono: %s', self)
                if self._fork:
                    Thread(target=self._handler()).start()
                else:
                    self._handler()
                self._next_fire = n + self._interval
            else:
                log.debug('waiting %s chrono: %s', w, self)
                time.sleep(w.total_seconds())

    def stop(self):
        log.debug('stopping chrono: %s', self)
        self._stop.set()
