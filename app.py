#coding:utf-8
import os
import time
import datetime
import json
import hashlib
import functools
from flask import Flask,render_template,request,jsonify,make_response,redirect,url_for
from sqlalchemy import Column, String, Integer, create_engine, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


# 创建 Flask 实例
app = Flask(__name__)
# 创建 SQLAlchemy 实例
Base = declarative_base()
# 创建继承自 SQLAlchemy 数据库模型的数据表抽象层，包含数据字段和自定义的方法

class User(Base):
    __tablename__ = 'user'
    user_id = Column(String(50), primary_key=True)
    username = Column(String)
    password = Column(String)
    token = Column(String)
    config = Column(String)

    def to_dict(input):
        # 把单个查询结果转换成字典
        def item_to_dict(item):
            one = {}
            one['user_id'] = item.user_id
            one['username'] = item.username
            one['config'] = json.loads(item.config)
            # one['token'] = item.token
            # one['password'] = item.password
            return one
        # 如果传入的查询结果的类型为 User 类
        if type(input) == User:
            return item_to_dict(input)
        else:
            output = []
            for item in input:
                output.append(item_to_dict(item))
            return output

class Article(Base):
    __tablename__ = 'article'
    _id = Column(String(50), primary_key=True)
    title = Column(String)
    user_id = Column(String)
    author = Column(String)
    brief = Column(String)
    content = Column(String)
    timestamp = Column(Integer)
    viewcount = Column(Integer) 
    auth = Column(String)

    def to_dict(input):
        # 把单个查询结果转换成字典
        def item_to_dict(item):
            one = {}
            one['_id'] = item._id
            one['user_id'] = item.user_id
            one['author'] = item.author
            one['title'] = item.title
            one['brief'] = item.brief
            one['content'] = item.content
            one['timestamp'] = item.timestamp
            one['viewcount'] = item.viewcount
            one['auth'] = item.auth
            return one
        # 如果传入的查询结果的类型为 User 类
        if type(input) == User:
            return item_to_dict(input)
        else:
            output = []
            for item in input:
                output.append(item_to_dict(item))
            return output

# 取得 Sqlite 数据库文件的绝对地址
db_abspath = os.path.abspath('./database.db')
# 初始化数据库连接:
engine = create_engine('sqlite:///'+db_abspath,connect_args={'check_same_thread':False})
# 检查并创建表
Base.metadata.create_all(engine)
# 创建DBSession类型:
DBSession = sessionmaker(bind=engine)


############################## 基础方法
# 通过 token 和 userid 鉴权
def auth_by_cookies(f):
    @functools.wraps(f)
    def dec(**kwargs):
        cookies = request.cookies
        if ('token' in cookies) and ('user_id' in cookies):
            def authorized():
                user_id = cookies['user_id']
                token = cookies['token']
                session = DBSession()
                user = session.query(User.user_id).filter(User.user_id == user_id).first()
                session.close()
                if not user:
                    return render_template('index/404.html'),404
                attrs = {"user_id":user_id,"token":token,"kwargs":kwargs}
                return f(attrs)
            return authorized()

        else:
            def unauthorized():
                return render_template('index/401.html'),401
            return unauthorized()
    return dec


# 为反馈添加跨域头部
def resp_cross(resp):
    resp = make_response(resp)
    resp.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    # resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Allow-Methods'] = '*'
    return resp


# 将字符串混合时间戳进行 md5 编码
def md5_string(string=time.time(),mix=False):
    string = str(string)
    if mix:
        srting = str(time.time()) + string
    return hashlib.md5(string.encode(encoding='UTF-8')).hexdigest()

###################################################### 可视化页面
## 主页：使用 Vue 和 Vue-router 提供主页，登录页和注册页的展示
@app.route('/')
def page_index():
    return make_response(render_template('index/index.html'))


## 用户页：使用 Vue 和 Vue-router 提供用户主页，用户博文，搜索等的展示
@app.route('/b/<username>')
def page_blog(username):
    if 3 < len(username) < 20:
        session = DBSession()
        query = session.query(User.config,User.user_id).filter(User.username == username).first()
        session.close()
        if query:
            config = json.loads(query[0])
            config['username'] = username
            config['user_id'] = query[1]
            return render_template('themes/{0}/index.html'.format(config['theme']),config=config)
        else:
            return redirect(url_for('page_index'))
    else:
        return redirect(url_for('page_index'))


