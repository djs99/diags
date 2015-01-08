# dataserver.py

import json

#
# Return data for force layout experiment.
#
def fetch_data(environ, start_response):
    start_response('200 OK', [ ('Content-type', 'application/json'), ('Access-Control-Allow-Origin', '*') ])
    params = environ['params']
    focus = params.get('focus')
    span = params.get('span')
    print("Retrieving graph data with focus=" + focus + " and span=" + span)
    graphData = filter_data(focus, span)
    print(json.dumps(graphData) )
    yield json.dumps(graphData).encode('utf-8')


#
# Return data with the specified link uncompressed.
#
def uncompress_link(environ, start_response):
    start_response('200 OK', [ ('Content-type', 'application/json'), ('Access-Control-Allow-Origin', '*') ])
    params = environ['params']
    focus = "bogus"
    span = "all"
    source = params.get('source')
    target = params.get('target')
    print("Retrieving uncompressed graph data :::: focus=" + focus + " : span=" + span + " : source=" + source + " : target=" + target)
    graphData = filter_data(focus, span)
    print(json.dumps(graphData) )
    yield json.dumps(graphData).encode('utf-8')


#
# Return data for tree layout experiments.
#
def fetch_flare_data(environ, start_response):
    start_response('200 OK', [ ('Content-type', 'application/json'), ('Access-Control-Allow-Origin', '*') ])
    print("Retrieving flare data")
    myData = get_flare_data()
    print(json.dumps(myData) )
    yield json.dumps(myData).encode('utf-8')


#
# Running the server
#
if __name__ == '__main__':
    from resty import PathDispatcher
    from diagdata import filter_data
    from diagdata import get_flare_data
    from wsgiref.simple_server import make_server

    # Create the dispatcher and register functions
    dispatcher = PathDispatcher()
    dispatcher.register('GET', '/data', fetch_data)
    dispatcher.register('GET', '/uncompress', uncompress_link)
    dispatcher.register('GET', '/flaredata', fetch_flare_data)

    # Launch a basic server
    httpd = make_server('', 24680, dispatcher)
    print('Serving on port 24680...')
    httpd.serve_forever()
