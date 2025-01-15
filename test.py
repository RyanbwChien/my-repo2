# -*- coding: utf-8 -*-
"""
Created on Fri Jan 10 20:21:45 2025

@author: user
"""

import requests
from flask import Flask, request, abort
# import redis  # Redis 作为会话存储
# 載入 json 標準函式庫，處理回傳的資料格式
import json
import pymysql
# 載入 LINE Message API 相關函式庫
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, StickerSendMessage
# from ultralytics import YOLO
# import ultralytics
import os
from linebot.models import MessageEvent, TextMessage
import redis  # Redis 作为会话存储
import openai
# import dotenv


openai.api_key = "sk-VfD850xN3z0nwdP5-JBDe6IBrdtEzvy3epQ2W_uHunT3BlbkFJosEggMit6a8ctw4sY7cxGUHgd-GrfYguJ8nJV6mcUA"


app = Flask(__name__)


def add_data_totable(ID,NAME,time):
    try:
        db_login = {
            'host':"127.0.0.1",
            'port':3306,
            'user':"root",
            'password':'1234', 
            # "db": "EXAMPLE"  
            }
        conn = pymysql.connect(**db_login)
        cur = conn.cursor()
        cur.execute("Use Example")
        
        sql_command = f"""Insert into Line_member (
          `USER ID`,
          `USERNAME`,
          `CREATE_NAME`
        ) values ({ID},{NAME},'{time}')
        ;"""
        
        cur.execute(sql_command)
        
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(e)


# =============================================================================
# # redis_host = os.getenv('REDIS_URL', 'localhost')
# url = 'rediss://:p436723e62e643cbd0e3ceb6019ad849e213b9389dd619c9aabc4b9ef8c21938f@ec2-54-85-74-43.compute-1.amazonaws.com:15990'
# r = redis.StrictRedis.from_url(url)
# 
# 
# 
# try:
#     r.ping()  # Should return True if Redis is connected successfully
#     print("Redis connection successful!")
# except redis.ConnectionError:
#     print("Redis connection failed")
# 
# =============================================================================

access_token = '7nbeHQXUhTmL0boi/XUfEnF+FbIpw5c9pCvf5oODmi3xhokSbceUNOd0AsPscwuHusHfLj5p9ixA9IWzTJQW+iIKytefUcXae6JpeX7QK67cGb8ucUgATY/oaj+NPhGbUiAd3f3t3JBnqT7/LOUdBQdB04t89/1O/w1cDnyilFU='
secret = 'e117059ff2261b2c0e6640403208b939'

line_bot_api = LineBotApi(access_token)
handler = WebhookHandler(secret)

def ask_openai(message):
    response = openai.completions.create(
        model="gpt-3.5-turbo-instruct",
        prompt = message,
        max_tokens=1000,
        n=1,
        stop=None,
        temperature=0.3,
        # handle_parsing_errors=True,
    )  
    answer = response.choices[0].text.strip()
    return answer

@app.route("/", methods=['POST'])
def linebot():
    body = request.get_data(as_text=True)                    # 取得收到的訊息內容
    try:
        json_data = json.loads(body)                         # json 格式化訊息內容
        line_bot_api = LineBotApi(access_token)              # 確認 token 是否正確
        handler = WebhookHandler(secret)                     # 確認 secret 是否正確
        signature = request.headers['X-Line-Signature']      # 加入回傳的 headers
        
        # 取得請求主體
        body = request.get_data(as_text=True)
        app.logger.info(f"Request body: {body}")

        
        data = request.json
        user_id = data['events'][0]['source']['userId']  # 获取用户 ID
        
        # LINE 的 Channel Access Token
        channel_access_token = "你的 Channel Access Token"
        
        # Get Profile API 的 URL
        url = f"https://api.line.me/v2/bot/profile/{user_id}"
        
        # 設置請求的 Headers
        headers = {
            "Authorization": f"Bearer {channel_access_token}"
        }
        
        # 發送請求
        response = requests.get(url, headers=headers)
        
        # 檢查回應狀態碼
        if response.status_code == 200:
            profile = response.json()
            display_name = profile['displayName']
            print(f"用戶名稱：{display_name}")
        else:
            print(f"無法獲取用戶名稱，錯誤碼：{response.status_code}")
        
        
        # user_name = data['events'][0]['source']['displayName']  # 获取用户名称

        print(f'User ID: {user_id}')  # 打印用户 ID 和 用户名称
    
        # r.set(user_id, user_name)
    
        # with open("user_id.txt", mode ='a') as f:
        #     f.write(f'User ID: {user_id}, User Name: {user_name}')
            
        
        handler.handle(body, signature)                      # 綁定訊息回傳的相關資訊
        tk = json_data['events'][0]['replyToken']            # 取得回傳訊息的 Token
        type = json_data['events'][0]['message']['type']     # 取得 LINe 收到的訊息類型
        
        
        if type=='text':
            msg = json_data['events'][0]['message']['text']  # 取得 LINE 收到的文字訊息
            try:                                  # 印出內容
                reply = ask_openai(msg)
            except:
                reply = msg
            line_bot_api.reply_message(
                                tk,
                                TextMessage(text=reply))    
                
        elif type == 'image':
            msgID = json_data['events'][0]['message']['id']  # 取得訊息 id
            message_content = line_bot_api.get_message_content(msgID)  # 根據訊息 ID 取得訊息內容
            # 在同樣的資料夾中建立以訊息 ID 為檔名的 .jpg 檔案
            with open(f'{msgID}.jpg', 'wb') as fd:
                fd.write(message_content.content)             # 以二進位的方式寫入檔案
            
