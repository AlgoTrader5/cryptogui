from queue import Queue, Empty
from threading import Thread
from collections import defaultdict

class LiveEventEngine(object):
    def __init__(self):
        self._active = False
        self._queue = Queue()
        self._thread = Thread(target=self._run)
        self._handlers = defaultdict(list)

    def _run(self):
        while self._active == True:
            try:
                event = self._queue.get(block=True, timeout=0.5)
                # call event handlers
                if event.event_type in self._handlers:
                    [handler(event) for handler in self._handlers[event.event_type]]
            except Empty:
                pass
            except Exception as e:
                print("Error {0}".format(str(e.args[0])).encode("utf-8"))

    def start(self, timer=True):
        self._active = True
        self._thread.start()

    def stop(self):
        self._active = False
        self._thread.join()

    def put(self, event):
        """ put event in the queue; call from outside """
        self._queue.put(event, block=True, timeout=None)

    def register_handler(self, type_, handler):
        handlerList = self._handlers[type_]
        if handler not in handlerList:
            handlerList.append(handler)

    def unregister_handler(self, type_, handler):
        handlerList = self._handlers[type_]
        if handler in handlerList:
            handlerList.remove(handler)
        if not handlerList:
            del self._handlers[type_]

