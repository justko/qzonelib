import urllib.request
import urllib.parse
import http.cookiejar
import random
import execjs
import re
import time
import bs4
import json
import Tuling
import demjson

normal_header = {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:56.0) Gecko/20100101 Firefox/56.0"}


class QQ:
    def __init__(self, qq_number, qq_password):
        self.qq_number = qq_number
        self.qq_password = qq_password
        self.login_sig = None
        self.g_tk = None
        self.qzonetoken = None
        self.qq_cookie = http.cookiejar.CookieJar()
        my_handler = urllib.request.HTTPCookieProcessor(self.qq_cookie)
        self.opener = urllib.request.build_opener(my_handler)

    def login(self):
        self.login_sig = self.__get_login_sig()
        verify_code = self.__get_verify_code()
        # Request login
        pt_login = urllib.request.Request(
            url="https://ssl.ptlogin2.qq.com/login?u=" + str(self.qq_number) +
                "&verifycode=" + self.verify_code +
                "&pt_vcode_v1=0"
                "&pt_verifysession_v1=" + self.__get_ptvf_session() +
                "&p=" + self.__get_p(verify_code) +
                "&pt_randsalt=2&pt_jstoken=3670018369"
                "&u1=https%3A%2F%2Fqzs.qq.com%2Fqzone%2Fv5%2Floginsucc.html%3Fpara%3Dizone"
                "&ptredirect=0&h=1&t=1&g=1&from_ui=1&ptlang=2052"
                "&action=4-3-1508039351070&js_ver=10230&js_type=1"
                "&login_sig=" + self.login_sig +
                "&pt_uistyle=40&aid=549000912&daid=5&has_onekey=1&",
            headers=normal_header, method="GET")
        text = self.opener.open(pt_login).read().decode()
        return_value = re.search("ptuiCB\('([0-9])'", text).group(1)
        if return_value != "0":
            print("%s(%s)" % (re.search("'([^0-9,]+)'", text).group(1), return_value))
            exit(255)
        else:
            print("%s登录成功!(0)" % (re.search("'([^']*)'\)", text).group(1)))
        pattern = re.compile("'(http[^']+)'")
        urls = pattern.search(text).group(1)
        self.opener.open(urls)
        self.opener.open("https://qzs.qq.com/qzone/v5/loginsucc.html?para=izone")
        self.g_tk = self.__get_g_tk()
        self.qzonetoken = self.__get_qzonetoken(self.qq_number)

    def logout(self):
        # Three arguments which ara needed
        pt4_token = None
        skey = None
        ptcz = None
        for i in self.qq_cookie:
            if i.name == "pt4_token":
                pt4_token = i.value
            elif i.name == "skey":
                skey = i.value
            elif i.name == "ptcz":
                ptcz = i.value
        skey = QQ.__time33(skey)
        ptcz = QQ.__hash33(ptcz)
        pt_logout = urllib.request.Request(
            url="https://ssl.ptlogin2.qq.com/logout"
                "?pt4_token=" + pt4_token +
                "&pt4_hkey=" + str(skey) +
                "&pt4_ptcz=" + str(ptcz) +
                "&deep_logout=1", headers=normal_header, method="GET")
        content = self.opener.open(pt_logout).read().decode()
        ret = re.search("ret\(([0-9]), '([^']+)'\)", content)
        print("安全从%s退出(%s)" % (ret.group(2), ret.group(1)))

    def feed(self, qq, start, count):
        say = urllib.request.Request(
            "https://h5.qzone.qq.com/proxy/domain/ic2.qzone.qq.com/cgi-bin/feeds/feeds_html_act_all"
            "?uin=" + str(self.qq_number) +
            "&hostuin=" + str(qq) +
            "&scope=0&filter=all&flag=1&refresh=0&firstGetGroup=0"
            "&mixnocache=0&scene=0&begintime=undefined&icServerTime="
            "&start=" + str(start) + "&count=" + str(count) +
            "&sidomain=qzonestyle.gtimg.cn&useutf8=1&outputhtmlfeed=1&refer=2"
            "&r=" + str(random.random()), headers=normal_header)
        text = self.opener.open(say).read().decode()[10:-2]
        return text

    def get_message(self, host_uin, start, num):
        req = urllib.request.Request(
            url="https://user.qzone.qq.com/proxy/domain/m.qzone.qq.com/"
                "cgi-bin/new/get_msgb"
                "?uin=" + str(self.qq_number) +
                "&hostUin=" + str(host_uin) +
                "&start=" + str(start) +
                "&s=" + str(random.random()) +
                "&format=jsonp&num=" + str(num) +
                "&inCharset=utf-8&outCharset=utf-8"
                "&g_tk=" + str(self.g_tk) +
                "&qzonetoken=" + self.qzonetoken,
            headers=normal_header, method="GET")
        return self.opener.open(req).read().decode().strip()[10:-2]

    def add_comment(self, qq, topic_id, content):
        headers = {
            "Host": "h5.qzone.qq.com",
            "Accept-Language": "en-US,en;q=0.5",
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:56.0) Gecko/20100101 Firefox/56.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = urllib.parse.urlencode(
            {"qzreferrer": "https://qzs.qq.com/qzone/app/mood_v6/html/index.html#mood"
                           "&uin=" + str(qq) +
                           "&pfid=2&qz_ver=8&appcanvas=0"
                           "&qz_style=35&params="
                           "&entertime=" + str(time.time()) +
                           "&canvastype=&cdn_use_https=1",
             "uin": self.qq_number,
             "topicId": topic_id,
             "commentUin": self.qq_number,
             "content": content,
             "private": 0,
             "with_fwd": 0,
             "to_tweet": 0,
             "hostuin": self.qq_number,
             "code_version": 1,
             "format": "fs"}).encode("utf-8")
        qzonetoken = self.qzonetoken
        req = urllib.request.Request(
            url="https://h5.qzone.qq.com"
                "/proxy/domain/taotao.qzone.qq.com"
                "/cgi-bin/emotion_cgi_addcomment_ugc"
                "?g_tk=" + str(self.g_tk) + "&qzonetoken=" + qzonetoken,
            headers=headers, method="POST"
        )
        self.opener.open(req, data=data)

    def del_comment(self, qq, topic_id, comment_id):
        headers = {
            "Host": "h5.qzone.qq.com",
            "Accept-Language": "en-US,en;q=0.5",
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:56.0) Gecko/20100101 Firefox/56.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = urllib.parse.urlencode(
            {"qzreferrer": "https://qzs.qq.com/qzone/app/mood_v6/html/index.html#mood"
                           "&uin=" + str(qq) +
                           "&pfid=2&qz_ver=8&appcanvas=0"
                           "&qz_style=35&params="
                           "&entertime=" + str(time.time()) +
                           "&canvastype=&cdn_use_https=1",
             "uin": self.qq_number,
             "hostUin": qq,
             "topicId": topic_id,
             "commentId": comment_id,
             "hostuin": self.qq_number,
             "code_version": 1,
             "format": "fs"}).encode("utf-8")
        qzonetoken = self.qzonetoken
        req = urllib.request.Request(
            url="https://h5.qzone.qq.com"
                "/proxy/domain/taotao.qzone.qq.com"
                "/cgi-bin/emotion_cgi_delcomment_ugc"
                "?g_tk=" + str(self.g_tk) + "&qzonetoken=" + qzonetoken,
            headers=headers, method="POST"
        )

        result = self.opener.open(req, data=data).read().decode()

        ret_json = json.loads(QQ.__extract_mid_callback(result))

        return ret_json["message"] + "(" + str(ret_json["code"]) + ")"

    def add_reply(self, host_uin, topic_id, comment_id, comment_uin, content):
        headers = {
            "Host": "h5.qzone.qq.com",
            "Accept-Language": "en-US,en;q=0.5",
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:56.0) Gecko/20100101 Firefox/56.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = urllib.parse.urlencode(
            {"qzreferrer": "https://qzs.qq.com/qzone/app/mood_v6/html/index.html#mood"
                           "&uin=" + str(host_uin) +
                           "&pfid=2&qz_ver=8&appcanvas=0"
                           "&qz_style=35&params="
                           "&entertime=" + str(time.time()) +
                           "&canvastype=&cdn_use_https=1",
             "uin": self.qq_number,
             "hostUin": host_uin,
             "topicId": topic_id,
             "commentId": comment_id,
             "commentUin": comment_uin,
             "content": "@{uin:" + str(comment_uin) + ",nick:ko,auto:1}" + content,
             "private": 0,
             "hostuin": self.qq_number,
             "code_version": 1,
             "format": "fs"}).encode("utf-8")
        qzonetoken = self.qzonetoken
        req = urllib.request.Request(
            url="https://h5.qzone.qq.com"
                "/proxy/domain/taotao.qzone.qq.com"
                "/cgi-bin/emotion_cgi_addreply_ugc"
                "?g_tk=" + str(self.g_tk) + "&qzonetoken=" + qzonetoken,
            headers=headers, method="POST"
        )

        result = self.opener.open(req, data=data).read().decode()

        ret_json = json.loads(QQ.__extract_mid_callback(result))

        return ret_json["message"] + "(" + str(ret_json["code"]) + ")"

    def get_feeds_count(self):
        """
        :return: myFeeds_new_cnt, the number of new feeds about me
        res is a json like string.
        {
            code:'0',
            subcode:'0',
            message:'operation success',
            data:{
                aboutHostFeeds_new_cnt:0,
                replyHostFeeds_new_cnt:0,
                myFeeds_new_cnt:0,
                friendFeeds_new_cnt:0,
                friendFeeds_newblog_cnt:0,
                friendFeeds_newphoto_cnt:0,
                specialCareFeeds_new_cnt:0,
                followFeeds_new_cnt:0,
                newfeeds_uinlist:[]
            }
        }
        """
        req = urllib.request.Request(
            url="https://user.qzone.qq.com/proxy/domain/ic2.qzone.qq.com"
                "/cgi-bin/feeds/cgi_get_feeds_count.cgi"
                "?uin=" + str(self.qq_number) +
                "&rd=" + str(random.random()) +
                "&g_tk=" + str(self.g_tk) +
                "&qzonetoken=" + self.qzonetoken, headers=normal_header)
        res = self.opener.open(req).read().decode().strip()[9:-1]
        return demjson.decode(res)['data']['myFeeds_new_cnt']

    def re_feeds(self, host_uin, topic_id, comment_id, comment_uin, this_comment_uin, content):
        data = urllib.parse.urlencode(
            {"qzreferrer": "https://user.qzone.qq.com/" + str(self.qq_number),
             "topicId": topic_id,
             "feedsType": 102,
             "inCharset": "utf-8",
             "outCharset": "utf-8",
             "plat": "qzone",
             "source": "ic",
             "hostUin": host_uin,
             "platformid": 52,
             "uin": self.qq_number,
             "format": "fs",
             "ref": "feeds",
             "content": "@{uin:" + str(this_comment_uin) + ",nick:ko,atuo:1}" + content,
             "commentId": comment_id,
             "commentUin": comment_uin,
             "private": 0,
             "paramstr": 1
             }).encode("utf-8")
        req = urllib.request.Request(
            url="https://user.qzone.qq.com/proxy/domain/taotao.qzone.qq.com"
                "/cgi-bin/emotion_cgi_re_feeds?"
                "g_tk=" + str(self.g_tk) +
                "&qzonetoken=" + self.qzonetoken,
            headers=normal_header)
        self.opener.open(req, data=data)

    def right(self):
        home_page = open("./home.html", 'r')
        qzonetoken = None
        token_pattern = re.compile("g_qzonetoken[^\"]*\"([^\"]*)\"")
        line = home_page.readline()
        while line:
            token = token_pattern.search(line)
            line = home_page.readline()
            if token is not None:
                qzonetoken = token.group(1)
                break

        # https://user.qzone.qq.com/proxy/domain/r.qzone.qq.com/cgi-bin/right_frame.cgi
        # ?uin=905920365&param=3_905920365_0%7C14_905920365%7C8_8_905920365_0_1_0_0_1%7C10%7C11%7C12%7C13_1%7C17%7C20%7C9_0_8_1%7C18
        # &g_tk=2119447006
        # &qzonetoken=cdf391de16e99ed0d29508897f7a0c49f0df4ff6e25856fc9588b1c05d71d53be6ca9a433ccf9c56
        right_url = "https://user.qzone.qq.com/proxy/domain/r.qzone.qq.com/cgi-bin/right_frame.cgi" \
                    "?uin=" + str(self.qq_number) + \
                    "&param=3_" + str(self.qq_number) + \
                    "_0|14_" + str(self.qq_number) + \
                    "|8_8_" + str(self.qq_number) + \
                    "_0_1_0_0_1|10|11|12|13_0|17|20|9_0_8_1|19" \
                    "&g_tk=" + str(self.g_tk) + \
                    "&qzonetoken=" + qzonetoken
        print(right_url)
        right_frame = urllib.request.Request(url=right_url, headers=normal_header)
        r = self.opener.open(right_frame).read().decode()
        print(r)

    def do_like(self, unikey, curkey, how=True):
        """DOLIKE or UNLIKE a user's feed identified by unikey and curkey,
        unikey and curkey are same if this feed was originally created by he"""
        headers = {
            "Host": "user.qzone.qq.com",
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:56.0) Gecko/20100101 Firefox/56.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Content-Type": "application/x-www-form-urlencoded", }
        data = urllib.parse.urlencode({
            "qzreferrer": "https://user.qzone.qq.com/" + str(self.qq_number),
            "opuin": self.qq_number,
            "unikey": unikey,
            "curkey": curkey,
            "from": 1,
            "appid": 311,
            "typeid": 0,
            "abstime": int(time.time()),
            "fid": "6d3fff35c5d3ce59843d0b00",
            "active": 0,
            "fupdate": 1}).encode(encoding='utf-8')
        op = "dolike" if how else "unlike"
        unlike_url = urllib.request.Request(
            url="https://user.qzone.qq.com/proxy/domain/"
                "w.qzone.qq.com/cgi-bin/likes/"
                "internal_" + op + "_app?g_tk=" + str(self.g_tk) +
                "&qzonetoken=" + self.qzonetoken,
            headers=headers, method="POST")
        self.opener.open(unlike_url, data=data)


    def auto_reply(self, offset=0, count=1):
        """
        回复从最近数第offset条开始，回复count条
        也就是，回复[offset,offset+count)条
        :param offset:
        :param count: The number of feeds
        :return:
        """
        feeds_pav_all = self.__get_feeds_pav_all(offset=offset, count=count)
        html = re.compile("html:'([^']+)'")
        index = 0
        for i in range(count):
            comment_html = html.search(feeds_pav_all, index)
            if comment_html is None:
                break
            index = comment_html.end()
            comment_html = comment_html.group(1).strip()
            try:
                comment_list = QQ.__process_comment_list(comment_html)
            except (TypeError, KeyError):
                continue
            comment_last = comment_list.comment_all[-1]
            dog = Tuling.Tuling()
            #
            #
            #
            answer = dog.answer(user_id=comment_last.comment_uin,
                                question=comment_last.comment_content)
            #
            #
            self.re_feeds(host_uin=comment_list.host_uin,
                          topic_id=comment_list.topic_id,
                          comment_uin=comment_list.comment_all[0].comment_uin,
                          comment_id=comment_list.comment_all[0].comment_id,
                          this_comment_uin=comment_last.comment_uin,
                          content=answer)

    def watch_dog(self,times=10,sleep_time=5):
        for i in range(times):
            count = self.get_feeds_count()
            print(count)
            if count > 0:
                self.auto_reply(0, count=count)
            time.sleep(seconds=sleep_time)



    @staticmethod
    def __extract_mid_callback(text):
        return re.search("callback\(({[^;]+})\);", text).group(1)

    def __get_g_tk(self):
        p_skey = None
        for i in self.qq_cookie:
            if i.name == "p_skey":
                p_skey = i.value
                break
        num = 5381
        for i in range(len(p_skey)):
            num += (num << 5) + ord(p_skey[i])
        return num & 2147483647

    @staticmethod
    def __hash33(o):
        t = 0
        for e in range(len(o)):
            t += (t << 5) + ord(o[e])
        return 2147483647 & t

    @staticmethod
    def __time33(o):
        t = 0
        for e in range(len(o)):
            t = 33 * t + ord(o[e])
        return t % 4294967296

    def __get_login_sig(self):
        login_sign_url = urllib.request.Request(
            url="https://xui.ptlogin2.qq.com/cgi-bin/xlogin"
                "?proxy_url=https%3A//qzs.qq.com/qzone/v6/portal/proxy.html"
                "&daid=5&&hide_title_bar=1&low_login=0"
                "&qlogin_auto_login=1"
                "&no_verifyimg=1&link_target=blank&appid=549000912"
                "&style=22&target=self"
                "&s_url=https%3A%2F%2Fqzs.qzone.qq.com%2Fqzone%2Fv5%2Floginsucc.html%3Fpara%3Dizone%26from%3Diqq"
                "&pt_qr_app=" + urllib.parse.quote("手机") + "Q" + urllib.parse.quote("空间") +
                "&pt_qr_link=http%3A//z.qzone.com/download.html"
                "&self_regurl=https%3A//qzs.qq.com/qzone/v6/reg/index.html"
                "&pt_qr_help_link=http%3A//z.qzone.com/download.html&pt_no_auth=0", headers=normal_header)
        self.opener.open(login_sign_url)
        for i in self.qq_cookie:
            if i.name == "pt_login_sig":
                return i.value
        raise RuntimeError("pt_login_sig Not Found")

    def __get_verify_code(self):
        check_req = urllib.request.Request(
            url="https://ssl.ptlogin2.qq.com/check?regmaster="
                "&pt_tea=2&pt_vcode=1&uin=" + str(self.qq_number) +
                "&appid=549000912&js_ver=10230&js_type=1"
                "&login_sig=" + self.login_sig +
                "&u1=https%3A%2F%2Fqzs.qq.com%2Fqzone%2Fv5%2Floginsucc.html%3Fpara%3Dizone"
                "&r=" + str(random.random()) +
                "&pt_uistyle=40&pt_jstoken=3670018369", headers=normal_header, method="GET")
        content = self.opener.open(check_req).read()
        if content[14] != 0x30:
            raise RuntimeError("Need Verification!")
        self.verify_code = content[18:22].decode()
        return self.verify_code

    def __get_ptvf_session(self):
        # Get ptvfsession in cookie
        for i in self.qq_cookie:
            if i.name == "ptvfsession":
                return i.value
        return None

    def __get_p(self, verify_code):
        # Get p by Javascript
        encryption_js = open("./Encryption.js", 'r')
        text = ""
        line = encryption_js.readline()
        while line:
            text += line
            line = encryption_js.readline()
        encryption_js.close()
        ctx = execjs.compile(text)
        p = ctx.call("en", self.qq_number, self.qq_password, verify_code)
        return p

    def __show_cookie(self):
        for i in self.qq_cookie:
            print("%s:%s" % (i.name, i.value))

    def __get_qzonetoken(self, qq):
        headers = {"Host": "user.qzone.qq.com",
                   "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:56.0) Gecko/20100101 Firefox/56.0",
                   "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                   "Accept-Language": "en-US,en;q=0.5",
                   "Referer": "https://qzs.qq.com/qzone/v5/loginsucc.html?para=izone"}
        req = urllib.request.Request(
            url="https://user.qzone.qq.com/" + str(qq), headers=headers)
        page = self.opener.open(req).read().decode()
        qz_pattern = re.compile("g_qzonetoken[^\"]+\"([0-9a-z]+)\"")
        return qz_pattern.search(page).group(1)

    def __get_feeds_pav_all(self, offset, count):
        req = urllib.request.Request(
            url="https://user.qzone.qq.com/proxy/domain/ic2.qzone.qq.com"
                "/cgi-bin/feeds/feeds2_html_pav_all?uin=" + str(self.qq_number) +
                "&begin_time=0&end_time=0&getappnotification=1&getnotifi=1&has_get_key=0"
                "&offset=" + str(offset) +
                "&set=0"
                "&count=" + str(count) +
                "&useutf8=1&outputhtmlfeed=1"
                "&grz=" + str(random.random()) +
                "&scope=1"
                "&g_tk=" + str(self.g_tk) +
                "&qzonetoken=" + self.qzonetoken, headers=normal_header)
        return self.opener.open(req).read().decode()

    @staticmethod
    def __process_comment_item(comment_item):
        try:
            comment_uin = comment_item["data-uin"]
            comment_id = comment_item["data-tid"]
            comment_content_item = comment_item.find("div", attrs={"class": "single-reply"}).find("div", attrs={
                "class": "comments-content"})
            comment_content = ""
            for i in comment_content_item:
                if i.name is None:
                    comment_content += i.strip()
            comment_content = comment_content[3:].strip()
            return Comment(comment_uin=comment_uin, comment_id=comment_id, comment_content=comment_content)
        except:
            print("这不是一个comment_item")
            raise

    # @staticmethod
    # def process_pav_all(text):
    #     pav_all = demjson.decode_file("pav_all.json")
    #     comment_html = pav_all["data"]["data"][0]["html"].strip()
    #     c0 = FeedComment.process_pav_one(comment_html=comment_html)
    @staticmethod
    def __process_comment_list(comment_html):
        """translate the comment html to CommentBlock
        :param comment_html: The structured comment html.
        :return: a CommentList instance
        """
        comment_html = comment_html.replace("\\x3C", '<')
        comment_html = comment_html.replace("\\x22", "\"")
        comment_html = comment_html.replace("\\/", "/")
        comment_soup = bs4.BeautifulSoup(comment_html, "html.parser")
        try:
            feed_data = comment_soup.find("i", attrs={"name": "feed_data"})
            host_uin = feed_data["data-uin"]
            topic_id = feed_data["data-topicid"]
            mod_comments = comment_soup.find("div", attrs={"class": "mod-comments"})
            comment_root = mod_comments.find("li", attrs={"data-type": "commentroot"})
            comment_all = [QQ.__process_comment_item(comment_root)]
            comment_item_container = comment_root.find("div", attrs={"class": "comments-list"})
            if comment_item_container is not None:
                comment_items = comment_item_container.find_all("li")
                for i in comment_items:
                    comment_all.append(QQ.__process_comment_item(i))
            return CommentBlock(host_uin=host_uin, topic_id=topic_id, comment_all=comment_all)
        except:
            print("这不是一个comment html")
            raise


