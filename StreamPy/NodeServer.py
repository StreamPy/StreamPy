from bottle import route, run, request
import dill
import threading

node = None


@route('/conf', method='POST')
def put_conf():
    data = request.body.read()
    conn = data.split(',')
    node.set_master(conn[0], int(conn[1]))
    print "POST on node server to set master conn {0}:{1}".format(conn[0], conn[1])



@route('/processes/:id', method='GET')
def get_process(id):
    print "GET on node server to get process port"
    print "process: " + id
    print "port: " + str(node.get_process_port(int(id)))
    return str(node.get_process_port(int(id)))


@route('/processes', method='POST')
def put_process():
    process = dill.loads(request.body.read())
    node.add_process(process)
    print "POST on node server to add process {0}".format(process.id)

@route('/start', method='POST')
def start():
    print "POST on node server to start processes"
    node.start()


def run_server(n):
    global node
    node = n
    #run(host='localhost', port=n.port, debug=True)
    server_thread = threading.Thread(target=run, kwargs=dict(host=n.host, port=n.port))
    server_thread.daemon = True
    server_thread.start()
