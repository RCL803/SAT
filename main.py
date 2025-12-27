# main.py
from bp_recognizer import recognize_bp_from_image
from fastapi import FastAPI, Request, WebSocket
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, ImageMessage, TextSendMessage
from linebot.exceptions import InvalidSignatureError
from excel_writer import write_bp_to_excel

import requests
import os
import uuid

app = FastAPI()

LINE_CHANNEL_ACCESS_TOKEN = "Ex9r9MnYAXVP0OilcRtfqMhRFFT0Xv2gE6EV7J0FbD4YC/jnsY43u6xKxWxHbjnthTDnFiPhmuMDMQvSgqg0OUVMgcE1Ysyjlhjc1VyHirKl6l7jD4Wb0SgxbVznSo39ZoJG0+JB63HT0HSx7cutBQdB04t89/1O/w1cDnyilFU="
LINE_CHANNEL_SECRET = "031c8e8ac21ed1d71377552eb9408f4e"

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

@app.post("/callback")
async def callback(request: Request):
    body = await request.body()
    signature = request.headers.get("X-Line-Signature")

    try:
        handler.handle(body.decode("utf-8"), signature)
    except InvalidSignatureError:
        return "Invalid signature"

    return "OK"

@handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):
    message_id = event.message.id

    # 1️⃣ 下載 LINE 圖片
    content = line_bot_api.get_message_content(message_id)

    os.makedirs("line_images", exist_ok=True)
    image_path = f"line_images/{uuid.uuid4()}.jpg"

    with open(image_path, "wb") as f:
        for chunk in content.iter_content():
            f.write(chunk)

    # 2️⃣ 自動辨識（⚠️ 這裡就是你整個 AI）
    SYS, DIA = recognize_bp_from_image(image_path)
    write_bp_to_excel(SYS, DIA)

    # 代入公式計算 y' (y = 0.0859 * DIA + 102.11)
    if DIA is not None:
        y_prime = 0.0859 * DIA + 102.11

        # 計算 SYS - y' 的絕對值
        z = abs(SYS - y_prime)

        # 判斷是否異常
        if z > 3:
            result = "異常"
        else:
            result = "正常"
    else:
        result = "未能辨識血壓數值"

    # 3️⃣ 回傳 LINE 結果
    reply = (
        f"📊 血壓辨識結果\n"
        f"SYS：{SYS}\n"
        f"DIA：{DIA}\n"
        f"判斷結果：{result}\n"
    )

    line_bot_api.reply_message(event.reply_token,TextSendMessage(text=reply))

# WebSocket 端點
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        try:
            result = await websocket.receive_text()
            # 這裡會發送來自後端的 SYS、DIA 以及判斷結果
            await websocket.send_text(f"SYS: {SYS}, DIA: {DIA}, Result: {result}")
        except WebSocketDisconnect:
            print("Client disconnected")
            break

# 傳送資料到前端
def send_to_frontend(SYS, DIA, result):
    # 您可以根據需要將資料發送到 WebSocket 或其他前端通訊方式
    pass

