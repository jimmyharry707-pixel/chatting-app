"""Reconnectable websocket worker with thread-safe outbound events."""
import json,threading,websocket
from PyQt5.QtCore import QThread,pyqtSignal

class RealtimeWorker(QThread):
    event_received=pyqtSignal(dict)
    status_changed=pyqtSignal(str)
    def __init__(self,url,reconnect_seconds=3,parent=None):
        super().__init__(parent); self.url=url; self.delay=reconnect_seconds
        self.stop_event=threading.Event(); self.app=None; self.lock=threading.Lock()
    def on_open(self,ws): self.status_changed.emit("Connected")
    def on_message(self,ws,raw):
        try:
            payload=json.loads(raw)
            if isinstance(payload,dict): self.event_received.emit(payload)
        except (ValueError,TypeError): pass
    def on_error(self,ws,error): self.status_changed.emit(f"Realtime: {error}")
    def on_close(self,ws,code,reason):
        if not self.stop_event.is_set(): self.status_changed.emit("Disconnected; reconnecting…")
    def run(self):
        while not self.stop_event.is_set():
            self.status_changed.emit("Connecting to live updates…")
            self.app=websocket.WebSocketApp(self.url,on_open=self.on_open,on_message=self.on_message,
                                             on_error=self.on_error,on_close=self.on_close)
            self.app.run_forever(ping_interval=20,ping_timeout=10)
            self.app=None
            self.stop_event.wait(self.delay)
    def send_event(self,payload):
        with self.lock:
            if self.app and self.app.sock and self.app.sock.connected:
                try: self.app.send(json.dumps(payload))
                except Exception: pass
    def stop(self):
        self.stop_event.set()
        if self.app:
            try: self.app.close()
            except Exception: pass
        self.wait(3000)
