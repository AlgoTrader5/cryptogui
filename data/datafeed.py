import os
import sys
import argparse
import json
import paramiko
import threading
import time
import zmq
import zmq.ssh


from multiprocessing import Process
from pandas import Timestamp
from queue import Queue, Empty
from zmq.utils.monitor import recv_monitor_message

from event import QuoteEvent, TradeEvent

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--addr", help='zmq subscriber')
    return parser.parse_args()

def get_time():
    return str(Timestamp(time.time(), unit='s'))

class DataFeed:
    def __init__(self, addr, event_engine=None, ctx=None):
        self.addr = addr
        self.event_engine = event_engine
        self.ctx = ctx if ctx else zmq.Context.instance()
        self.active = False
        self.connected = False
        self._connect_subcriber()
        self._thread = threading.Thread(target=self.run, daemon=True)
        
    def _connect_subcriber(self):
        print(f"DataFeed connect addr={self.addr}.")
        self.socket = self.ctx.socket(zmq.SUB)
        self.socket.setsockopt(zmq.SUBSCRIBE, b'')
        self.socket.bind(self.addr)
        time.sleep(0.3)


    #--------------------------- private functions --------------------------#
    def run(self):
        '''
        event types received: ticker, trades, book
        '''
        print("DataFeed running.")
        while self.active:
            data = None
            try:
                data = self.socket.recv_string()
                topic, data = data.split(" ", 1)
                event_type = topic.split("-")[1]
                data = json.loads(data)
                if event_type == 'book':
                    exch = topic.split("-")[0]
                    pair = "-".join(topic.split("-")[2:])
                    e = QuoteEvent(exch, pair, data)
                    self.event_engine.put(e)
                elif event_type == 'trades':
                    pass
                    # e = TradeEvent(data)
                    # self.event_engine.put(e)
                elif event_type == 'ticker':
                    pass
                elif event_type == 'funding':
                    pass
                else:
                    print(f"Could not determine event_type. Topic={topic}. Event type={event_type}. Data={data}")
            except zmq.error.Again:
                continue
            except Exception as e:
                print(f"EXECEPTION! {e}. Breaking out of loop. Topic={topic}. Data={data}.")
                break
            time.sleep(.001)
        
        self.active = False
        print("Done running DataFeed.")


    def start(self):
        self.active = True
        if not self._thread.isAlive():
            print("DataFeed start.")
            self._thread.start()
        else:
            print("DataFeed thread already alive???")

    def stop(self):
        # self.socket.unbind(self.addr)
        # self.socket.close()
        self.active = False
        
        if self._thread.isAlive():
            print("DataFeed join.")
            self._thread.join(timeout=2)

        if self._thread.isAlive():
            print("DataFeed join operation timed out!")
        


def main():
    args = get_args()
    sub = Subscriber(addr=args.addr)
    sub.start()
    try:
        while True:
            pass
    except KeyboardInterrupt as e:
        pass
    finally:
        sub.stop()

if __name__ == '__main__':
    main()
