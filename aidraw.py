import base64
from io import BytesIO
import random
from nakuru.entities.components import *
from nakuru import (
    GroupMessage,
    FriendMessage
)
from botpy.message import Message, DirectMessage
from model.platform.qq import QQ
import time
import threading
from util import cmd_config as cc
import traceback
import requests
from PIL import Image as PILImage
import os

"""
QQChannelChatGPT
"""
class AIDrawPlugin:
    """
    初始化函数, 可以选择直接pass
    """
    def __init__(self) -> None:
        print("AIDraw Support Plugin Loaded.")
        if not os.path.exists("aidraw"):
            os.mkdir("aidraw")
        self.cc = cc.CmdConfig()
        self.seed = None
        config = {
            "naifu_site": None,
            "width": 512,
            "height": 768,
            "ntags": "",
            "scale": 12,
            "step": 28,
            "batch": None,
            "strength": None,
            "noise": None,
            "width": 512,
            "height": 768,
            "step": 28,
            "n_samples": 1,
            "ucPreset": 0,
        }
        self.cc.init_attributes(["aidraw_config"], json.dumps(config))
        self.busy = False

        self.config = json.loads(self.cc.get("aidraw_config"))


    def run(self, message: str, role: str, platform: str, message_obj, qq_platform: QQ):

        if message.lower().startswith("nai") or message.lower().startswith("/nai") or message.lower().startswith("画"):
            l = message.split(" ")
            
            if len(l) == 1:
                return True, tuple([True, self.help_menu(), "nai"])
            
            if l[1].lower() == "site":
                self.config["naifu_site"] = l[2]
                self.cc.put("aidraw_config", json.dumps(self.config))
                return True, tuple([True, "[Naifu] 已设置Naifu后端链接", "nai"])
            
            if l[1].lower() == "config":
                # 查看self.config
                return True, tuple([True, f"[Naifu] 当前配置：\n{json.dumps(self.config, indent=4)}", "nai"])

            if l[1].lower() == "cset":
                if len(l) < 4:
                    return True, tuple([True, f"[Naifu] 参数不足", "nai"])
                if l[2] not in self.config:
                    return True, tuple([True, f"[Naifu] 参数不存在", "nai"])
                self.config[l[2]] = "".join(l[3:])
                self.cc.put("aidraw_config", json.dumps(self.config))
                return True, tuple([True, f"[Naifu] 参数设置成功", "nai"])
                
            
            prompt = "".join(l[1:])
            temp_params = {}
            if "#" in prompt:
                t = prompt.split("#")
                prompt = t[0]
                temp_params_list = t[1].split("|")
                temp_params = {}
                for i in temp_params_list:
                    key = i.split("=")[0]
                    value = "".join(i.split("=")[1:])
                    if key == "ntags":
                        key = "uc"

                    temp_params[key] = value

            try:
                while self.busy:
                    time.sleep(2)
                self.busy = True
                filepath = self.naifu(prompt, temp_params)
                self.busy = False
                return True, tuple([True, [Plain("图像生成成功~"), Image.fromFileSystem(filepath)], "nai"])
            except Exception as e:
                self.busy = False
                return True, tuple([True, f"[Naifu] 生成图像失败: {traceback.format_exc()}", "nai"])
                
        return False, None


    def naifu(self, prompt, tmp_params) -> str:
        if not self.config["naifu_site"]:
            raise Exception("未设置Colab链接")
        site = self.config["naifu_site"]
        if site.endswith("/"):
            site = site[:-1]
        post_url = site + "/generate-stream"
        header = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        self.seed = random.randint(0, 4294967295)
        params = {
            "prompt": prompt,
            "width": self.config["width"],
            "height": self.config["height"],
            "qualityToggle": False,
            "scale": self.config["scale"],
            "sampler": "k_euler_ancestral",
            "steps": self.config["step"],
            "seed": self.seed,
            "n_samples": self.config["n_samples"],
            "ucPreset": self.config["ucPreset"],
            "uc": self.config["ntags"],
        }
        params.update(tmp_params)

        print(json.dumps(params, indent=4))
        filepath = self.post(post_url, header, params)
        return filepath


    def post(self, url, header, params) -> str:
        r = requests.post(url, headers=header, json=params)
        print(url, r.text, params)
        try:
            img = r.text.split('data:')[1]
        except:
            raise Exception("生成图像失败: " + r.text)
        return self.save_data(img)


    def save_data(self, raw: bytes) -> str:
        raw: BytesIO = BytesIO(base64.b64decode(raw))
        img_PIL = PILImage.open(raw).convert("RGB")
        filepath = "aidraw/" + str(time.time()) + ".jpg"
        img_PIL.save(filepath, format="JPEG", quality=95)
        return filepath
        # image_new = BytesIO()
        # img_PIL.save(image_new, format="JPEG", quality=95)
        # image_new = image_new.getvalue()
        # return image_new
        
        
    def help_menu(self):
        return """
===DrawAI图像生成支持插件V1.0.0===
指令：
1. /nai <prompt> 生成一张图片
例如：/nai masterpiece, best quality, girl, red eyes, medium hair, white hair, ahoge
2. /nai <prompt> #<params> 生成一张图片，params为可选参数，参数之间用|分隔，参数格式为key=value
例如: /nai masterpiece, best quality, girl #width=512|height=768|step=28
3. /nai site <url> 设置Colab链接
4. /nai config 查看当前配置
5. /nai cset <key> <value> 设置配置，key为配置名，value为配置值

未来会增加Stable Diffusion等更多功能，敬请期待。
"""

    """
    帮助函数,当用户输入 plugin v 插件名称 时,会调用此函数,返回帮助信息
    返回参数要求(必填): dict{
        "name": str, # 插件名称
        "desc": str, # 插件简短描述
        "help": str, # 插件帮助信息
        "version": str, # 插件版本
        "author": str, # 插件作者
    }
    """        
    def info(self):
        return {
            "name": "NovelAI",
            "desc": "NovelAI支持插件",
            "help": "输入/nai查看帮助",
            "version": "v1.0.1",
            "author": "Soulter"
        }