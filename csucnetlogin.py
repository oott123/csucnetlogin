#!/usr/bin/env python2.6
#coding=utf-8
# -*- coding: utf-8 -*-

"""
csucnetlogin 中国电信数字中南登录脚本
author : oott123
via : https://github.com/oott123/csucnetlogin
"""
import rsa
import httplib
import sys
import json
import ConfigParser
import binascii

config = ConfigParser.ConfigParser()
configfilename = 'config.ini'
config.read(configfilename)

# 密码加密
base = [str(x) for x in range(10)] + [ chr(x) for x in range(ord('A'),ord('A')+6)]

def dec2bin(string_num):
    num = int(string_num)
    mid = []
    while True:
        if num == 0: break
        num,rem = divmod(num, 2)
        mid.append(base[rem])
    result =  ''.join([str(x) for x in mid[::-1]])
    while len(result)<8:
        result = "0"+result
    return result
def dec2hex(string_num):
    num = int(string_num)
    mid = []
    while True:
        if num == 0: break
        num,rem = divmod(num, 16)
        mid.append(base[rem])
    return ''.join([str(x) for x in mid[::-1]])

def encrypted_pwd(pwd):
    n = 118412968095593089696003595256943158860853473161415576733447804842301571568757172298177752975532992898222036246641653221445506569501197901613520593964333398062725892226386301624234776784458736053884120766450015009923516265683635605497451865069151546715184399574358971886504430854133607074276246210978427253829
    e = 65537
    pwd = str(pwd)[::-1]
    pwd_ascii_list = map(lambda x:ord(x),pwd)
    bin_chain_pwd = ''.join(dec2bin(x) for x in pwd_ascii_list)
    return dec2hex(pow(int(bin_chain_pwd,2),e,n)).lower()


###### 使用方法概述 ######
if len(sys.argv) <= 1 or not sys.argv[1] in ('login','logout'):
	usage = """======= ChinaNet-CSU login script =======
usage: %s login|logout""" % sys.argv[0]
	print usage
	sys.exit(1)

###### 配置相关 ######

if sys.argv[1] == 'login':
	if not config.has_section('user'):
		print "Welcome. It seems this is the first time you use this script."
		print "Please follow a simple guide to set your user data."
		config.add_section('user')
		config.write(open(configfilename,'w'))
	if config.has_option('user','username'):
		username = config.get('user','username',True)
	else:
		print "Input your username:",
		username = raw_input()
		username = username.rstrip()
		#保存配置信息
		config.set('user','username',username)
		config.write(open(configfilename,'w'))
	if config.has_option('user','password'):
		password = config.get('user','password',True)
	else:
		print "Input your secret:",
		password = raw_input()
		password = password.rstrip()
		password = encrypted_pwd(password)
		#保存配置信息
		config.set('user','password',password)
		config.write(open(configfilename,'w'))
else:
	#登出
	if not (config.has_option('user','bas') and config.has_option('user','wlanuserip')) :
		print "It seems that you haven't login with this script. It can't logout for you if you haven't login with this."
		sys.exit(2)

###### 判断用户是否登录 ######

#202.108.22.5为百度首页，这里为了获取IP而进行连接
#
print "Checking your login status ... "
conn = httplib.HTTPConnection("202.108.22.5")
conn.request('HEAD', '/')
res = conn.getresponse()
conn.close()
#print "HTTP code:",res.status	#HTTP code: 302
#print "HTTP headers:",res.getheaders()	#HTTP headers: [('location', 'http://61.137.86.87:8080/portalNat444/AccessServices/bas.59df7586?wlanuserip=10.96.10.12&wlanacname='), ('server', 'NetEngine Server 1.0'), ('pragma', 'No-Cache'), ('allow', 'GET,POST,HEAD'), ('mime-version', '1.0')]

