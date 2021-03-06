import time
import calendar
import eventlet
import requests
from flask import *
from config import *
from datetime import datetime
from lxml.html import fromstring
from main import main, configured_servers

time.sleep(STARTUP_DELAY)  # Wait for the startup delay so the other applications have time to boot up

main()  # initialize configured_servers

app = Flask(__name__)

configured_urls = []
short_urls = []
short_url_use = []
titles = []

for server in configured_servers:
    configured_urls += server.get_link_urls()
    short_urls += server.get_short_urls()
    short_url_use += server.get_short_url_use()


# Pull the title of the webpage from the URL
def get_title(url):
    global title
    try:
        with eventlet.Timeout(2):
            r = requests.get(url)  # 2 second ping timeout in case of invalid url
            tree = fromstring(r.content)
            title = tree.findtext('.//title')
            if r.status_code != 200:
                title = ''
    except:
        title = ''

    return title


eventlet.monkey_patch()  # Necessary to set timeouts on requests

for index in range(0, len(configured_urls)):
    titles.append(get_title(configured_urls[index]))


@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}


@app.context_processor
def inject_time_to_all_templates():
    return dict(time=get_time())


@app.route('/')
def index():
    return render_template("index.html", urls=configured_urls, short_urls=short_urls, short_url_use=short_url_use,
                           titles=titles)


def get_time():
    return calendar.timegm(datetime.now().utctimetuple())


if __name__ == '__main__':
    app.run()
