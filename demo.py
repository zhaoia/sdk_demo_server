# -*- encoding=utf8 -*-
#
# zhaoia api example (Python)
# http://www.zhaoia.com/api
# This script is for study and communication.
#
# Test platform: Ubuntu-9.10-x86-desktop-python2.6-Firefox3.6.10

# facebook open source web server tornado-1.0 download url:
# http://pypi.python.org/simple/tornado/
# wget "http://pypi.python.org/packages/source/t/tornado/tornado-1.0.tar.gz"
# tar xf tornado-1.0.tar.gz
# cd tornado-1.0
# sudo python setup.py install

import os
import sys
import pdb
import json
import urllib
import urllib2
try:
  from hashlib import md5
except:
  import md5
try:
    import tornado.httpserver
    import tornado.ioloop
    import tornado.web
    import tornado.options
    from tornado.options import define, options
except:
    print "import tornado failed.Please see:"
    print """
    facebook open source web server tornado-1.0 download url:
    http://pypi.python.org/simple/tornado/
    run below command in the terminal:
        $ cd /tmp
        $ wget "http://pypi.python.org/packages/source/t/tornado/tornado-1.0.tar.gz"
        $ tar xf tornado-1.0.tar.gz
        $ cd tornado-1.0
        $ sudo python setup.py install
    run this script again
    """
    sys.exit(0)

# API url: http://www.zhaoia.com/service/
ZHAOIA_ROOT = 'http://www.zhaoia.com/service/'

class ZhaoiaAPI(object):

    # *********************** Note this *******************
    # Mail to api@hellom2.com to ask for app_key and secret_code
    # *****************************************************
    app_key = '29286397' # ****************************************
    secret_code = '78cf14f220bdffa07e' # ************************************
    # *****************************************************

    # get data from api service must pass a argument named sign
    @staticmethod
    def get_sign(params):
        # src is like "appkey=test1&keyword=dell&page=1&per_page=10&sort=&secretcode=1qaz1234"
        src = '&'.join(["%s=%s" % (k, v) for k, v in sorted(params.iteritems())]) + "&secretcode="+ZhaoiaAPI.secret_code
        return md5(src).hexdigest().upper()

    # get data from api service
    # secretcode must be not in params
    @staticmethod
    def get_results(url,params):
        # pass sign
        params['sign'] = ZhaoiaAPI.get_sign(params)
        form_data = urllib.urlencode(params)
        return urllib2.urlopen(url,form_data).read()

    @staticmethod
    def get_product_lists(keyword,page=1,per_page=16,sort=''):
        url = ZHAOIA_ROOT+"get_product_lists"
        params = {
            'appkey':ZhaoiaAPI.app_key,
            'keyword':keyword,
            'page':page,
            'per_page':per_page,
            'sort':sort
            }
        return ZhaoiaAPI.get_results(url,params)

    @staticmethod
    def get_product_info(id):
        url = ZHAOIA_ROOT+"get_product_info"
        params = {
            'appkey':ZhaoiaAPI.app_key,
            'id':id
            }
        return ZhaoiaAPI.get_results(url,params)

    @staticmethod
    def get_related_product_lists(id,lsize=8):
        url = ZHAOIA_ROOT+"get_related_product_lists"
        params = {
            'appkey':ZhaoiaAPI.app_key,
            'id':id,
            'lsize':lsize
            }
        return ZhaoiaAPI.get_results(url,params)

    @staticmethod
    def get_context_product_lists(keyword,url,lsize=8):
        url = ZHAOIA_ROOT+"get_context_product_lists"
        params = {
            'appkey':ZhaoiaAPI.app_key,
            'keyword':keyword,
            'url':url,
            'lsize':lsize
            }
        return ZhaoiaAPI.get_results(url,params)

CWD = os.path.dirname(os.path.realpath(__file__))
class APIDemo(tornado.web.RequestHandler):

    def get(self, pat):
        if pat == "search":
            keyword = self.get_argument("keyword")
            page = 1
            try:
                page = int(self.get_argument("page",default="1"))
            except:
                pass
            per_page = 16
            try:
                per_page = int(self.get_argument("per_page",default="16"))
            except:
                pass
            sort = self.get_argument("sort",default="")
            try:
                ret = json.loads(ZhaoiaAPI.get_product_lists(keyword,page,per_page,sort))
            except Exception,err:
                self.write(str(err))
            else:
                if "error" in ret:
                    self.write("%s %s" % ("error",ret["error"]))
                else:
                    total_rows = ret["total_rows"]
                    product_lists = ret["product_lists"]
                    self.render(os.path.join(CWD,'product_lists.html'),keyword=keyword,total_rows=total_rows,product_lists=product_lists,page=page,per_page=per_page)
        elif pat == "detail":
            pid = self.get_argument("id")
            ret = json.loads(ZhaoiaAPI.get_product_info(pid))
            if "error" in ret:
                self.write("%s %s" % ("error",ret["error"]))
            else:
                relas = json.loads(ZhaoiaAPI.get_related_product_lists(pid))
                self.render(os.path.join(CWD,'product_detail.html'),product=ret,relas=relas)

class Home(tornado.web.RequestHandler):
    def get(self):
        self.render(os.path.join(CWD,'home.html'))

def main():

    define("host",default="0.0.0.0",type=str)
    define("port",default=8888,type=int)
    tornado.options.parse_command_line()
    settings = {
            "static_path":CWD
            }
    application = tornado.web.Application([
        (r'/?',Home),
        (r'/(search)/?',APIDemo),
        (r'/(detail)/?',APIDemo),
    ], **settings)
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.bind(options.port,options.host)
    http_server.start(1)
    print "Start tornado IOloop."
    print "http://%s:%d" % (options.host, options.port)
    try:
        tornado.ioloop.IOLoop.instance().start()
    except:
        print "Quit from tornado IOloop."
        sys.exit(0)

if __name__ == '__main__':

    # run this script : python demo.py or python demo.py --host=127.0.0.1 --port=8888
    # http://localhost:8888/search/?keyword=apple&page=1&per_page=10
    # if you want to run the examples, comment main()
    main()

    # examples
    # search keyword=dell, page number=6, 10 products per page
    print ZhaoiaAPI.get_product_lists('dell',page=6, per_page=10)
    # get product detail info by product id
    print ZhaoiaAPI.get_product_info('85f286c812340d61c727a427bd527566')
    # get related products by product id, lsize is the size of result
    print ZhaoiaAPI.get_related_product_lists('85f286c812340d61c727a427bd527566',lsize=6)
    # get products which relates by the url or keyword
    print ZhaoiaAPI.get_context_product_lists('Canon 佳能 EOS 500D 单反相机','http://www.newegg.com.cn/Product/90-c13-193.htm')

