#!/usr/bin/python 
#coding=utf-8
import sys,re
import Queue
import urllib2
import gzip
import logging
from StringIO import StringIO
from bs4 import BeautifulSoup
from urllib2 import Request, urlopen, URLError, HTTPError

config={"url":"http://www.baidu.com","depth":1}
ques=[]
urlhash=[]

logger = logging.getLogger('push')
logger.setLevel(logging.DEBUG)
#ch = logging.StreamHandler()
ch = logging.FileHandler("spider.log")
ch.setLevel(logging.DEBUG)
fm = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch.setFormatter(fm)
logger.addHandler(ch)

def crawlone(url,curdepth):
    #print url
    req = urllib2.Request(url)
    req.add_header('Accept-encoding','gzip')
    try:
        res = urllib2.urlopen(req)
        #有的网站数据是经过gzip压缩的，如qq.com,sina.com.cn等
        contentType = res.info().get('Content-Type')
        if contentType:
            m = re.match(r'text/html.*',contentType)
            if m:
                print ("%s-%s-%s")%(res.info().get('Content-Encoding'),contentType,url)
                if res.info().get('Content-Encoding')=='gzip':
                    buf = StringIO(res.read())
                    f = gzip.GzipFile(fileobj=buf)
                    content = f.read()
                else:
                    content = res.read()
            else:
                print ("\033[1;31;40m*%s\033[0m")%(url,)
                return
        else:
            return
    except URLError,e:
        print ("\033[1;31;40m%s-%s\033[0m")%(e,url)
        return
    analysis(content,curdepth)

def crawFromQue(que,curdepth):
    print curdepth
    while not que.empty():
        crawlone(que.get(),curdepth)

def analysis(content,curdepth):
    global ques
    global config
    global logger 
    msg={}
    #soup = BeautifulSoup(content)
    #print soup.title.string
    #f = open("/tmp/body.html","w+")
    links = re.findall(r'href\=\"(http\:\/\/[a-zA-Z0-9\.\/\=]+)\"',content)
    #f.write(soup.body.get_text())
    for l in links:
        if hash(l) in urlhash:
            continue
        elif curdepth < config["depth"]:
            logger.info(l)

            ques[curdepth+1].put(l)
            urlhash.append(hash(l))

def init():
    global ques
    for i in range(config["depth"]+1):
        ques.append(Queue.Queue())

def main(argc,argv):
    global config
    if(argc < 2 or argv[1] == "--help"):
        help()
        sys.exit(0)
    else:
        for i in range(1,argc):
            if i % 2 ==1:
                s = argv[i]
                if s in ("--url","-u"):
                    config['url'] = argv[i+1]
                elif s in ("--depth","-d"):
                    config["depth"] = int(argv[i+1])
    init()
    crawlone(config["url"],0)
    for i in range(1,config['depth']):
        #pass
        crawFromQue(ques[i],i)

def help():
    msg='''usage: spider.py -u|--url xxx -d|--depth ng
    --url   | -u: the url to begin, http://www.sina.com.cng
    --depth | -d: the depth to be crawled, intg
    --help  | -h: help
    '''
    print msg
if __name__ == "__main__":
    main(len(sys.argv),sys.argv)
    for q in ques:
        while not q.empty():
            print q.get()
#    for k in config.keys():
#        print config[k]