## 用户页：使用 Vue 和 Vue-router 提供用户主页，用户博文，搜索等的展示
@app.route('/b/<username>/admin')
@auth_by_cookies
def page_blog_admin(attrs):
    user_id = attrs['user_id']
    session = DBSession()
    query = session.query(User.config,User.username,User.user_id).filter(User.user_id == user_id).first()
    session.close()
    if not query:
        return resp_cross(jsonify({"ok":False,"message":"用户已存在"})),403
    output = json.loads(query[0])
    output['username'] = query[1]
    output['user_id'] = query[2]
    return render_template('themes/{0}/admin.html'.format(output['theme']),config = output)


###################################################### 接口
######################### 公开接口

# 接口：用户注册
@app.route('/api/user.new',methods=['POST'])
def api_user_new():
    username = request.json['username']
    password = request.json['password']
    # 检查用户名和密码长度
    if not (3 < len(password) < 20 and 3 < len(username) < 20) :
        return resp_cross(jsonify({"ok":False,"message":"账号或密码长度不正确"})),500
    # 检查用户是否存在
    session = DBSession()
    user = session.query(User.user_id).filter(User.username == username).first()
    if user:
        return resp_cross(jsonify({"ok":False,"message":"用户已存在"})),403
    
    # 若检查通过
    # 准备新用户数据
    user_id = md5_string(string = username,mix=True)
    password = md5_string(string = password)
    token = md5_string(string = password + username,mix=True)
    config = {
        "blog_name":username,
        "theme":"base",
        "icon_url":"/static/picture/default_user_icon.png"
    }
    config = json.dumps(config)
    # 写入数据库
    user = User(user_id = user_id,username = username,password = password, config=config, token = token)
    session.add(user)
    session.commit()
    session.close()
    return resp_cross(jsonify({"ok":True,"message":"注册成功"}))


# 接口：登录后返回cookies
@app.route('/api/user.login',methods=['POST'])
def api_user_auth():
    username = request.json['username']
    password = request.json['password']
    # 检查用户名和密码长度
    if not (3 < len(password) < 20 and 3 < len(username) < 20) :
        return resp_cross(jsonify({"ok":False,"message":"账号或密码长度不正确"}))
    # 检查用户是否存在
    session = DBSession()
    user = session.query(User.password,User.user_id,User.token).filter(User.username == username).first()
    if not user:
        return resp_cross(jsonify({"ok":False,"message":"用户不存在"})),404
    # 检查密码是否匹配
    if not (md5_string(password) == user.password):
        return resp_cross(jsonify({"ok":False,"message":"账号与密码不匹配"})),401
    # 若检查通过
    resp = jsonify({"ok":True,"data":{"username":username,"token":user.token,"user_id":user.user_id}})
    return resp_cross(resp)

# 查询自己的账户信息
@app.route('/api/user.info/<username>',methods=['GET'])
def api_user_info(username):
    session = DBSession()
    query = session.query(User.config,User.username).filter(User.username == username).first()
    session.close()
    if not query:
        return resp_cross(jsonify({"ok":False})),404
    output = json.loads(query[0])
    output['username'] = query[1]
    resp = jsonify({"ok":True,"data":output})
    return resp_cross(resp)

# 接口：获取自己的文章列表
@app.route('/api/articles/<user_id>',methods=['GET'])
def api_delete_article_by_ariticle_id(user_id):
    # 用用户id找到所有由这个id创建的文章
    session = DBSession()
    results = session.query(Article._id,Article.title,Article.brief,Article.timestamp).filter(Article.user_id == user_id).order_by(Article.timestamp.desc()).all()
    session.close()
    return resp_cross(jsonify({"ok":True,"data":results}))


# 接口：通过 ID 获取文章
@app.route('/api/article.one/<_id>',methods=['GET'])
def api_article_by_id(_id):
    if not _id:
        return resp_cross(jsonify({"ok":False})),404
    session = DBSession()
    article = session.query(Article).filter(Article._id == _id).one()
    article.viewcount = int(article.viewcount) + 1
    article = {
        '_id':article._id,
        'title':article.title,
        'user_id':article.user_id, 
        'author':article.author,
        'brief':article.brief,
        'content':article.content,
        'timestamp':article.timestamp,
        'viewcount':article.viewcount}
    session.commit()
    session.close()
    return resp_cross(jsonify({"ok":True,"data":article}))


