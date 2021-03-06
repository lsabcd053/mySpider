#!/usr/bin/python 
#coding=utf-8
import sys,os,re,threading
import Queue
import urllib2,cookielib,gzip,logging
from StringIO import StringIO
from bs4 import BeautifulSoup
from urllib2 import Request, urlopen, URLError, HTTPError

config={"url":"http://www.baidu.com","depth":1,"logfile":"spider.log","loglevel":3,"thread":0}
ques=[]
urlhash=[]
logger=''

LEVEL={1:logging.CRITICAL,2:logging.ERROR,3:logging.WARNING,4:logging.INFO,5:logging.DEBUG}

def log(logname=__name__):
    global config,logger
    logger = logging.getLogger(logname)
    logger.setLevel(LEVEL[config["loglevel"]])

    ch = logging.FileHandler(config["logfile"])
    #ch = logging.StreamHandler()
    ch.setLevel(LEVEL[config["loglevel"]])
    fm = logging.Formatter("%(asctime)s - %(levelname)s - %(funcName)s - %(threadName)s - %(message)s")
    ch.setFormatter(fm)
    logger.addHandler(ch)


def crawlone(url,curdepth):
    global logger
    logger.info("Begin to crawl %s depth:%d"%(config['url'],curdepth))
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    req = urllib2.Request(url)
    req.add_header('Accept-encoding','gzip')
    try:
        res = opener.open(req)
        #有的网站数据是经过gzip压缩的，如qq.com,sina.com.cn等
        contentType = res.info().get('Content-Type')
        if contentType:
            logger.info("%s-%s"%(url,contentType))
            m = re.match(r'text/html.*',contentType)
            if m:
                #print ("%s-%s-%s")%(res.info().get('Content-Encoding'),contentType,url)
                if res.info().get('Content-Encoding')=='gzip':
                    try:
                        buf = StringIO(res.read())
                        f = gzip.GzipFile(fileobj=buf)
                        content = f.read()
                    except IOError,e:
                        logger.error('%s:%s'%(e,url))
                        print ("\033[1;31;40m*%s:%s\033[0m")%(e,url)
                        content = f.extrabuf
                else:
                    content = res.read()
            else:
                logger.error(url)
                print ("\033[1;31;40m*%s\033[0m")%(url,)
                return
        else:
            return
    except URLError,e:
        logger.error(("%s,%s")%(e,url))
        print ("\033[1;31;40m%s-%s\033[0m")%(e,url)
        return
    analysis(content,curdepth)

class crawThread(threading.Thread):
    def __init__(self,url,curdepth):
        threading.Thread.__init__(self)
        self.url = url
        self.curdepth = curdepth
        print url,curdepth
    def run(self):
        crawlone(self.url,self.curdepth)

def crawFromQue(que,curdepth):
    global config,logger
    #多线程处理
    if config['thread'] > 0:
        threads=[]
        while not que.empty():
            url = que.get()
            try:
                ctd = crawThread(url,curdepth)
                ctd.start()
                threads.append(ctd)
            except BaseException,e:
                print threading.currentThread().getName(),":",e
                logger.error("%s - %s"%(e,url))
                #print threading.currentThread().getNum(),'quit'
        for t in threads:
            t.join()
    #单线程处理
    else:
        while not que.empty():
            crawlone(que.get(),curdepth)

def analysis(content,curdepth):
    global ques
    global config,logger
    msg={}
    #soup = BeautifulSoup(content)
    #print soup.title.string
    #f = open("/tmp/body.html","w+")

    links = re.findall(r'href\=\"(http\:\/\/[a-zA-Z0-9\.\/\=\?]*)\"',content)
    #f.write(soup.body.get_text())
    for l in links:
        if hash(l) in urlhash:
            continue
        elif curdepth < config["depth"]-1:
            #logger.info(l)
            logger.info(l)
            ques[curdepth+1].put(l)
            urlhash.append(hash(l))

def init():
    global ques
    log()
    for i in range(config["depth"]+1):
        ques.append(Queue.Queue())

def main(argc,argv):
    global config,logger
    if(argc < 2 or argv[1] == "--help"):
        help()
        sys.exit(0)
    else:
        for i in range(1,argc):
            if i % 2 ==1:
                s = argv[i]
                if s in ("--url","-u"):
                    config["url"] = argv[i+1]
                elif s in ("--depth","-d"):
                    config["depth"] = int(argv[i+1])
                elif s in ("--logfile","-f"):
                    config["logfile"] = argv[i+1]
                elif s in ("--loglevel","-l"):
                    config["loglevel"]=int(argv[i+1])
                elif s in ("--thread","-t"):
                    config["thread"]=int(argv[i+1])
    init()
    logger.info("Begin to crawl %s,depth:%d logfile:%s"%(config['url'],config['depth'],config['logfile']))
    crawlone(config["url"],0)
    for i in range(1,config['depth']):
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
#    for q in ques:
#        while not q.empty():
#            print q.get()
#    for k in config.keys():
#        print config[k]
