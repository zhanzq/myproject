# encoding=utf-8
# Copyright 2019 Lenovo(Beijing) Technologies Co.,LTD.
# Smart Education Engine Team, All Rights Reserved.
# Author: Coco Gao
# Date: 2020/12/17 下午4:52
# Email: gaojh4@lenovo.com
# Description: upload bea packages automatically.

import pdb
import json
import requests
import time
from backend.models import db
from backend.models.RoomModel import Room

class DouYin:
    def __init__(self):
        self.en2cn = {
            "flow_stats": "流量",
            "avg_online_uv": "平均在线人数",
            'avg_watch_duration': "平均观看时长",
            'fans_avg_watch_duration': "粉丝平均观看时长",
            'max_online_uv': "最高在线人数",
            'rt_online_uv': "null",
            'watch_pv': "直播间观看人数",
            'watch_uv': "直播间观看次数",

            "interaction_stats": "互动",
            'comment_num': "直播间评论数",
            'incr_fans_num': "新增粉丝数",
            'like_num': "直播间点赞数",
            'share_num': "直播间分享次数",

            "live_status": "null",

            "order_stats": "成交",
            'fans_pay_in_live_gmv_ratio': "支付订单金额粉丝占比",
            'fans_pay_in_live_num_ratio': "支付订单量粉丝占比",
            'pay_in_live_gmv': "支付订单金额",
            'pay_in_live_num': "支付订单量",
            'pay_in_live_num_ratio': "支付订单量率",

            "product_stats": "用户",
            'click_uv': "商品点击人数",
            'fans_click_uv_ratio': "null",
            'fans_pay_in_live_uv_ratio': "直播期间成交人数粉丝占比",
            'fans_show_uv_ratio': "null",
            'pay_in_live_uv': "直播期间成交人数",
            'show_uv': "商品曝光人数",

            "create_time": "开始时间",
            "finish_time": "结束时间",
            "watch_pv_entrance_show": "直播间观看人次",
            "click_pv_entrance": "购物车点击次数",
            "click_pv_product": "商品点击次数",
            "pay_gmv": "抖店成交金额",
            "room_id": "直播间ID",
        }

        self.en2cn = {}

        self.agent = None
        self.cookie = None
        self.header = {}
        self.set_header()
        self.user_name = ""
        self.rooms = {}

    def set_cookie(self, cookie):
        self.cookie = cookie

    def set_agent(self, agent):
        self.agent = agent

    def set_header(self):
        self.header = {
            "cookie": self.cookie,
            "user-agent": self.agent
        }

    def get_room_ids(self):
        """ get room_id, start_time and finish_time
            room_id = db.Column(db.BigInteger, primary_key=True, autoincrement=False)
        """
        # date_type = 21/23/24 分别表示最近7/30/90天的信息
        base = "https://compass.jinritemai.com/business_api/author/live_detail/history_live?date_type=24&page_no=1"

        home_page = base + "&page_size=1"
        resp = requests.get(home_page, headers=self.header)
        data = json.loads(resp.content)["data"]
        room_num = data["page_result"]["total"]

        url = base + "&page_size=%d" % room_num
        time.sleep(1)
        resp = requests.get(url, headers=self.header)
        data = json.loads(resp.content)["data"]
        rooms = data["data_result"]
        for room in rooms:
            room_id = int(room["operation"]["live_id"])
            obj = self.rooms.get(room_id, {})
            obj["room_id"] = room_id
            self.rooms[room_id] = obj
            break
        print(self.rooms)

    def get_room_details(self):
        """ get room detail information
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
            person_val = db.Column(db.Float)    # 人均价值 = 成交金额/进入直播间总人数
        """

        base = "https://compass.jinritemai.com/business_api/author/live_detail/live_room/dashboard?live_room_id="
        for room_id in self.rooms:
            obj = self.rooms[room_id]
            url = base + str(room_id)
            time.sleep(1)
            resp = requests.get(url, headers=self.header)
            data = json.loads(resp.content)["data"]
            tmp_obj = {}
            for key in data:
                lst = data[key]
                for item in lst:
                    name = item["index_display"]
                    val = item["value"]["value"]
                    tmp_obj[name] = val

            obj["ttl_per_nm"] = tmp_obj["累计观看人数"]
            obj["max_oln_nm"] = tmp_obj["最高在线人数"]
            obj["avg_oln_nm"] = tmp_obj["平均在线人数"]
            obj["prd_cmt_nm"] = tmp_obj["评论次数"]
            obj["prd_lik_nm"] = tmp_obj["点赞次数"]
            obj["inc_fan_nm"] = tmp_obj["新增粉丝数"]
            obj["avg_wth_tm"] = tmp_obj["人均看播时长"]
            obj["prd_shw_nm"] = tmp_obj["商品曝光人数"]
            obj["prd_clk_nm"] = tmp_obj["商品点击人数"]
            obj["pay_per_nm"] = tmp_obj["成交人数"]
            obj["prd_oln_nm"] = tmp_obj["带货商品数"]
            obj["pay_ord_nm"] = tmp_obj["成交订单数"]
            obj["fan_per_rt"] = 1.0*tmp_obj["新增粉丝数"]/(tmp_obj["累计观看人数"] + 0.00001)
            obj["prd_shw_rt"] = 1.0*tmp_obj["商品点击人数"]/(tmp_obj["商品曝光人数"] + 0.00001)
            obj["pay_per_rt"] = 1.0*tmp_obj["成交人数"]/(tmp_obj["累计观看人数"] + 0.00001)
            obj["person_val"] = 1.0*obj["pay_moneys"]/(obj["ttl_per_nm"] + 0.00001)

            self.rooms[room_id] = obj
        print(self.rooms)

    def get_pay_money(self):
        """
            start_time = db.Column(db.DateTime) # 直播开始时间
            finsh_time = db.Column(db.DateTime) # 直播结束时间
            pay_moneys = db.Column(db.Float)    # 成交金额
        :return:
        """
        base = "https://compass.jinritemai.com/business_api/author/live_detail/live_room/base_info?live_room_id="
        for room_id in self.rooms:
            obj = self.rooms[room_id]
            url = base + str(room_id)
            time.sleep(1)
            resp = requests.get(url, headers=self.header)
            data = json.loads(resp.content)["data"]
            tm_len = len("2021/03/09 18:04")
            if len(data["start_time"]) == tm_len:
                data["start_time"] += ":00"
            if len(data["end_time"]) == tm_len:
                data["end_time"] += ":00"
            obj["start_time"] = data["start_time"]
            obj["finsh_time"] = data["end_time"]
            obj["pay_moneys"] = data["gmv"]["value"]

            self.rooms[room_id] = obj
        print(self.rooms)

    def get_order_rate(self):
        """
            ord_per_rt = db.Column(db.Float)    # 订单创建率 = 创建订单数/进入直播间总人数
            ord_pay_rt = db.Column(db.Float)    # 创建成交率 = 成交人数/创建订单数
        :return:
        """
        base = "https://compass.jinritemai.com/business_api/author/live_detail/live_room/flow_trans?live_room_id="
        for room_id in self.rooms:
            obj = self.rooms[room_id]
            url = base + str(room_id)
            time.sleep(1)
            resp = requests.get(url, headers=self.header)
            data = json.loads(resp.content)["data"]
            order_num = data["create_order_ucnt"]
            obj["ord_per_rt"] = 1.0*order_num/(obj["ttl_per_nm"] + 0.00001)
            obj["ord_pay_rt"] = 1.0*obj["pay_per_nm"]/(order_num + 0.00001)

            self.rooms[room_id] = obj
        print(self.rooms)

    def get_pay_product_num(self):
        """
            pay_prd_nm = db.Column(db.Integer)  # 成交商品数：需要统计有成交量的商品数
        :return:
        """
        base = "https://compass.jinritemai.com/business_api/author/live_detail/live_room/product/list?&index_selected=pay_order_product_cnt&live_room_id="
        for room_id in self.rooms:
            obj = self.rooms[room_id]
            url = base + str(room_id) + "&page_size=1&page_no=0"
            time.sleep(1)
            resp = requests.get(url, headers=self.header)
            data = json.loads(resp.content)["data"]
            product_num = data["page_result"]["total"]

            # get the sold number of all products
            _url = base + "%d&page_no=0&page_size=%d" % (room_id, product_num)
            time.sleep(1)
            _resp = requests.get(_url, headers=self.header)
            _data = json.loads(_resp.content)["data"]
            sold_num = 0
            product_lst = _data["data_result"]
            for product in product_lst:
                if int(product["pay_order_product_cnt"]) > 0:
                    sold_num += 1

            obj["pay_prd_nm"] = sold_num

            self.rooms[room_id] = obj
        print(self.rooms)

    def encNum(self, mobile):
        mp = {
            '0': '35', '1': '34', '2': '37',
            '3': '36', '4': '31', '5': '30',
            '6': '33', '7': '32', '8': '3d',
            '9': '3c', '+': '2e'
        }
        res = ""
        for ch in mobile:
            res += mp[ch]

        return res

    def cookie2String(self, cookie_json):
        lst = []
        for k in cookie_json:
            v = cookie_json[k]
            lst.append("%s=%s;" % (k, v))
        return " ".join(lst)

    def login(self, mobile, mix_mode=1, tp=3732, aid=1128):
        enc_mobile = self.encNum(mobile)
        url = "https://open.douyin.com/oauth/send_code/?mix_mode=%d&mobile=%s&type=%d&aid=%d" % (
            mix_mode, enc_mobile, tp, aid)
        requests.get(url)
        scope = "mobile,user_info,video.create,video.data"
        code = input()
        enc_code = self.encNum(code)
        auth = "https://open.douyin.com/oauth/sms/authorize/?\
mix_mode=1&code=%s&mobile=%s&scope=%s&type=3732\
&from=web&client_key=aw7tduvjdk1a0x3r&aid=1128" % (enc_code, enc_mobile, scope)
        print("url2: %s" % auth)

        resp2 = requests.get(auth, headers=None)
        obj2 = json.loads(resp2.content)
        ticket = obj2["data"]["ticket"]

        uri = "https://fxg.jinritemai.com/account/page/service/login?"
        redir = "https://open.douyin.com/oauth/authorize/?\
client_key=%s&scope=%s&redirect_uri=%s&state=douyin&ticket=%s\
&response_type=code&type=27&from=web" % (1111, scope, uri, ticket)
        resp3 = requests.get(redir, headers=None)

        url4 = resp3.url
        resp4 = requests.get(url4, headers=None)

        url5 = "https://fxg.jinritemai.com/passport/web/account/info/?aid=1574"
        resp5 = requests.get(url5, headers=None)

        url6 = "https://fxg.jinritemai.com/passport/web/auth/login_only/"
        data = {
            'fp': 'verify_4439a5b10b1b258ac012f4f8bc873345',
            'aid': '1574',
            'language': 'zh',
            'account_sdk_source': 'web',
            'platform': 'aweme_v2',
            'platform_app_id': '1080',
            'need_mobile': '1',
            'code': '0ba24d0d41e3275dJe8hekxfe0uqhCWZH7xU'
        }
        resp6 = requests.post(url6, data=data)

    def get_user_name(self, ):
        url = "https://compass.jinritemai.com/business_api/home/user_basic_info"
        resp = requests.get(url, headers=self.header)
        obj = json.loads(resp.content)["data"]
        self.user_name = obj["name"]

    def insert_rooms(self, ):
        for room_id in self.rooms:
            room = self.rooms[room_id]
            room_i = Room.query.filter_by(room_id=room_id).first()
            if room_i is None:
                room_i = Room(room_id=room_id)
                room_i.avg_wth_tm = time.strftime("%H:%M:%S", time.gmtime(room["avg_wth_tm"]))  # 人均观看时长
                room_i.start_time = room["start_time"]  # 直播开始时间
                room_i.finsh_time = room["finsh_time"]  # 直播结束时间
                room_i.accnt_name = self.user_name      # 用户名
                room_i.ttl_per_nm = room["ttl_per_nm"]  # 进入直播间总人数
                room_i.max_oln_nm = room["max_oln_nm"]  # 最大在线人数
                room_i.prd_cmt_nm = room["prd_cmt_nm"]  # 评论数
                room_i.prd_lik_nm = room["prd_lik_nm"]  # 点赞数
                room_i.inc_fan_nm = room["inc_fan_nm"]  # 新增粉丝数
                room_i.prd_shw_nm = room["prd_shw_nm"]  # 商品曝光人数
                room_i.prd_clk_nm = room["prd_clk_nm"]  # 商品点击人数
                room_i.pay_per_nm = room["pay_per_nm"]  # 成交人数
                room_i.prd_oln_nm = room["prd_oln_nm"]  # 上架商品数
                room_i.pay_ord_nm = room["pay_ord_nm"]  # 成交订单量
                room_i.pay_prd_nm = room["pay_prd_nm"]  # 成交商品数：需要统计有成交量的商品数
                room_i.avg_oln_nm = room["avg_oln_nm"]  # 平均在线人数
                room_i.fan_per_rt = room["fan_per_rt"]  # 进粉率=新增粉丝数/进入直播间总人数
                room_i.prd_shw_rt = room["prd_shw_rt"]  # 商品点击率 = 商品点击人数/商品曝光人数
                room_i.pay_per_rt = room["pay_per_rt"]  # 曝光转化率 = 成交人数/进入直播间总人数
                room_i.pay_moneys = room["pay_moneys"]  # 成交金额
                room_i.person_val = room["person_val"]  # 人均价值 = 成交金额/进入直播间总人数
                room_i.ord_per_rt = room["ord_per_rt"]  # 订单创建率 = 创建订单数/进入直播间总人数
                room_i.ord_pay_rt = room["ord_pay_rt"]  # 创建成交率 = 成交人数/创建订单数

                db.session.add(room_i)
                db.session.commit()
            else:
                pass


