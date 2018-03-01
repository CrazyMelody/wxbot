# -*- coding: utf-8-*-
import random

from wxpy import *
import os
import requests
import configparser
import re
import time
import EventMark
import sys

if len(sys.argv) > 1:
    bot = Bot(cache_path=True,console_qr=True)
else:
    bot = Bot(cache_path=True)
bot.enable_puid('wxpy_puid.pkl')

global EventMark
i = bot.friends().search("天选老司机")[0]
group = bot.groups().search("6666666666")[0]
i.send("hello")


@bot.register([i, group])
def message_handler(msg):
    global EventMark
    EventMark.imsg = msg
    config = configparser.RawConfigParser()

    if msg.type == 'Picture':
        if EventMark.getImageFlag:
            msg.get_file(msg.file_name)
            msg.reply_file(msg.file_name)
            EventMark.getImageFlag = False
        if EventMark.convertEmoji:
            msg.get_file(msg.file_name)
            new_file_name = msg.file_name[:-4] + ".gif"
            os.rename(msg.file_name, new_file_name)
            msg.reply_image(new_file_name)

    if msg.type == "Sharing":
        if EventMark.waimaiFlag:
            config.read("bind.cfg")
            try:
                if msg.member is not None:
                    mobile = config.get("mobile", msg.member.name)
                else:
                    mobile = config.get("mobile", msg.sender.name)
                resp = requests.post("http://101.132.113.122:3007/hongbao", data={"mobile": mobile, "url": msg.url})
                message = resp.json().get("message")
                print(message)
                EventMark.waimaiFlag = False
                return message
            except configparser.NoOptionError:
                return "还未绑定手机号"
    if msg.type == "Text":
        text = msg.text
        if text == "转图片":
            EventMark.getImageFlag = True
            return "转图片已开启，将自动将下一个表情转换为附件"

        if text == "转表情":
            EventMark.convertEmoji = True
            return "转表情已开启，将自动将下一个图片转为表情"

        if text == "外卖红包":
            EventMark.waimaiFlag = True
            return "将自动领取下一个链接的外卖红包"

        if text == "饿了么外卖" or text == "美团外卖":
            if text == "饿了么外卖":
                link = "https://www.pinghongbao.com/eleme/%s"
            elif text == "美团外卖":
                link = "https://www.pinghongbao.com/meituanwaimai/%s"

            config.read("bind.cfg")
            try:
                if msg.member is not None:
                    mobile = config.get("mobile", msg.member.name)
                else:
                    mobile = config.get("mobile", msg.sender.name)
            except configparser.NoOptionError:
                return "还未绑定手机号"

            for page in range(1, 5):
                resp = requests.get(link % page)
                print("正在请求", link % page)
                if resp.status_code == 200:
                    match = re.finditer(r"openURL\(&#39;(\S{16})&#39;.*\)", resp.text)
                    codes = [code.group(1) for code in match]
                    for code_page in range(1, len(codes)):
                        resp = requests.get("https://www.pinghongbao.com/go/%s" % codes[code_page])
                        resp = requests.post("http://101.132.113.122:3007/hongbao",
                                             data={"mobile": mobile, "url": resp.url})
                        print(resp.json())
                        result = resp.json().get("message")
                        if result.find(mobile[-4:]) != -1 or result.find("上限") != -1 or result.find("用完") != -1:
                            return result
                        time.sleep(2)
                else:
                    print(resp)

        if text.startswith("绑定手机:"):
            mobile = text[5:]
            print("绑定手机号为：", mobile)
            config.read("bind.cfg")
            try:
                config.add_section("mobile")
            except configparser.DuplicateSectionError:
                pass
            if msg.member is not None:
                config.set('mobile', msg.member.name, mobile)
            else:
                config.set('mobile', msg.sender.name, mobile)
            config.write(fp=open('bind.cfg', 'w'))
            return "绑定成功"

    print(msg)


embed()
