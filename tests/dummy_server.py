# -*- coding: utf-8 -*-
import json
import os
from optparse import OptionParser
from gevent import monkey
monkey.patch_all()
from gevent import pywsgi
results = {}


def response_ok(regid):
    return {'registrationID': regid}, '200 OK'


def response_update(regid):
    return {'registrationID': 'newtoken'}, '200 OK'


def response_invalid(regid):
    return {'reason': 'InvalidRegistrationId'}, '400 BAD REQUEST'


ops = {
    'OK': response_ok,
    'INVALID': response_invalid,
    'UPDATE': response_update
}


def handle(env, start_response):
    if '/auth/O2/token' in env['PATH_INFO']:
        response = {'access_token': 'token', 'expires_in': 10}
        code = '200 OK'
    else:
        body = json.loads(env['wsgi.input'].read())
        print "body: {0}".format(body)
        regid = env['PATH_INFO'].split('/')[3]
        if regid in results:
            response, code = ops[results[regid].strip().upper()](regid)
        else:
            # by default response will be ok
            response, code = response_ok(regid)

    start_response(code, [('Content-Type', 'application/json')])
    print "response: {0}".format(response)
    return [json.dumps(response)]


def main():
    parser = OptionParser()
    parser.add_option(
        "-p", "--port",
        dest="port",
        help="Server port [%default]",
        default=8081)

    parser.add_option(
        "-b", "--bind_address",
        dest="bind",
        help="Bind addreess [%default]",
        default="0.0.0.0")

    parser.add_option(
        "-r", "--results_file",
        dest="rfile",
        help="Results file [%default]",
        default="results.csv")

    (options, args) = parser.parse_args()

    # By default server outputs ok responses, but a results file could be defined to define responses.
    if os.path.exists(options.rfile):
        print 'Loaded %s file' % options.rfile
        global results
        results = dict(x.strip().split(',') for x in open(options.rfile, 'r'))

    print "Starting server on %s:%s" % (options.bind, int(options.port))
    pywsgi.WSGIServer((options.bind, int(options.port)), handle).serve_forever()

if __name__ == "__main__":
    main()