######################### 受保护接口 
# 查询自己的账户信息
@app.route('/api/user.detail',methods=['GET'])
@auth_by_cookies
def api_user_detail(attrs):
    user_id = attrs['user_id']
    session = DBSession()
    user = session.query(User).filter(User.user_id == user_id).first()
    # 统计文章数量
    output = User.to_dict(input=user)
    total = session.query(func.count(Article._id)).filter(Article.user_id == user_id).all()
    total = total[0][0]
    output['total'] = total
    # 统计阅读数量
    viewcount = session.query(func.sum(Article.viewcount)).filter(Article.user_id == user_id).all()
    session.close()
    viewcount = viewcount[0][0]
    output['viewcount'] = viewcount
    resp = jsonify({"ok":True,"data":output})
    return resp_cross(resp)


# 更新自己的账户配置
@app.route('/api/user.config',methods=['POST'])
@auth_by_cookies
def api_user_config_post(attrs):
    user_id = attrs['user_id']
    session = DBSession()
    user = session.query(User).filter(User.user_id == user_id).first()
    # 把用户的配置更新
    user_config = json.loads(user.config)
    data = json.loads(request.json)
    user_config['blog_name'] = data['config']['blog_name']
    user.config = json.dumps(user_config)
    session.commit()
    session.close()
    return resp_cross(jsonify({"ok":True}))


# 删除自己的账户
@app.route('/api/user.delete',methods=['GET'])
@auth_by_cookies
def api_user_delete(attrs):
    user_id = attrs['user_id']
    session = DBSession()
    user = session.query(User).filter(User.id == user_id).one()
    session.delete(user)
    session.commit()
    session.close()
    resp = jsonify({"ok":True,"message":"删除成功"})
    return resp_cross(resp)


# 接口：新建文章
@app.route('/api/article.new',methods=['POST'])
@auth_by_cookies
def api_article_new(attrs):
    user_id = attrs['user_id']
    # 接收数据
    _id = md5_string()
    data = json.loads(request.json)
    title = data['title']
    author = data['author']
    brief = data['brief']
    content = data['content']
    auth = data['auth']
    # 方便前端，这里使用13位时间戳
    timestamp = str(time.time()).replace('.','')[0:13]
    viewcount = 0
    session = DBSession()
    # 整理数据，写入数据库
    article = Article(_id=_id,title=title,user_id=user_id, author=author,brief=brief,content=content,timestamp=timestamp,auth=auth,viewcount=viewcount)
    session.add(article)
    session.commit()
    session.close()
    return resp_cross(jsonify({"ok":True,"message":"保存成功"}))

# 接口：更新文章
@app.route('/api/article.update',methods=['POST'])
@auth_by_cookies
def api_article_update(attrs):
    user_id = attrs['user_id']
    # 接收数据
    data = json.loads(request.json)
    # 用id找到文章
    _id = data['_id']
    session = DBSession()
    article = session.query(Article).filter(Article._id == _id).first()
    # 如果文章所属用户和token所属用户不一致
    if str(article.user_id) != str(user_id):
        return resp_cross(jsonify({"ok":False})),401

    # 更新数据
    article.title = data['title']
    article.author = data['author']
    article.brief = data['brief']
    article.content = data['content']
    article.auth = data['auth']
    session.commit()
    session.close()
    return resp_cross(jsonify({"ok":True,"message":"更新成功"}))
    



# 接口：删除自己的文章
@app.route('/api/article.delete/<id>',methods=['GET'])
@auth_by_cookies
def api_articles_by_user_id(attrs):
    _id = attrs['kwargs']['id']
    if not _id:
        return resp_cross(jsonify({"ok":False})),404
    session = DBSession()
    article = session.query(Article).filter(Article._id == _id).one()
    session.delete(article)
    session.commit()
    session.close()
    return resp_cross(jsonify({"ok":True}))



# 错误处理
@app.errorhandler(500)
def error_500(e):
    return render_template('index/500.html'),500

@app.errorhandler(404)
def error_404(e):
    return render_template('index/404.html'),404


if __name__ == '__main__':
    app.run(threaded=True,debug=True,host='0.0.0.0',port=8080)