def get_room_info():
    douyin = DouYin()
    agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) \
Chrome/89.0.4389.82 Safari/537.36}"
    # buyin_cookie = "passport_csrf_token_default=0782d0514a45920bd649ecc98448d1f0; passport_csrf_token=0782d0514a45920bd649ecc98448d1f0; sessionid_ss=3d10b43e415ff312117feb551446ea04; ttwid=1%7CesV67iar9ovzHp-XgvYDBKaC9ZIvQnJWP7FA5CgIO0k%7C1616493230%7Cb1a955f0c0de1d1dd81b30d3abe073bc20cb12db86f86dff9b8377a7e7d10836; n_mh=rGpPpq_Ww6H75B7cKlg3fwgNqAcvUaybo7I3hLFONWc; uid_tt_ss=c475f94d27a871a854022533967e0169; gftoken=M2QxMGI0M2U0MXwxNjE2NDkzMzg1ODl8fDAGBgYGBgY; ttcid=36549d6074c440c5b0ec7b46ae5fe1cb35; MONITOR_WEB_ID=83ca31ae-5cea-481a-96b2-6608acc73169; buyin_shop_type=24; buyin_app_id=1128; uid_tt=c475f94d27a871a854022533967e0169; sid_tt=3d10b43e415ff312117feb551446ea04; sessionid=3d10b43e415ff312117feb551446ea04; passport_auth_status=ffeed020583c162817566d543a73fdfe%2C62f44c050e38741460cda05787ec8ca0; passport_auth_status_ss=ffeed020583c162817566d543a73fdfe%2C62f44c050e38741460cda05787ec8ca0; sid_guard=3d10b43e415ff312117feb551446ea04%7C1616493481%7C5184000%7CSat%2C+22-May-2021+09%3A58%3A01+GMT; odin_tt=18526d450f5bd738d5ced1fbfc6d4e245cc56e69b04786309a79885110311030da2666e05c2318d9e228ec9c640dfc6c192c55a0fc668006a1770d2d2bbe4b01; SASID=SID2_3471393321237250716; BUYIN_SASID=SID2_3471393321237250716; s_v_web_id=verify_kmluhe38_oB2F9ycc_RI7j_4VH5_AaeW_pHZxR9bCJb9o; gfpart_1.0.0.3847_49293=0; tt_scid=DepOkgx1rTrnHEYqrqHOc7WhtA0GYsROOxSo3yOY6nTQ-GQs7qhDoucZ0pnS-iXMe744"
    compass_cookie = "passport_csrf_token_default=0782d0514a45920bd649ecc98448d1f0; passport_csrf_token=0782d0514a45920bd649ecc98448d1f0; sessionid_ss=3d10b43e415ff312117feb551446ea04; ttwid=1%7CesV67iar9ovzHp-XgvYDBKaC9ZIvQnJWP7FA5CgIO0k%7C1616493230%7Cb1a955f0c0de1d1dd81b30d3abe073bc20cb12db86f86dff9b8377a7e7d10836; n_mh=rGpPpq_Ww6H75B7cKlg3fwgNqAcvUaybo7I3hLFONWc; uid_tt_ss=c475f94d27a871a854022533967e0169; uid_tt=c475f94d27a871a854022533967e0169; sid_tt=3d10b43e415ff312117feb551446ea04; sessionid=3d10b43e415ff312117feb551446ea04; passport_auth_status=ffeed020583c162817566d543a73fdfe%2C62f44c050e38741460cda05787ec8ca0; passport_auth_status_ss=ffeed020583c162817566d543a73fdfe%2C62f44c050e38741460cda05787ec8ca0; sid_guard=3d10b43e415ff312117feb551446ea04%7C1616493481%7C5184000%7CSat%2C+22-May-2021+09%3A58%3A01+GMT; odin_tt=18526d450f5bd738d5ced1fbfc6d4e245cc56e69b04786309a79885110311030da2666e05c2318d9e228ec9c640dfc6c192c55a0fc668006a1770d2d2bbe4b01; BUYIN_SASID=SID2_3471393321237250716; gfpart_1.0.0.691_48136=0; gfsitesid=M2QxMGI0M2U0MXwxNjE2NzQ2NTQ0NTV8fDkxNDQ0MzMxNDkzNDA4NwgICAgICAgI; gftoken=M2QxMGI0M2U0MXwxNjE2NzQ2NTQ0NTV8fDAGBgYGBgY; MONITOR_WEB_ID=389b47d0-7920-4813-a063-0e55223bde51; LUOPAN_DT=session_6945043657770696990; Hm_lvt_45173f3eae0174bc5b02a4973fe5a872=1616746545,1617020272; Hm_lpvt_45173f3eae0174bc5b02a4973fe5a872=1617036337"
    douyin.set_cookie(cookie=compass_cookie)
    douyin.set_agent(agent=agent)
    douyin.set_header()
    douyin.get_user_name()
    print(douyin.user_name)
    douyin.get_room_ids()
    douyin.get_pay_money()
    douyin.get_room_details()
    douyin.get_pay_product_num()
    douyin.get_order_rate()
    douyin.insert_rooms()