# =============================================================================
#             model = YOLO()  # build a new model from scratch
#             
#             results = model(f'{msgID}.jpg')  # predict on an image
#             
#             class_mapping= { 0: "person",  1: "bicycle",  2: "car",
#               3: "motorcycle",  4: "airplane",  5: "bus",  6: "train",  7: "truck",  8: "boat",  9: "traffic light",
#               10: "fire hydrant",  11: "stop sign",  12: 'parking meter',  13: "bench",  14: "bird",  15: "cat",  16: "dog",
#               17: "horse",  18: "sheep",  19: "cow",  20: "elephant",  21: "bear",  22: "zebra",  23: "giraffe",  24: "backpack",
#               25: "umbrella",  26: "handbag",  27: "tie",  28: "suitcase",  29: "frisbee",  30: "skis",  31: "snowboard",  32: "sports ball",
#               33: "kite",  34: "baseball bat",  35: "baseball glove",  36: "skateboard",  37: "surfboard",  38: "tennis racket",
#               39: "bottle",  40: "wine glass",  41: "cup",  42: "fork",  43: "knife",  44: "spoon",  45: "bowl",  46: "banana",
#               47: "apple",  48: "sandwich",  49: "orange",  50: "broccoli",  51: "carrot",  52: "hot dog",  53: "pizza",  54: "donut",
#               55: "cake",  56: "chair",  57: 'couch' ,  58: "potted plant",  59: 'bed',  60: "dining table",  61: 'toilet',  62: 'tv',  63: 'laptop',  64: 'mouse',  65: 'remote',  66: 'keyboard',  67: "cell phone",  68: 'microwave',
#               69: 'oven',  70: 'toaster', 71: 'sink',  72: 'refrigerator',  73: 'book',  74: 'clock',  75: 'vase',  76: 'scissors',  77: "teddy bear",  78: "hair drier",  79: 'toothbrush',
#               }
# 
# 
#             for result in results:
#                 for cls_id, custom_label in class_mapping.items():
#                     if cls_id in result.names: # check if the class id is in the results
#                         result.names[cls_id] = custom_label # replace the class name with the custom label
#                 # result.show()
#                 result.save(os.path.join(f"{msgID}_predict.jpg"))  # save to disk
# =============================================================================

            
            reply = '你傳的圖片儲存完成！'                             # 設定要回傳的訊息
            line_bot_api.reply_message(
                                tk,
                                TextMessage(text=reply))    
            
            
        else:
            reply = '你傳的不是文字也不是圖片呦～'
        # print(reply)
        # line_bot_api.reply_message(tk,TextSendMessage(reply))# 回傳訊息
            try:
                message = StickerSendMessage(
                    package_id = '8522',
                    sticker_id = '16581289'
                )
                line_bot_api.reply_message(tk, message)
            except:
                line_bot_api.reply_message(tk,
                TextSendMessage(text= 'Sorry~故障囉！'))
    except:
        print(body)                                          # 如果發生錯誤，印出收到的內容
    return 'OK'           
                                   # 驗證 Webhook 使用，不能省略

if __name__ == "__main__":
    app.run()