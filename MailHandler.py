import sys
import os
from email.parser import FeedParser
from email.message import Message
import datetime

LOG_FILE="/home/ubuntu/MailHandler/log.txt"
PUBLISH="sh /home/ubuntu/Training/publish.sh > /home/ubuntu/MailHandler/detail.txt 2>&1"
EVA_PUBLISH="sh /home/ubuntu/Training/eva_publish.sh >> /home/ubuntu/MailHandler/detail.txt 2>&1"

parser = FeedParser()
for line in sys.stdin:
    parser.feed(line)
message = parser.close()

destination = message["X-Original-To"]
log = open(LOG_FILE, "a")
if "auto.test.email@" in destination:
    log.write("Test email received at %s\n"%datetime.date.today())
elif "auto.submitted.run" in destination:
    log.write("Submitted run at %s\n"%datetime.date.today())
    os.system(PUBLISH)
    os.system(EVA_PUBLISH)
elif "auto.newsfeed" in destination:
    log.write("News item %s at %s\n"%(message["Subject"], datetime.date.today()))
    
else:
    log.write("Unrecognized destination '%s' at %s\n"%(destination, datetime.date.today()))
log.close()

