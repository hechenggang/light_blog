# coding=utf-8
import sys
sys.path.append('..')
from flask import Flask,request,jsonify,make_response
from flask import Blueprint
from database.session import getSession,User

import random
import time
from tools import string_to_md5

from api.verification import cross
from api.verification import check

# resiger a bluepoint 
bp_api_user = Blueprint('api_user',__name__)

# build apis base on this bluepoint
@bp_api_user.route('/login',methods=['POST','OPTIONS'])
@cross
def login():
    if request.method == 'OPTIONS':
        return ''

    req = request.json

    # 檢查參數是否齊全
    if not(('id' in req) and ('answer' in req) and ('mail' in req) and ('password' in req) and ('timestamp' in req)):
        return jsonify({
            'ok':False,
            'message':'不要非法侵入本站喔。'
        })

    result = check(req=req,delete=True)
    print (result)
    if not result:
        return jsonify({
            'ok':False,
            'message':'你是机器人吗？'
        })

    # 登录逻辑
    return jsonify({
        'ok':True
    })

# build apis base on this bluepoint
@bp_api_user.route('/signup',methods=['POST','OPTIONS'])
@cross
def signup():
    if request.method == 'OPTIONS':
        return ''

    req = request.json

    # 檢查參數是否齊全
    if not(('id' in req) and ('answer' in req) and ('mail' in req) and ('password' in req) and ('timestamp' in req)):
        return jsonify({
            'ok':False,
            'message':'不要非法侵入本站喔。'
        })

    result = check(req=req,delete=True)
    print (result)
    if not result:
        return jsonify({
            'ok':False,
            'message':'你是机器人吗？'
        })

    # 登录逻辑
    return jsonify({
        'ok':True
    })