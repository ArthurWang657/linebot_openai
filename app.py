from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

#======python的函數庫==========
import tempfile, os
import datetime
import openai
import time
#======python的函數庫==========

app = Flask(__name__)
static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')
# Channel Access Token
line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
# Channel Secret
handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))
# OPENAI API Key初始化設定
openai.api_key = os.getenv('OPENAI_API_KEY')


context = [ {'role':'system', 'content':"""
        你是客服機器人，為台灣三住自動收集訂單信息。
        你要首先問候顧客。然後等待用戶回複收集訂單信息。收集完信息需確認顧客是否還需要添加其他內容。
        最後告訴顧客訂單總金額，並送上祝福。
        請確保明確所有選項，以便從清單中識別出該項唯一的內容。

        清單包括：
        中精度高扭矩時規皮帶輪S3M型 122
        小徑滾珠軸承 兩側密封式 11
        壓縮彈簧 外徑基準不鏽鋼型 重荷重型 9
        凸輪軸承隨動器　頭部內六角孔　平面型 121
        """}
]



def GPT_response(text):
    # 接收回應
    prompt = text
    context.append({'role':'user', 'content':f"{prompt}"})
    response = get_completion_from_messages(context) 
    context.append({'role':'assistant', 'content':f"{response}"})
     
    return response


def get_completion_from_messages(messages):
    # 接收回應
    response = openai.chat.completions.create(
        model = 'ft:davinci-002:tymphany::8fATMT3E',
        messages=messages,
        temperature=1
    )
    
    print(response.choices[0].message.content)
    return response.choices[0].message.content



# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'


# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text
    GPT_answer = GPT_response(msg)
    print(GPT_answer)
    line_bot_api.reply_message(event.reply_token, TextSendMessage(GPT_answer))

@handler.add(PostbackEvent)
def handle_message(event):
    print(event.postback.data)


@handler.add(MemberJoinedEvent)
def welcome(event):
    uid = event.joined.members[0].user_id
    gid = event.source.group_id
    profile = line_bot_api.get_group_member_profile(gid, uid)
    name = profile.display_name
    message = TextSendMessage(text=f'{name}歡迎加入')
    line_bot_api.reply_message(event.reply_token, message)
        
        
import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
