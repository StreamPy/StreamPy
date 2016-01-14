from bottle import route, run, request
import pickle
import threading

master = None

@route('/processes/:id', method='GET')
def get_process(id):
    print "GET on master server for process conn {0}:{1}".format(master.processConns[int(id)][0], master.processConns[int(id)][1])
    return str(master.processConns[int(id)][0]) + "," + str(master.processConns[int(id)][1])

@route('/processes/ready', method='POST')
def process_ready():
    data = request.body.read()
    master.processReady(data)
"""
@route('/processes', method='POST')
def put_process():
    global data
    data = pickle.loads(request.body.read())
"""

def run_server(m):
    global master
    master = m
    # run(host='localhost', port=m.port, debug=True)
    threading.Thread(target=run, kwargs=dict(host=m.host, port=m.port)).start()
