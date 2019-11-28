import logging
from logging.config import dictConfig

from flask import Flask
from flask import jsonify, json
from flask import request

from . import identifier

dictConfig({
    'version': 1,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s %(levelname)s [pid: %(process)s] [%(name)s: %(lineno)s] %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'DEBUG'
        },
    }
})

app = Flask(__name__)
logger = logging.getLogger(__name__)

CACHE = {}


@app.route('/store/', methods=['POST'])
def store():
    form = request.form

    logger.debug('-' * 80)
    logger.debug('url    : %s' % form['url'])
    logger.debug('title  : %s' % form['title'])
    logger.debug('window : %s x %s' % (form['window_width'], form['window_height']))
    logger.debug('length : %s' % len(form['page_source']))
    logger.debug('ips    : %s' % form['ips'])
    logger.debug('-' * 80)

    url = form['url']
    page_source = form['page_source']

    meta = identifier.get_site_meta(url, page_source)
    logger.debug('meta   :\n%s' % json.dumps(meta, indent=4, sort_keys=True))

    parser = identifier.get_parser(meta)
    logger.debug('parser : %s' % parser)

    logger.debug('-' * 80)

    parsed_data = {}
    if parser is not None:
        p = parser(page_source=page_source)
        parsed_data = p.parse()

    data = {
        'url': url,
        'window': {
            'width': int(form['window_width']),
            'height': int(form['window_height'])
        },
        'meta': meta,
        'parser_name': parser and parser.__name__,
        'parsed_data': parsed_data
    }
    return jsonify(data)
