'''
Simulate Perfect Campus App login and get user token
'''
import hashlib
import random
import json
import requests
import urllib3
import logging
from login import des_3
from login import rsa_encrypt as rsa


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class CampusCard:
    """
    完美校园App
    初始化时需要传入手机号码、密码
    """
    __slots__ = ['phone', 'password', 'user_info']

    def __init__(self, phone, password):
        """
        初始化一卡通类
        :param phone: 完美校园账号
        :param password: 完美校园密码
        """
        self.phone = phone
        self.password = password
        self.user_info = self.create_blank_user()
        flag = self.exchange_secret()
        if flag:
            self.login()


    def create_blank_user(self):
        """
        当传入的已登录设备信息不可用时，虚拟一个空的未登录设备
        :return: 空设备信息
        """
        rsa_keys = rsa.create_key_pair(1024)
        return {
            'appKey': '',
            'sessionId': '',
            'exchangeFlag': True,
            'login': False,
            'serverPublicKey': '',
            'deviceId': str(self.phone),
            'wanxiaoVersion': 10531102,
            'rsaKey': {
                'private': rsa_keys[1],
                'public': rsa_keys[0]
            }
        }

    def exchange_secret(self):
        """
        与完美校园服务器交换RSA加密的公钥，并取得sessionId
        :return:结果
        """
        try:
            resp = requests.post(
                # "https://server.17wanxiao.com/campus/cam_iface46/exchangeSecretkey.action",
                "https://app.17wanxiao.com:443/campus/cam_iface46/exchangeSecretkey.action",
                headers={
                    # "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 5.1.1; HUAWEI MLA-AL10 Build/HUAWEIMLA-AL10)",
                    "User-Agent": "NCP/5.3.1 (iPhone; iOS 13.5; Scale/2.00)",
                },
                json={
                    "key": self.user_info["rsaKey"]["public"]
                },
                verify=False
            )
            session_info = json.loads(
                rsa.rsa_decrypt(
                    resp.text.encode(
                        resp.apparent_encoding),
                    self.user_info["rsaKey"]["private"]))
            self.user_info["sessionId"] = session_info["session"]
            self.user_info["appKey"] = session_info["key"][:24]
            return True
        except Exception as e:
            logging.warning(e)
            return False

    def login(self):
        """
        使用账号密码登录完美校园App
        """
        password_list = []
        for i in self.password:
            password_list.append(
                des_3.des_3_encrypt(
                    i,
                    self.user_info["appKey"],
                    "66666666"))  # iv必须为8位数字6
        login_args = {
            "appCode": "M002",
            "deviceId": self.user_info["deviceId"],
            "netWork": "wifi",
            "password": password_list,
            "qudao": "guanwang",
            "requestMethod": "cam_iface46/loginnew.action",
            "shebeixinghao": "iPhone12",
            "systemType": "iOS",
            "telephoneInfo": "13.5",
            "telephoneModel": "iPhone",
            "type": "1",
            "userName": self.phone,
            "wanxiaoVersion": 10531102,
            "yunyingshang": "07"
        }
        upload_args = {
            "session": self.user_info["sessionId"],
            "data": des_3.object_encrypt(
                login_args,
                self.user_info["appKey"],
                "66666666")}
        try:
                
            resp = requests.post(
                # "https://server.17wanxiao.com/campus/cam_iface46/loginnew.action",
                "https://app.17wanxiao.com/campus/cam_iface46/loginnew.action",
                headers={
                    "campusSign": hashlib.sha256(
                        json.dumps(upload_args).encode('utf-8')).hexdigest()},
                json=upload_args,
                verify=False,
                timeout=30
            ).json()
            """
            {'result_': True, 'data': '........', 'message_': '登录成功', 'code_': '0'}
            {'result_': False, 'message_': '该手机号未注册完美校园', 'code_': '4'}
            {'result_': False, 'message_': '您正在新设备上使用完美校园，请使用验证码进行验证登录', 'code_': '5'}
            {'result_': False, 'message_': '密码错误,您还有5次机会!', 'code_': '5'}
            """
            if resp["result_"]:
                # logging.info(resp)
                logging.info(f'{self.phone[:4]}：{resp["message_"]}')
                self.user_info["login"] = True
                self.user_info["exchangeFlag"] = False
                self.user_info['login_msg'] = resp
            else:
                # logging.warning(resp)
                logging.warning(f'{self.phone[:4]}：{resp["message_"]}')
                self.user_info['login_msg'] = resp
            return resp["result_"]
        except Exception as e:
            self.user_info['login_msg'] = {"message_": e}
            logging.warning(e)

    # 如果不请求一下 token 会失效
    def get_main_info(self):
        '''
        模拟App请求用户信息
        :return: 服务器响应
        '''
        resp = requests.post(
            # "https://reportedh5.17wanxiao.com/api/clock/school/open",
            "https://reportedh5.17wanxiao.com/api/clock/school/getUserInfo",
            headers={
                # "Referer": "https://reportedh5.17wanxiao.com/collegeHealthPunch/index.html?token="+self.user_info["sessionId"],
                "Referer": "https://reportedh5.17wanxiao.com/health/index.html?templateid=pneumonia&businessType=epmpics&versioncode=10531102&systemType=IOS&UAinfo=wanxiao&token=" + self.user_info["sessionId"],
                "Origin": "https://reportedh5.17wanxiao.com",
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E149 Wanxiao/5.3.1"
            },
            data={
                "appClassify": "DK",
                "token": self.user_info["sessionId"]
            },
            verify=False
        ).json()
        if resp["msg"] == '成功':
            return resp["userInfo"]
        print(resp)
        return resp

    def save_user_info(self):
        """
        保存当前的设备信息
        :return: 当前设备信息的json字符串
        """
        return json.dumps(self.user_info)
