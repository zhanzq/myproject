#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
Created by liaoyangyang1 on 2018/8/22 上午9:40.
"""
from flask import Blueprint,request,render_template,jsonify,flash  #第二课增加内容
from flask import redirect,url_for,abort #第五课新增
from backend.models.UserModel import User,Role #第五课新增
from backend.models.RoomModel import Room #第五课新增
from backend.models import db
from flask_login import login_user,login_required,logout_user,current_user #第三课增加内容 #第五课新增
from functools import wraps #第五课新增
from backend.models.UserModel import Permission #第五课新增
from utils.layout import layout
from sqlalchemy import func, desc
import pdb

#账户的蓝图  访问http://host:port/account 这个链接的子链接，都会跳到这里
pv = Blueprint('pv', __name__)  #第二课增加内容


def permission_required(permission): #第五课新增
    """Restrict a view to users with the given permission."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# 要求管理员权限
def admin_required(f): #第五课新增
    return permission_required(Permission.ADMINISTER)(f)


@pv.route('/query', methods=(["GET", "POST"]))
@login_required
def room_list(): #第五课新增
    form = None
    if request.method == "POST":
        form = request.form #获取登录表单
    else:
        return layout('/pv/query.html', captions=[], rooms=[])

    dct ={
       "room_id"   :  [Room.room_id  , "直播间ID"],
       "ttl_per_nm":  [Room.ttl_per_nm, "进入直播间总人数"],
       "max_oln_nm":  [Room.max_oln_nm, "最大在线人数"],
       "avg_oln_nm":  [Room.avg_oln_nm, "平均在线人数"],
       "prd_cmt_nm":  [Room.prd_cmt_nm, "评论数"],
       "prd_lik_nm":  [Room.prd_lik_nm, "点赞数"],
       "inc_fan_nm":  [Room.inc_fan_nm, "新增粉丝数<"],
       "fan_per_rt":  [Room.fan_per_rt, "进粉率"],
       "avg_wth_tm":  [Room.avg_wth_tm, "人均观看时长"],
       "prd_shw_nm":  [Room.prd_shw_nm, "商品曝光人数"],
       "prd_clk_nm":  [Room.prd_clk_nm, "商品点击人数"],
       "pay_per_nm":  [Room.pay_per_nm, "成交人数"],
       "prd_oln_nm":  [Room.prd_oln_nm, "上架商品数"],
       "pay_ord_nm":  [Room.pay_ord_nm, "成交订单量"],
       "prd_shw_rt":  [Room.prd_shw_rt, "商品点击率"],
       "pay_per_rt":  [Room.pay_per_rt, "曝光转化率"],
       "pay_prd_nm":  [Room.pay_prd_nm, "成交商品数"],
       "pay_moneys":  [Room.pay_moneys, "成交金额"],
       "person_val":  [Room.person_val, "人均价值"],
       "ord_per_rt":  [Room.ord_per_rt, "订单创建率"],
       "ord_pay_rt":  [Room.ord_pay_rt, "创建成交率"]
    }
    s_option = request.values.getlist("s_option")
    captions = ["用户名"]
    names = [Room.accnt_name]
    room_lst = []
    if "query" in form:
        for s in s_option:
            names.append(dct[s][0])
            captions.append(dct[s][1])
        room_lst = Room.query.with_entities(*names).filter().all()
    elif "compare" in form:
        for s in s_option:
            if s == "room_id":
                continue
            names.append(func.avg(dct[s][0]))
            captions.append(dct[s][1])
        room_lst = Room.query.with_entities(*names).group_by(Room.accnt_name).all()
    # pdb.set_trace()
    return layout('/pv/query.html', captions=captions, rooms=room_lst)


@pv.route('/detail', methods=(["GET", "POST"]))
@login_required
def room_detail(): #第五课新增
    # pdb.set_trace()
    room_id = request.values.get('id')
    details = Room.query.filter(Room.id == room_id).all()
    return layout('/pv/detail.html', infos=details)


@pv.route('/deluser')
@login_required
def user_del(): #第五课新增
    try:
        id = request.values.get('id')
        user = User.query.filter(User.id == id).first()
        db.session.delete(user)
        db.session.commit()
        flash('删除用户成功！', 'success')
    except Exception as e:
        print(e)
        flash('删除用户失败！', 'error')

    return redirect(url_for(request.args.get('next') or 'account.user_list'))


