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
        你是客服機器人，為台灣三住自動回答問題。
        你要首先問候顧客。然後等待用戶詢問問題。客戶問的問題主要依照下面的問答內容來回答。
         
        你的回應應該以簡短、非常隨意和友好的風格呈現。

        問答內容：

        FA的線性襯套是什麼品牌?
FA的線性襯套為MISUMI品牌。
MISUMI各類線性襯套的防鏽能力比較？
防鏽能力由強至弱：低溫鍍黑鉻→無電解鍍鎳→不鏽鋼（SUS440C）→軸承鋼（SUJ2）。普通軸承鋼容易生鏽，一定要定期塗抹防鏽油使用。
收到的線性襯套漏油怎麼辦？
線性襯套出廠時塗抹對潤滑脂等影響很少的防鏽油（除MX型潤滑脂裝置以外），建議使用前超音波清洗機清洗，乾燥後塗抹潤滑脂再使用。
單襯型線性襯套和雙襯型線性襯套的區別？
單襯型是一排鋼珠，雙襯型是兩排鋼珠。長度一般雙襯型是單襯型的2倍以上，鋼珠接觸面積更長，徑向晃動量更小，額定負載更大。
線性襯套上有產品刻印嗎？
有。但產品刻印不含帶潤滑裝置MX，潤滑脂L，G，H字樣。
線性襯套用間隔環一般與MISUMI銷售的哪些零部件搭配使用？
建議與旋轉軸、驅動軸、軸承、連座軸承以及防鬆螺母等配套使用。
線性襯套用間隔環有哪些材質以及表面處理？
材質有一般結構鋼，5000系列鋁合金以及SUS304（相當），針對於一般結構鋼材質的表面處理有染黑和無電解鍍鎳。
線性襯套用間隔環的用途？
主要用於對線性襯套的精準定位。
線性襯套用間隔環的交貨期？
由於是標準加工品，非大口訂單大部分為3個工作日，瞬達服務僅需1個工作日。
線性襯套用間隔環的種類？
根據在實際設計中軸承的固定方式不同，可分為內圈固定型線性襯套用間隔環和外圈固定型線性襯套用間隔環。
線性襯套如何定期維護？
MISUMI推薦線性襯套定期補充潤滑脂，推薦每6個月一次。當移動距離較長時，推薦3個月一次或者當移動距離在期限範圍內超過1000km時，以1000km為准。
MISUMI推薦線性襯套應定期補充潤滑油脂，推薦每6個月一次。當移動距離較長時，推薦3個月一次或者當移動距離在期限範圍內超過1000km時，以1000km為準。
線性襯套使用用途是什麼？
線性襯套與線性導桿組合使用，通過內部鋼珠迴圈結構滾動，進行無限直線運動。
線性襯套和導桿配合使用時，部分配合的比較緊密，但有些間隙比較大，是否影響使用？
線性襯套和導桿是通過迴圈鋼珠結構進行點接觸滾動配合的，由於是點接觸且非過盈配合，軸與軸承間有間隙是正常的現象，並不會影響使用，這種結構的使用，大大降低摩擦阻力，同時提高了工件的使用壽命。
線性襯套的防銹能力比較？
防銹能力由強至弱：低溫鍍黑鉻→無電解鍍鎳→無表面處理。
線性襯套的防鏽能力比較？
防鏽能力由強至弱：低溫鍍黑鉻→無電解鍍鎳→無表面處理。<br>普通軸承鋼和不鏽鋼（SUS440C）容易生鏽，一定要定期塗抹防鏽油使用。
線性襯套是否可以旋轉？
線性襯套在結構上不適合旋轉運動，如果強行旋轉，則可能導致產品損壞。
線性襯套種類及各自的優缺點是什麼？
MISUMI的線性襯套主要分為3大類：直柱型、法蘭型、帶固定座型。<br>直柱型線性襯套的優點：1.價格便宜;2.佔用空間小;3.庫存較多；缺點:使用時要自己加工固定座,費時費力。<br>法蘭型線性襯套的優點: 通過法蘭的沉孔用內六角固定,因此安裝方便；缺點:價格較直柱型貴。<br>帶固定座型線性襯套的優點:鋁合金外殼內置線性襯套，可減少零件數量和加工工時；缺點:佔用空間大;價格也是較其他兩種更貴。
線性襯套選擇和安裝時的注意事項是什麼？
1、線性襯套承受較大的力矩負載（偏載）時，建議使用雙襯型或多個單襯型線性襯套。<br>2、線性襯套在結構上不適合旋轉運動。如果強行旋轉，可能導致產品的損壞，請注意使用。<br>3、線性襯套不適合反復插拔。<br>4、將導桿插入線性襯套中時，請對準中心並慢慢插入，否則會導致滾珠脫落或保持器變形。
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
    response = openai.ChatCompletion.create(
        model = 'gpt-3.5-turbo',
        messages=messages,
        temperature=1
    )
    
    print(response.choices[0].message["content"])
    return response.choices[0].message["content"]



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
