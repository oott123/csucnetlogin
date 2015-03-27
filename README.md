# csucnetlogin

中国电信数字中南（中南大学校园网）Python登录器

## 怎么获取“secret”

现在只需要直接输入你的数字中南帐号即可。

密码会加密保存，但请注意这并不安全；任何获取了你的加密后密码的人均可轻松登录你的数字中南帐号，所以请保护好你的 `config.ini`。

## 怎么用

./csucnetlogin.py [login|logout]

第一次使用会自动引导初始化。

## 为什么要写这个脚本

给不想开桌面/开不了桌面/开了桌面却无法打开浏览器的同学使用……

## 为什么是py2.6

因为 yum 是 Python2.6 写的，而我最喜欢的发行版本就是 CentOS。

*该脚本在 Python 2.7 下也能运行良好。*
