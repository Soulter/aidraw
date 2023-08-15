# QQChannelChatGPT——AIDraw

## 目前支持的模型

- NovelAI（Naifu）

## 安装方法
 
`plugin i 本插件github地址`

## Naifu部署

链接：https://colab.research.google.com/drive/1_Ma71L6uGbtt6UQyA3FjqW2lcZ5Bjck-

也可在本地部署NovelAI。


## 使用方法

1. /nai <prompt> 生成一张图片
例如：/nai masterpiece, best quality, girl, red eyes, medium hair, white hair, ahoge
2. /nai <prompt> #<params> 生成一张图片，params为可选参数，参数之间用逗号分隔，参数格式为key=value
例如: /nai masterpiece, best quality, girl #width=512,height=768,step=28
3. /nai site <url> 设置后端链接
4. /nai config 查看当前配置
5. /nai cset <key> <value> 设置配置，key为配置名，value为配置值

未来会增加Stable Diffusion等更多功能，敬请期待。