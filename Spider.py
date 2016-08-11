# coding=utf-8
import re
import urllib2
import sqlite3
import random
import threading
from bs4 import BeautifulSoup
import pymysql
import sys

reload(sys)
sys.setdefaultencoding("utf-8")

# Some User Agents
hds = [{'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'},
       {
           'User-Agent': 'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.12 Safari/535.11'},
       {'User-Agent': 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0)'},
       {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0'},
       {
           'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/44.0.2403.89 Chrome/44.0.2403.89 Safari/537.36'},
       {
           'User-Agent': 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50'},
       {
           'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50'},
       {'User-Agent': 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0'},
       {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1'},
       {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1'},
       {
           'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11'},
       {'User-Agent': 'Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11'},
       {'User-Agent': 'Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11'}]

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Host': 'passport.lianjia.com',
    'Pragma': 'no-cache',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36'
}

home_url = u'http://sh.lianjia.com'
ditiefang_url = u'http://sh.lianjia.com/ditiefang/'
ershoufang_url = u'http://sh.lianjia.com/ershoufang/'
lock = threading.Lock()


class Spider:
    def __init__(self):
        self.siteURL = ditiefang_url
        self.ershoufangURL = ershoufang_url

    def get_line_url(self):
        try:
            req = urllib2.Request(self.siteURL)
            source_code = urllib2.urlopen(req, timeout=10).read()
            plain_text = unicode(source_code)
            soup = BeautifulSoup(plain_text, "html.parser")

        except (urllib2.HTTPError, urllib2.URLError), e:
            print e
            exit(-1)
        except Exception, e:
            print e
            exit(-1)

        lines = soup.find_all(gahref=re.compile("^li[0-9]*$"))
        for line in lines:
            print line.string
            self.get_station_url(line['gahref'])

    def get_station_url(self, lineurl=u'li143685036'):
        url = ditiefang_url + lineurl
        print url
        try:
            req = urllib2.Request(url)
            source_code = urllib2.urlopen(req, timeout=10).read()
            plain_text = unicode(source_code)
            soup = BeautifulSoup(plain_text, "html.parser")

        except (urllib2.HTTPError, urllib2.URLError), e:
            print e
            exit(-1)
        except Exception, e:
            print e
            exit(-1)

        stationurl = soup.find_all(gahref=re.compile("^li[0-9]*s[0-9]*$"))
        for station in stationurl:
            print station['gahref'] + " " + station.string
            self.get_station_info(station['gahref'], station.string)

    def get_station_info(self, station=u'li143685036s100021817', station_name='1号线'):
        url = ditiefang_url + station

        try:
            req = urllib2.Request(url)
            source_code = urllib2.urlopen(req, timeout=10).read()
            plain_text = unicode(source_code)
            soup = BeautifulSoup(plain_text, "html.parser")

        except (urllib2.HTTPError, urllib2.URLError), e:
            print e
            exit(-1)
        except Exception, e:
            print e
            exit(-1)

        d = soup.find(gahref="results_totalpage")
        if d is None:
            station_panigation = soup.find_all(gahref=re.compile("^results_d[0-9]$"))
            for station_url in station_panigation:
                print station_url['href']
                self.get_ditiefang_info(station_url['href'], station_name)

        else:

            total_pages = int(d.string)
            for i in range(total_pages):
                station_url = u"/ditiefang/" + station + "/d%d" % (i + 1)
                print "start spider  %d page" % (i + 1)
                print station_url
                self.get_ditiefang_info(station_url, station_name)
                print "end spider %d page" % (i + 1)


    def get_ditiefang_info(self, url=u'/ditiefang/li143685036s100021810/d1', station_name=u'富锦路站'):
        url = home_url + url
        try:
            req = urllib2.Request(url)
            source_code = urllib2.urlopen(req, timeout=10).read()
            plain_text = unicode(source_code)
            soup = BeautifulSoup(plain_text, "html.parser")
        except (urllib2.HTTPError, urllib2.URLError), e:
            print e
            return
        except Exception, e:
            print e
            return
        info_panel_list = soup.find_all("div", class_="info-panel")
        xiaoqu_url_set = set()
        for info_panel in info_panel_list:
            t = []
            xiaoqu = info_panel.find("div", class_="where")
            xiaoqu_url = xiaoqu.find("a", class_="laisuzhou")
            xiaoqu_url_set.add(xiaoqu_url['href'])
            info_list = xiaoqu.find_all("span")
            house_url = info_panel.find("h2").find("a")

            # for info in info_list:
            # print info.string
            print "community_name : " + info_list[0].string
            print "community_url : " + xiaoqu_url['href']
            print "house_type : " + info_list[1].string
            print "house_area :" + info_list[2].string
            print "house_url :" + house_url['href']

            price_info = info_panel.find("div", class_="col-3")
            price_total = price_info.find("div", class_="price").find("span")
            price_pre = price_info.find("div", class_="price-pre")
            print "price : " + price_total.string
            print "per_price : " + price_pre.string

            label = info_panel.find("div", class_="view-label left")

            tax_label = ""
            key_label = ""

            tax = label.find("span", class_="taxfree-ex")
            key = label.find("span", class_="haskey-ex")
            if tax is not None:
                tax_label = tax.find("span").string.strip()

            if key is not None:
                key_label = key.find("span").string.strip()

            station_lable = label.find("span", class_="fang-subway-ex").find("span").string
            print "station_label : " + station_lable
            print "tax_label : " + tax_label
            print "key_label :" + key_label
            pattern = re.compile(r'\d+')
            m = re.findall(pattern, station_lable)
            print m[1]

            try:
                conn = pymysql.connect(host='localhost', user='root', passwd='root', db='test', port=3306,
                                       charset='utf8')
                cur = conn.cursor()
                # insert record to DB
                sql = "insert into Subway_Room values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                cur.execute(sql, (
                    info_list[0].string, xiaoqu_url['href'], info_list[1].string, house_url['href'],
                    info_list[2].string,
                    price_total.string, price_pre.string, station_lable, tax_label, key_label, str(m[0]) + "号线",
                    station_name, str(m[1])))
                cur.close()
                conn.commit()
                conn.close()
            except pymysql.Error, e:
                print "Mysql Error %d: %s" % (e.args[0], e.args[1])
                print "error in insert "

    def exception_write(fun_name, url):
        lock.acquire()
        f = open('log.txt', 'a')
        line = "%s %s\n" % (fun_name, url)
        f.write(line)
        f.close()
        lock.release()

    def exception_read(self):
        lock.acquire()
        f = open('log.txt', 'r')
        lines = f.readlines()
        f.close()
        f = open('log.txt', 'w')
        f.truncate()
        f.close()
        lock.release()
        return lines

    def getxiaoquurl(self):
        try:
            conn = pymysql.connect(host='localhost', user='root', passwd='root', db='test', port=3306, charset='utf8')
            cur = conn.cursor()
            sql = "select distinct community_url from ErShouFang_room"
            cur.execute(sql)
            for r in cur:
                print self.get_xiaoqu_info(r[0])
            cur.close()
            conn.close()
        except pymysql.Error, e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])
            print "error in insert community "

    def get_xiaoqu_info(self, url=u'/xiaoqu/5011000011256.html'):
        host_url = home_url + url
        print  host_url
        try:
            req = urllib2.Request(host_url)
            source_code = urllib2.urlopen(req, timeout=10).read()
            plain_text = unicode(source_code)
            soup = BeautifulSoup(plain_text, "html.parser")
        except (urllib2.HTTPError, urllib2.URLError), e:
            print e
            return
        except Exception, e:
            print e
            return
        print url
        price = soup.find("div", class_="priceInfo").find("div", class_="item col1").find("span", class_="p")
        infolist = soup.find("div", class_="col-2 clearfix").find_all("span", class_="other")
        position = soup.find("a", class_="actshowMap")['xiaoqu']
        print position

        if price is not None:
            if price.string is not None:
                price_label = price.string.strip()
            else:
                price_label = ""
        else:
            price_label = ""
        print price
        print price_label
        for info in infolist:
            if info is not None:
                print info.string.strip()
        position = position.replace(' ', '').lstrip('[').rstrip(']').split(',')
        print position[0]
        print position[1]
        print position[2].strip('\'')
        try:
            conn = pymysql.connect(host='localhost', user='root', passwd='root', db='test', port=3306, charset='utf8')
            cur = conn.cursor()
            # insert record to DB
            sql = "insert into xiaoqu values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            cur.execute(sql, (
                url, price_label, infolist[0].string.strip(), infolist[1].string.strip(), infolist[2].string.strip(),
                infolist[3].string.strip(), infolist[4].string.strip(), infolist[5].string.strip(),
                infolist[6].string.strip(), infolist[7].string.strip(), position[0], position[1],
                position[2].strip('\'')))
            cur.close()
            conn.commit()
            conn.close()
        except pymysql.Error, e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])
            print "error in insert : " + url

    def getcommunityurl(self):
        try:
            conn = pymysql.connect(host='localhost', user='root', passwd='root', db='test', port=3306, charset='utf8')
            cur = conn.cursor()
            sql = "select community_url from Community"
            cur.execute(sql)
            for r in cur:
                self.getcommunityurl(r[0])
            cur.close()
            conn.close()
        except pymysql.Error, e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])
            print "error in insert community "

    def getcommunityprice(self):
        try:
            conn = pymysql.connect(host='localhost', user='root', passwd='root', db='test', port=3306, charset='utf8')
            cur = conn.cursor()
            sql = "select sum(house_price)/sum(house_area) from test.Subway_room_temp  group by community_url"
            cur.execute(sql)
            for r in cur:
                self.getcommunityprice(r[0], r[1])
            cur.close()
            conn.close()
        except pymysql.Error, e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])
            print "error in insert community "

    def setcommunityprepreice(self, price, url):
        try:
            conn = pymysql.connect(host='localhost', user='root', passwd='root', db='test', port=3306, charset='utf8')
            cur = conn.cursor()
            sql = "update test.community set community_pre_price = %s where community_url = %s"
            cur.execute(sql, (price, url))
            cur.close()
            conn.close()
        except pymysql.Error, e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])
            print "error in insert community "

    def getershoufang(self):
        try:
            req = urllib2.Request(self.ershoufangURL)
            source_code = urllib2.urlopen(req, timeout=10).read()
            plain_text = unicode(source_code)
            soup = BeautifulSoup(plain_text, "html.parser")

        except (urllib2.HTTPError, urllib2.URLError), e:
            print e
            exit(-1)
        except Exception, e:
            print e
            exit(-1)

        div = soup.find("div", class_="option-list")
        lines = div.find_all(gahref=re.compile("^[a-zA-Z]{1,30}$"))

        for line in lines:
            if line.string is not None:
                print line['href']
                self.getershoufangbankuai(line['href'], line.string)

    def getershoufangbankuai(self, bankuai_url, bankuai_name):
        url = home_url + bankuai_url
        print url
        try:
            req = urllib2.Request(url)
            source_code = urllib2.urlopen(req, timeout=10).read()
            plain_text = unicode(source_code)
            soup = BeautifulSoup(plain_text, "html.parser")

        except (urllib2.HTTPError, urllib2.URLError), e:
            print e
            exit(-1)
        except Exception, e:
            print e
            exit(-1)

        div = soup.find("div", class_="option-list sub-option-list")
        lines = div.find_all(gahref=re.compile("^[a-zA-Z0-9]{1,30}$"))

        for line in lines:
            if line.string is not None:
                print line['href'] + line.string
                self.getershoufangquyu(line['href'], line.string, bankuai_name)

    def getershoufangquyu(self, quyu_url, quyu_name, bankuai):
        url = home_url + quyu_url

        try:
            req = urllib2.Request(url)
            source_code = urllib2.urlopen(req, timeout=10).read()
            plain_text = unicode(source_code)
            soup = BeautifulSoup(plain_text, "html.parser")

        except (urllib2.HTTPError, urllib2.URLError), e:
            print e
            exit(-1)
        except Exception, e:
            print e
            exit(-1)

        d = soup.find(gahref="results_totalpage")
        if d is None:
            quyu_panigation = soup.find_all(gahref=re.compile("^results_d[0-9]$"))
            for quyu_url in quyu_panigation:
                print quyu_url['href']
                # self.getditiefanginfo(quyu_url['href'], quyu_name)
                self.getershoufanginfo(quyu_url['href'], quyu_name, bankuai)

        else:

            total_pages = int(d.string)
            if total_pages == 100:
                f = open('log.txt', 'a')
                line = "%s %s\n" % (quyu_url, quyu_name)
                f.write(line)
                f.close()
                for i in range(6):
                    quyu_l_url = quyu_url + "l%d" % (i + 1)
                    self.getershoufangquyu(quyu_l_url, quyu_name, bankuai)
            else:
                for i in range(total_pages):
                    ershoufang_url = quyu_url + "d%d" % (i + 1)
                    print "start spider  %d page" % (i + 1)
                    print ershoufang_url
                    # self.getditiefanginfo(station_url, station_name)
                    self.getershoufanginfo(ershoufang_url, quyu_name, bankuai)
                    print "end spider %d page" % (i + 1)

    def getershoufanginfo(self, ershoufang_url=u'/ershoufang/beicai/d1', bankuai_name=u'浦东', quyu_name=u'北蔡'):
        url = home_url + ershoufang_url
        try:
            req = urllib2.Request(url)
            source_code = urllib2.urlopen(req, timeout=10).read()
            plain_text = unicode(source_code)
            soup = BeautifulSoup(plain_text, "html.parser")
        except (urllib2.HTTPError, urllib2.URLError), e:
            print e
            return
        except Exception, e:
            print e
            return
        info_panel_list = soup.find_all("div", class_="info-panel")
        xiaoqu_url_set = set()
        for info_panel in info_panel_list:
            t = []
            xiaoqu = info_panel.find("div", class_="where")
            xiaoqu_url = xiaoqu.find("a", class_="laisuzhou")
            xiaoqu_url_set.add(xiaoqu_url['href'])
            info_list = xiaoqu.find_all("span")
            house_url = info_panel.find("h2").find("a")

            # for info in info_list:
            # #print info.string
            print "community_name : " + info_list[0].string
            print "community_url : " + xiaoqu_url['href']
            print "house_type : " + info_list[1].string
            print "house_area :" + info_list[2].string
            print "house_url :" + house_url['href']

            price_info = info_panel.find("div", class_="col-3")
            price_total = price_info.find("div", class_="price").find("span")
            price_pre = price_info.find("div", class_="price-pre")
            print "price : " + price_total.string
            print "per_price : " + price_pre.string

            label = info_panel.find("div", class_="view-label left")

            tax_label = ""
            key_label = ""
            station_lable = ""

            tax = label.find("span", class_="taxfree-ex")
            key = label.find("span", class_="haskey-ex")
            station = label.find("span", class_="fang-subway-ex")
            distance = ""
            if tax is not None:
                tax_label = tax.find("span").string.strip()

            if key is not None:
                key_label = key.find("span").string.strip()

            if station is not None:
                station_lable = station.find("span").string
                if station_lable is not None:
                    pattern = re.compile(r'\d+')
                    m = re.findall(pattern, station_lable)
                    distance = m[1]
            print "station_label : " + station_lable
            print "tax_label : " + tax_label
            print "key_label :" + key_label

            try:
                conn = pymysql.connect(host='localhost', user='root', passwd='root', db='test', port=3306,
                                       charset='utf8')
                cur = conn.cursor()
                # insert record to DB
                sql = "insert into ErShouFang_room values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                cur.execute(sql, (
                    info_list[0].string, xiaoqu_url['href'], info_list[1].string, house_url['href'],
                    info_list[2].string,
                    price_total.string, price_pre.string, station_lable, tax_label, key_label, bankuai_name, quyu_name,
                    distance))
                cur.close()
                conn.commit()
                conn.close()
            except pymysql.Error, e:
                print "Mysql Error %d: %s" % (e.args[0], e.args[1])
                print "error in insert "


spider = Spider()
spider.getxiaoquurl()