class Comment:
    """
    ---------------------------------
    |Host UIN & Topic ID            |
    |"Today is Sunday!!"            |
    |-------------------------------|
    |   Comment Root                |     ->    Comment
    |       Comment Reply           |     ->    Comment
    |       Comment Reply           |     ->    Comment
    |       Comment Reply           |     ->    Comment
    |-------------------------------|
    |   Comment Root                |     ->    Comment
    |       Comment Reply           |     ->    Comment
    |       Comment Reply           |     ->    Comment
    ---------------------------------

    """

    def __init__(self, comment_uin, comment_id, comment_content):
        self.comment_uin = comment_uin
        self.comment_id = comment_id
        self.comment_content = comment_content

    def __str__(self):
        return str.format("%d(%d):%s" % (self.comment_uin, self.comment_id, self.comment_content))


class CommentBlock:
    """
    ---------------------------------
    |Host UIN & Topic ID            |
    |"Today is Sunday!!"            |
    |-------------------------------|
    |   Comment Root                |\          This is "comment_all",
    |       Comment Reply           | \____>        "CommentBlock" is a "comment_all" with
    |       Comment Reply           | /                 host UIN and topic ID
    |       Comment Reply           |/
    |-------------------------------|
    |   Comment Root                |\
    |       Comment Reply           | ---->     And also this one.
    |       Comment Reply           |/
    ---------------------------------
    ---------------------------------------------------------------------------------
    """

    def __init__(self, host_uin, topic_id, comment_all):
        self.host_uin = host_uin
        self.topic_id = topic_id
        self.comment_all = comment_all

    def __str__(self):
        return str.format("Host UIN:%d\nTopic ID:%s\n%s"
                          % (self.host_uin, self.topic_id,
                             "\n".join([str(i) for i in self.comment_all])))


class Message:
    def __init__(self):
        pass


if __name__ == "__main__":
    ko = QQ(1216789457, "12589qq")
    ko.login()
    ko.watch_dog()
    ko.logout()
