import time
import hmac
import hashlib
import base64
import json
import os
import urllib.parse
import logging
import requests

def initLogging():
    logging.getLogger().setLevel(logging.INFO)
    logging.basicConfig(format="[%(levelname)s]; %(message)s")


class sendNotify:
    # ============================ 微信server酱通知设置区域 ============================
    # 此处填你申请的SCKEY.
    # 注：此处设置github action用户填写到Settings-Secrets里面(Name输入PUSH_KEY)
    SCKEY = ''
    SCKEY = os.environ.get('SCKEY')
    # ============================ Bark App通知设置区域 ============================
    # 此处填你BarkAPP的信息(IP/设备码，例如：https://api.day.app/XXXXXXXX)
    # 注：此处设置github action用户填写到Settings-Secrets里面（Name输入BARK_PUSH）
    BARK_PUSH = ''
    BARK_PUSH = os.environ.get('BARK_PUSH')
    # BARK app推送铃声,铃声列表去APP查看复制填写
    # 注：此处设置github action用户填写到Settings-Secrets里面（Name输入BARK_SOUND ,
    # Value输入app提供的铃声名称，例如:birdsong）
    BARK_SOUND = ''
    BARK_SOUND = os.environ.get('BARK_SOUND')
    # ============================ Telegram机器人通知设置区域 ============================
    # 此处填你telegram bot 的Token，例如：1077xxx4424:AAFjv0FcqxxxxxxgEMGfi22B4yh15R5uw
    # 注：此处设置github action用户填写到Settings-Secrets里面(Name输入TG_BOT_TOKEN)
    TG_BOT_TOKEN = ''
    TG_BOT_TOKEN = os.environ.get('TG_BOT_TOKEN')
    # 此处填你接收通知消息的telegram用户的id，例如：129xxx206
    # 注：此处设置github action用户填写到Settings-Secrets里面(Name输入TG_USER_ID)
    TG_USER_ID = ''
    TG_USER_ID = os.environ.get('TG_USER_ID')
    # ============================ 钉钉机器人通知设置区域 ============================
    # 此处填你钉钉 bot 的webhook，例如：5a544165465465645d0f31dca676e7bd07415asdasd
    # 注：此处设置github action用户填写到Settings-Secrets里面(Name输入DD_BOT_TOKEN)
    DD_BOT_TOKEN = ''
    DD_BOT_TOKEN = os.environ.get('DD_BOT_TOKEN')
    # 密钥，机器人安全设置页面，加签一栏下面显示的SEC开头的字符串
    DD_BOT_SECRET = ''
    DD_BOT_SECRET = os.environ.get('DD_BOT_SECRET')
    # ============================ QQ酷推通知设置区域 ============================
    # 此处填你申请的SKEY(具体详见文档 https://cp.xuthus.cc/)
    # 注：此处设置github action用户填写到Settings-Secrets里面(Name输入QQ_SKEY)
    QQ_SKEY = ''
    QQ_SKEY = os.environ.get('QQ_SKEY')
    # 此处填写私聊或群组推送，默认私聊(send或group或者wx)
    QQ_MODE = 'send'
    
    def serverNotify(self, text, desp):
        if sendNotify.SCKEY != '':
            url = 'https://sctapi.ftqq.com/' + sendNotify.SCKEY + '.send'
            if "\n" in desp:
                desp = desp.replace("\n", "\n\n")
            data = {
                'text': text,
                'desp': desp
            }
            response = json.dumps(
                requests.post(
                    url,
                    data).json(),
                ensure_ascii=False)
            datas = json.loads(response)
            # print(datas)
            if datas['code'] == 0:
                logging.info('server酱发送通知消息成功')
            elif datas['code'] == 40001:
                logging.warning('PUSH_KEY 错误\n')
            else:
                logging.warning('发送通知调用API失败！！\n')
        else:
            logging.info('您未提供server酱的SCKEY，取消微信推送消息通知')

    def BarkNotify(self, text, desp):
        ##desp=desp.replace('\n', ' ').replace('\r\n', ' ')
        if sendNotify.BARK_PUSH != '':
            url = sendNotify.BARK_PUSH + '?sound=' + sendNotify.BARK_SOUND
            headers = {'Content-type': "application/x-www-form-urlencoded"}
            data = {
                'title': text,
                'body': desp
            }
            response = json.dumps(
                requests.post(
                    url,
                    data,
                    headers=headers).json(),
                ensure_ascii=False)

            data = json.loads(response)
            if data['code'] == 400:
                logging.warning(data['message'])
                logging.warning('\n找不到 Key 对应的 DeviceToken\n')
            elif data['code'] == 200:
                logging.info('Bark APP发送通知消息成功')
            else:
                logging.warning('\n发送通知调用API失败！！\n')
                logging.warning(data)
        else:
            logging.info('您未提供Bark的APP推送BARK_PUSH，取消Bark推送消息通知')

    def tgBotNotify(self, text, desp):
        if sendNotify.TG_BOT_TOKEN != '' or sendNotify.TG_USER_ID != '':
            desp=desp.replace("-", "\\-")
            url = 'https://api.telegram.org/bot' + sendNotify.TG_BOT_TOKEN + '/sendMessage'
            headers = {'Content-type': "application/x-www-form-urlencoded"}
            body = 'chat_id=' + sendNotify.TG_USER_ID + '&text=' + urllib.parse.quote(
                text) + '\n\n' + urllib.parse.quote(desp) + '&parse_mode=MarkdownV2' \
                +'&disable_web_page_preview=true'
            response = json.dumps(
                requests.post(
                    url,
                    data=body,
                    headers=headers).json(),
                ensure_ascii=False)

            data = json.loads(response)
            print(data)
            if data['ok']:
                logging.info('Telegram发送通知消息完成')
            elif data['error_code'] == 400:
                logging.warning('请主动给bot发送一条消息并检查接收用户ID是否正确。\n')
            elif data['error_code'] == 401:
                logging.warning('Telegram bot token 填写错误。\n')
            else:
                logging.warning('发送通知调用API失败！！\n')
                logging.warning(data)
        else:
            logging.info('您未提供Telegram Bot的BOT_TOKEN或USER_ID，取消Telegram Bot推送消息通知')

    def dingNotify(self, text, desp):
        if sendNotify.DD_BOT_TOKEN != '':
            url = 'https://oapi.dingtalk.com/robot/send?access_token=' + sendNotify.DD_BOT_TOKEN
            data = {
                "msgtype": "text",
                "text": {
                    'content': text + desp
                }
            }
            headers = {
                'Content-Type': 'application/json;charset=utf-8'
            }
            if sendNotify.DD_BOT_SECRET != '':
                timestamp = str(round(time.time() * 1000))
                secret = sendNotify.DD_BOT_SECRET
                secret_enc = secret.encode('utf-8')
                string_to_sign = '{}\n{}'.format(timestamp, secret)
                string_to_sign_enc = string_to_sign.encode('utf-8')
                hmac_code = hmac.new(
                    secret_enc,
                    string_to_sign_enc,
                    digestmod=hashlib.sha256).digest()
                sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
                url = 'https://oapi.dingtalk.com/robot/send?access_token=' + \
                    sendNotify.DD_BOT_TOKEN + '&timestamp=' + timestamp + '&sign=' + sign

            response = requests.post(
                url=url,
                data=json.dumps(data),
                headers=headers).text
            if json.loads(response)['errcode'] == 0:
                logging.info('钉钉发送通知消息成功')
            else:
                logging.warning('发送通知失败！！\n')
        else:
            logging.info('您未提供钉钉的有关数据，取消钉钉推送消息通知')

    def coolpush(self, text, desp):
        if sendNotify.QQ_SKEY != '':
            url = "https://push.xuthus.cc/" + sendNotify.QQ_MODE + "/" + sendNotify.QQ_SKEY
            params = {"c": desp, "t": text}
            headers = {'content-type': 'charset=utf8'}
            response = json.dumps(
                requests.post(
                    url=url,
                    params=params,
                    headers=headers).json(),
                ensure_ascii=False)
            datas = json.loads(response)

            if datas['code'] == 200:
                logging.info('QQ推送发送通知消息成功')
            elif datas['code'] == 500:
                logging.warning('QQ推送QQ_SKEY错误\n')
            else:
                logging.warning('发送通知调用API失败！！\n')

        else:
            logging.info('您未提供酷推的SKEY，取消QQ推送消息通知')


    def send(self, **kwargs):
        send = sendNotify()
        title = kwargs.get("title", "")
        msg = kwargs.get("msg", "")
        #send.serverNotify(title, msg)
        #send.BarkNotify(title, msg)
        send.tgBotNotify('*' + title + '*', msg)
        #send.dingNotify(title, msg)
        #send.coolpush(title, msg)


if __name__ == "__main__":
    os.environ['TZ'] = 'Asia/Shanghai'
    try:
        time.tzset()
    except BaseException:
        pass
    initLogging()
    Notify = sendNotify()
    Notify.send(title='这是标题', msg='这是内容')
