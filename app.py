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


def GPT_response(text):
    # 接收回應
    response = openai.ChatCompletion.create(
        model = 'gpt-3.5-turbo',
        messages=[ {"role": "system", "content": "You are a friendly chatbot."},
        {"role": "user", "content": "請為MISUMI台灣公司撰寫一個簡要的描述。"},
        {"role": "assistant", "content": "MISUMI台灣是MISUMI集團的一個分支機構，屬於日本MISUMI集團的一部分。他們是一家全球性的供應商，提供工業用零件和零件設計的解決方案。MISUMI台灣提供各種標準零件，如螺絲、螺母、軸承、線性導軌、夾具等，同時也提供客製化的設計服務，以滿足不同客戶的需求。他們的目標是提供高品質、高精度的產品，並且致力於縮短交貨時間，讓客戶能夠更有效率地進行生產和製造。MISUMI台灣的產品廣泛應用於許多行業，包括機械、汽車、電子、半導體、醫療等。如需更多詳細資訊，請訪問MISUMI台灣的官方網站或直接聯繫他們。"},
        {"role": "user", "content": "請根據MISUMI台灣公司的業務，列出至少五個產品類別。"},
        {"role": "assistant", "content": "螺絲、螺母和螺栓：包括各種尺寸和材質的螺絲、螺母和螺栓，用於固定和連接零件。 \
線性導軌：提供高精度的線性運動控制解決方案，用於機械和自動化應用。 \
夾具：各種夾具和固定裝置，用於固定工件並實現準確的加工和裝配。 \
軸承：提供不同類型的軸承，用於支撐和減少機械零件之間的摩擦。 \
模具和模具零件：各種模具和模具零件，用於注塑、壓鑄等製造工藝。 \
這些只是MISUMI台灣公司產品的一小部分，他們還提供許多其他類別的工業用零件和相關產品。如果您對特定產品或更多產品類別感興趣，建議您訪問MISUMI台灣的官方網站或直接聯繫他們以獲取更詳細的資訊。"}
    ])
    print(response)
    # 重組回應
    answer = response['choices'][0]['message']['content']
    print(answer)
    return answer


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
