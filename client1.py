from websockets.asyncio.client import connect
from ist_ws_python import Ws_Param
from colorama import Fore
import websockets
import colorama
import asyncio
import base64
import json

colorama.init()
async def send_audio_data(websocket_client: connect, wsParam: Ws_Param):
    status = 0
    with open(wsParam.AudioFile, 'rb') as file:
        while True:
            audio_buff = file.read(1280)
            if not audio_buff:
                status = 2
            if status == 0:
                data = {"common": wsParam.CommonArgs,
                        "business": wsParam.BusinessArgs,
                        "data": {"status": 0, "format":"audio/L16;rate=16000",
                                    "audio": str(base64.b64encode(audio_buff), 'utf-8'),
                                    'encoding': "raw"}}
                await websocket_client.send(json.dumps(data))
                status = 1
            elif status == 1:
                data = {
                        "data": {"status": 1, "format":"audio/L16;rate=16000",
                        "audio": str(base64.b64encode(audio_buff), 'utf-8'),
                        'encoding': "raw"}}
                await websocket_client.send(json.dumps(data))
            elif status == 2:
                data = {
                    "data": {"status": 2, "format": "audio/L16;rate16000",
                    "audio": str(base64.b64encode(audio_buff), 'utf-8'),
                    "encoding": "raw"}}
                await websocket_client.send(json.dumps(data))
                await asyncio.sleep(1)
                break
            await asyncio.sleep(0.04)
    await websocket_client.close()


async def receive_messages(websocket):
    try:
        while True:
            print("## wait data come from websocket server ##")
            message = await websocket.recv()
            print("## receive message from websocket server ##")
            try:
                code = json.loads(message)["code"]
                sid = json.loads(message)["sid"]
                if code != 0:
                    errMsg = json.loads(message)["message"]
                    print(f"sid:{sid} \ncall error:{errMsg} \ncode is:{code}")
                else:
                    data = json.loads(message)["data"]["result"]["ws"]
                    result = ""
                    for i in data:
                        for w in i["cw"]:
                            result += w["w"]
                    print(result)
            except Exception as e:
                print("Receive message, but parsing exception:", e)
    except websockets.exceptions.ConnectionClosedError as cls_err:
        print(Fore.CYAN + f"Connection closed: {cls_err}" + Fore.RESET)
    except websockets.exceptions.ConnectionClosedOK as cls_ok:
        print(Fore.CYAN + f"Connection closed: {cls_ok}" + Fore.RESET)
    except websockets.exceptions.ConnectionClosed as cls:
        print(Fore.CYAN + f"Connection closed: {cls}" + Fore.RESET)
    except Exception as e:
        print("Error receiving messages:", e)



async def main_client(wsParam: Ws_Param):
    url = wsParam.create_url()
    async with connect(url) as ws_client:
        send_task = asyncio.create_task(send_audio_data(websocket_client=ws_client, wsParam=wsParam))
        receive_task = asyncio.create_task(receive_messages(websocket=ws_client))
        await asyncio.gather(send_task, receive_task)


if __name__ == "__main__":        
    wsParam = Ws_Param(APPID="", APISecret="",
                    APIKey="",
                    AudioFile="")
    try:
        asyncio.run(main_client(wsParam))
    except KeyboardInterrupt:
        print(Fore.RED + "\nDisconnect ...")