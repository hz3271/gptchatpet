import asyncio
import tkinter as tk
import json
import websockets
import threading
import time

class Simple:
    def __init__(self):
        try:
            self.websocket = None
            self.i=0
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self.start_connect()
        except Exception:
            print("未开启live2d")
            return OSError


    async def connect(self):
        uri = "ws://127.0.0.1:10086/api"
        async with websockets.connect(uri) as websocket:
            self.websocket = websocket
            msg = {"msg": 10000, "msgId": 1}
            await self.websocket.send(json.dumps(msg))
            print("***连接中***")
            while True:
                response = await self.websocket.recv()
                if isinstance(response, str):
                    response = json.loads(response)
                msg_value = response.get('msg', None)
                if msg_value == 10000:
                    print("***连接成功***")
                    self.i=1
                    print(self.i)
                else:
                    print(response)

    def start_connect(self):
        def target():
            try:
                self.loop.run_until_complete(self.connect())

            except Exception:
                print("未开启live2d")
                pass
        threading.Thread(target=target).start()




    async def send_message(self,text):
        msg1 = {
            "msg": 11000,
            "msgId": 1,
            "data": {
                "id": 0,
                "text": str(text),
                "textFrameColor": 0x000000,
                "textColor": 0xFFFFFF,
                "duration": 600000,
            }
        }
        msg2 = {
            "msg": 13200,
            "msgId": 1,
            "data": {
                "id": 0,
                "type": 0,
                "mtn": "talk#3"
            }
        }
        await self.websocket.send(json.dumps(msg1))
        print("发送消息")
        await self.websocket.send(json.dumps(msg2))
        print("更改表情")

    def call_send_message(self, text):
        while True:
            if self.i == 1:
                asyncio.run(self.send_message(text))
                break

#chat2d=Simple()
#chat2d.call_send_message("你好")