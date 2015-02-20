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
def expand_link(environ, start_response):
    params = environ['params']
    source = params.get('source')
    target = params.get('target')
    
    print("Retrieving expanded path data :::: source=" + source + " : target=" + target)
    
    graphData = get_expanded_path(source, target)

    print(json.dumps(graphData) )
    start_response('200 OK', [ ('Content-type', 'application/json'), ('Access-Control-Allow-Origin', '*') ])
    yield json.dumps(graphData).encode('utf-8')


#
# Running the server
#
if __name__ == '__main__':
    from resty import PathDispatcher
    from diagdata import filter_data
    from diagdata import get_expanded_path
    from wsgiref.simple_server import make_server

    # Create the dispatcher and register functions
    dispatcher = PathDispatcher()
    dispatcher.register('GET', '/data', fetch_data)
    dispatcher.register('GET', '/expand', expand_link)

    # Launch a basic server
    httpd = make_server('', 24680, dispatcher)
    print('Serving on port 24680...')
    httpd.serve_forever()
