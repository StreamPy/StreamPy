import sys
import time
from stompy.simple import Client
import json

class RemoteQueue(object):
    def __init__(self, host, port, destination):
        self.host = host
        self.port = port
        self.destination = destination
        self.stomp = Client(host, port)
        self.stomp.connect()
        self.stomp.subscribe(destination)

    def put(self, message):
        message = json.dumps(message)
        self.stomp.put(message, self.destination)

    def get(self):
        mq_message = self.stomp.get(block=True)
        message = mq_message.body
        message = json.loads(message)
        return message

    def disconnect(self):
        self.stomp.unsubscribe(self.destination)
        self.stomp.disconnect()

def main():
    TOPIC_1 = '/topic/julian_1'
    TOPIC_2 = '/topic/remote_queue'

    SERVER = 'pcbunn.cacr.caltech.edu'
    PORT = 61613
    
    try:
        # Testing remote queue
        q = RemoteQueue(host=SERVER, port=PORT, destination=TOPIC_2)
        stomp_1 = Client(host=SERVER, port=PORT)
        stomp_1.connect()
        stomp_1.subscribe(destination=TOPIC_1)
        
        for i in range(4):
            stomp_1.put(i, destination=TOPIC_1)
            q.put(i+40)

        for j in range(4):
            message_1 = stomp_1.get(block=True)
            message_2 = q.get()
            print 'message_1 is ', message_1.body
            print 'message_2 is ', message_2

            #print 'ack'
            #stomp.ack(message)
            time.sleep(1.0)

    except Exception, err:
        print 'Error', err
        return
    q.disconnect()
    stomp_1.unsubscribe(TOPIC_1)
    stomp_1.disconnect()

if __name__ == '__main__':
    main()
