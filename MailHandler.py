import sys
import os
from email.parser import FeedParser
from email.message import Message
import datetime
import ConfigParser
import boto
from boto.s3.key import Key

LOG_FILE="/home/ubuntu/MailHandler/log.txt"
PUBLISH="sh /home/ubuntu/Training/publish.sh >> /home/ubuntu/MailHandler/detail.txt 2>&1"
EVA_PUBLISH="sh /home/ubuntu/Training/eva_publish.sh >> /home/ubuntu/MailHandler/detail.txt 2>&1"
# Nasty sleep is to try and ensure read-after-update consistency
PUBLISH_NEWS="sleep 10;cd /home/ubuntu/NewsFeed; python ./NewsFeed.py >> /home/ubuntu/MailHandler/detail.txt 2>&1"

BUCKET="danieltebbutt.com"
NEWSLOG="newsfeed/newslog.csv"

def uploadNews(newNews):
    s3 = boto.connect_s3()
    bucket = s3.get_bucket(BUCKET)
                    
    k = Key(bucket)
    k.key = NEWSLOG
    if k.exists():
        oldNews = k.get_contents_as_string().strip()
    else:
        oldNews = ""
    print oldNews
    news = oldNews + "\n" + newNews
    print news   
    k.set_contents_from_string(news)

def upload(text, dest):
    s3 = boto.connect_s3()
    bucket = s3.get_bucket(BUCKET)

    k = Key(bucket)
    k.key = dest
    k.set_contents_from_string(text)

def deleteLast():
    s3 = boto.connect_s3()
    bucket = s3.get_bucket(BUCKET)
    k = Key(bucket)
    k.key = NEWSLOG
    if k.exists():
        content = k.get_contents_as_string()
        lines = content.strip().split("\n")[:-1]
        content = "\n".join(lines)
        k.set_contents_from_string(content)

parser = FeedParser()
for line in sys.stdin:
    parser.feed(line)
message = parser.close()

destination = message["X-Original-To"]
print destination
log = open(LOG_FILE, "a")
if "auto.test.upload" in destination:
    log.write("Test upload at %s\n"%datetime.date.today())
    upload(message["Subject"], "test.html")
elif "auto.test" in destination:
    log.write("Test email received at %s\n"%datetime.date.today())
elif "auto.run" in destination or "auto.submitted.run" in destination:
    log.write("Submitted run at %s\n"%datetime.date.today())
    os.system(PUBLISH)
    os.system(EVA_PUBLISH)
    os.system(PUBLISH_NEWS)
elif "auto.news.delete" in destination:
    log.write("Delete last news item at %s\n"%datetime.date.today())
    deleteLast()
    os.system(PUBLISH_NEWS)
elif "auto.news" in destination:
    log.write("News item %s at %s\n"%(message["Subject"], datetime.date.today()))
    # !! Make score configurable in subject
    uploadNews("NEWS,%s,%s,%d\n"%(datetime.date.today(), message["Subject"], 50))
    os.system(PUBLISH_NEWS)
else:
    log.write("Unrecognized destination '%s' at %s\n"%(destination, datetime.date.today()))
log.close()

