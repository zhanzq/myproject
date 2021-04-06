#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
Created by liaoyangyang1 on 2018/8/22 下午1:50.
"""
from flask_login import UserMixin,AnonymousUserMixin  #第二课增加内容
from werkzeug.security import check_password_hash, generate_password_hash  #第二课增加内容
from backend.models import db  #第二课增加内容
from backend.views import login_manager #第三课新增
from flask import current_app #第五课内容


class Room(UserMixin, db.Model):  #第二课增加内容
    __tablename__ = 'rooms'  #这是我们将来建出来的表的表名，在这里定义，下面的都是字段名和字段类型长度这些

    room_id = db.Column(db.BigInteger, primary_key=True, autoincrement=False)
    accnt_name = db.Column(db.String(128))   # 用户名
    start_time = db.Column(db.DateTime) # 直播开始时间
    finsh_time = db.Column(db.DateTime) # 直播结束时间
    ttl_per_nm = db.Column(db.Integer)  # 进入直播间总人数
    max_oln_nm = db.Column(db.Integer)  # 最大在线人数
    avg_oln_nm = db.Column(db.Float)    # 平均在线人数
    prd_cmt_nm = db.Column(db.Integer)  # 评论数
    prd_lik_nm = db.Column(db.Integer)  # 点赞数
    inc_fan_nm = db.Column(db.Integer)  # 新增粉丝数
    fan_per_rt = db.Column(db.Float)    # 进粉率=新增粉丝数/进入直播间总人数
    avg_wth_tm = db.Column(db.Time)     # 人均观看时长
    prd_shw_nm = db.Column(db.Integer)  # 商品曝光人数
    prd_clk_nm = db.Column(db.Integer)  # 商品点击人数
    pay_per_nm = db.Column(db.Integer)  # 成交人数
    prd_oln_nm = db.Column(db.Integer)  # 上架商品数
    pay_ord_nm = db.Column(db.Integer)  # 成交订单量
    prd_shw_rt = db.Column(db.Float)    # 商品点击率 = 商品点击人数/商品曝光人数
    pay_per_rt = db.Column(db.Float)    # 曝光转化率 = 成交人数/进入直播间总人数
    pay_prd_nm = db.Column(db.Integer)  # 成交商品数：需要统计有成交量的商品数
    pay_moneys = db.Column(db.Float)    # 成交金额
    person_val = db.Column(db.Float)    # 人均价值 = 成交金额/进入直播间总人数
    ord_per_rt = db.Column(db.Float)    # 订单创建率 = 创建订单数/进入直播间总人数
    ord_pay_rt = db.Column(db.Float)    # 创建成交率 = 成交人数/创建订单数

    def __init__(self, **kwargs): #第五课内容
        super(Room, self).__init__(**kwargs)
        print(self)


class AnonymousUser(AnonymousUserMixin): #第三课新增
    def can(self, _):
        return False

    def is_admin(self):
        return False


login_manager.anonymous_user = AnonymousUser   #第三课新增
