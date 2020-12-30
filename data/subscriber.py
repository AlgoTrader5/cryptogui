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

class Subscriber:
    def __init__(self, addr, ui_engine=None, ctx=None):
        self.addr        = addr
        self.ui_engine   = ui_engine
        self.remote_addr = f"{USERNAME}@{HOST}:{PORT}"
        self.ctx         = ctx if ctx else zmq.Context.instance()
        self.active      = False
        self.connected   = False
        self._connect_subcriber()
        self._thread     = threading.Thread(target=self.run, daemon=True)
        
    def _connect_subcriber(self):
        print(f"Subscriber connect addr={self.sub_addr}\nRemote addr={self.remote_addr}")
        self.socket = self.ctx.socket(zmq.SUB)
        self.socket.setsockopt(zmq.SUBSCRIBE, b'')
        monitor = self.socket.get_monitor_socket()
        zmq.ssh.tunnel_connection(self.socket, self.addr, self.remote_addr, keyfile=KEY_FILE, paramiko=True)
        retries = 0
        while retries < 10:
            status = recv_monitor_message(monitor)
            retries += 1
            if status['event'] == zmq.EVENT_HANDSHAKE_SUCCEEDED:
                print("zmq.EVENT_HANDSHAKE_SUCCEEDED")
                return
            elif status['event'] == zmq.EVENT_CONNECTED:
                print("zmq.EVENT_CONNECTED")
            elif status['event'] == zmq.EVENT_CONNECT_DELAYED:
                print("zmq.EVENT_CONNECT_DELAYED")
            elif status['event'] == zmq.EVENT_CONNECT_RETRIED:
                print("zmq.EVENT_CONNECT_RETRIED")
            elif status['event'] == zmq.EVENT_LISTENING:
                print("zmq.EVENT_LISTENING")
            elif status['event'] == zmq.EVENT_BIND_FAILED:
                print("zmq.EVENT_BIND_FAILED")
            elif status['event'] == zmq.EVENT_ACCEPTED:
                print("zmq.EVENT_ACCEPTED ")
            elif status['event'] == zmq.EVENT_ACCEPT_FAILED:
                print("zmq.EVENT_ACCEPT_FAILED")
            elif status['event'] == zmq.EVENT_CLOSED:
                print("zmq.EVENT_CLOSED")
            elif status['event'] == zmq.EVENT_CLOSE_FAILED:
                print("zmq.EVENT_CLOSE_FAILED")
            elif status['event'] == zmq.EVENT_DISCONNECTED:
                print("zmq.EVENT_DISCONNECTED")
            elif status['event'] == zmq.EVENT_MONITOR_STOPPED:
                print("zmq.EVENT_MONITOR_STOPPED")
            elif status['event'] == zmq.EVENT_ALL:
                print("zmq.EVENT_ALL")
            elif status['event'] == zmq.EVENT_HANDSHAKE_FAILED_NO_DETAIL:
                print("zmq.EVENT_HANDSHAKE_FAILED_NO_DETAIL")
                print("EXITING ON HANDSHAKE FAILED")
                sys.exit(0)
            elif status['event'] == zmq.EVENT_HANDSHAKE_FAILED_PROTOCOL:
                print("zmq.EVENT_HANDSHAKE_FAILED_PROTOCOL")
            elif status['event'] == zmq.EVENT_HANDSHAKE_FAILED_AUTH:
                print("zmq.EVENT_HANDSHAKE_FAILED_AUTH")
            else:
                print(f"Do not recognize status {status}")
        monitor.close()
        if retries >= 10:
            print(f"EXITING! Retries={retries}")
            sys.exit(1)
        time.sleep(0.3)


    #--------------------------- private functions --------------------------#
    def run(self):
        print("Subscriber running")
        while self.active:
            data = None
            try:
                data = self.socket.recv_string()
                topic, data = data.split(" ", 1)
                data = json.loads(data)
                event_type = topic.split("-")[1]
                if event_type == 'book':
                    exch = topic.split("-")[0]
                    pair = "-".join(topic.split("-")[2:])
                    e = QuoteEvent(exch, pair, data)
                    self.ui_engine.put(e)
                elif event_type == "trades":
                    e = TradeEvent(data)
                    self.ui_engine.put(e)
                else:
                    print(f"Could not determine event_type for topic={topic} event_type={event_type}")
            except zmq.error.Again:
                continue
            except Exception as e:
                print(f"EXECEPTION! {e}. Breaking out of loop. Topic={topic} Data={data}")
                break
            time.sleep(.001)
        
        self.active = False
        print("Done running ServerSubscriber")


    def start(self):
        self.active = True
        if not self._thread.isAlive():
            print("ServerSubscriber start")
            self._thread.start()
        else:
            print("ServerSubscriber already alive???")

    def stop(self):
        # self.socket.unbind(self.addr)
        # self.socket.close()
        self.active = False
        
        if self._thread.isAlive():
            print("ServerSubscriber join")
            self._thread.join(timeout=2)

        if self._thread.isAlive():
            print("ServerSubscriber join operation timed out!")
        


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