#检查登录状态
if res.status == 302:
	loginstatus = -1
	location = res.getheader('location','')
	#print "HTTP Location:",location
	#HTTP Location: http://61.137.86.87:8080/portalNat444/AccessServices/bas.59df7586?wlanuserip=10.96.10.12&wlanacname=
	bas = location[location.rfind('/bas.')+len('/bas.'):location.rfind('?')]	#59df7586
	wlanuserip = location[location.rfind('wlanuserip=')+len('wlanuserip='):location.rfind('&')]	#10.96.10.12
	print "bas:",bas,"wlanuserip:",wlanuserip
else:
	loginstatus = 1

if sys.argv[1] == 'login' and loginstatus > 0:
	print "It seems that you are already logged in."
	sys.exit(4)
if sys.argv[1] == 'logout' and loginstatus < 0:
	print "It seems that you are already logged out."
	sys.exit(5)

if sys.argv[1] == 'login' :
	#登录
	#保存配置信息
	print "Please wait while login ... "
	login = httplib.HTTPConnection("61.137.86.87",8080)
	postData = 'accountID=%s%%40zndx.inter&password=%s&brasAddress=%s&userIntranetAddress=%s' % (username,password,bas,wlanuserip)
	#print "postData:",postData
	postHeader = {"Host": "61.137.86.87",
		"User-Agent": "Mozilla/5.0 (Windows NT 6.1; rv:21.0) Gecko/20100101 Firefox/21.0",
		"Referer": "http://61.137.86.87:8080/portalNat444/index.jsp",
		'Accept': 'application/json, text/javascript, */*; q=0.01',
		'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8',
		'X-Requested-With': 'XMLHttpRequest'}
	login.request('POST', '/portalNat444/AccessServices/login',postData,postHeader)
	loginRes = login.getresponse()
	loginJson = loginRes.read()
	#print loginJson
	loginJson = json.loads(loginJson)
	if int(loginJson['resultCode']) > 0 :
		print "Login failed."
		sys.exit(int(loginJson['resultCode']))
	percentage = int(loginJson['usedflow'])/(int(loginJson['totalflow'])+0.1)*100
	if percentage > 99 :
		percentage = 100
	if percentage < 1 :
		percentage = 0
	width = 79
	usedSymbols = int(percentage*width/100)
	unusedSymbols = width - int(percentage*width/100)
	print "Used:" , int(int(loginJson['usedflow'])/1024) , "G /" , int(int(loginJson['totalflow'])/1024) , "G (" , int(percentage) , "%)"
	print ">" * usedSymbols + '-' * unusedSymbols
	config.set('user','bas',bas)
	config.set('user','wlanuserip',wlanuserip)
	config.write(open(configfilename,'w'))
	login.close()
else:
	#退出
	print "Please wait while logout ... "
	bas = config.get('user','bas')
	wlanuserip = config.get('user','wlanuserip')
	login = httplib.HTTPConnection("61.137.86.87",8080)
	postData = 'brasAddress=%s&userIntranetAddress=%s' % (bas,wlanuserip)
	#print "postData:",postData
	postHeader = {"Host": "61.137.86.87",
		"User-Agent": "Mozilla/5.0 (Windows NT 6.1; rv:21.0) Gecko/20100101 Firefox/21.0",
		"Referer": "http://61.137.86.87:8080/portalNat444/main2.jsp",
		'Accept': 'application/json, text/javascript, */*; q=0.01',
		'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8',
		'X-Requested-With': 'XMLHttpRequest'}
	login.request('POST', '/portalNat444/AccessServices/logout',postData,postHeader)
	loginRes = login.getresponse()
	loginJson = loginRes.read()
	#print loginJson
	loginJson = json.loads(loginJson)
	if int(loginJson['resultCode']) > 0 :
		print "Logout failed."
		sys.exit(int(loginJson['resultCode']))
	login.close()
	print "Logged out."
	config.remove_option('user','bas')
	config.remove_option('user','wlanuserip')
	config.write(open(configfilename,'w'))

