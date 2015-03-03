__author__ = 'zanibonim'

import zmq
import zmq.error

# Test a REQ -> ROUTER pattern in ZMQ

#
# Init
#

clients = {}

def update_client(name):

    if name in clients:
        c = clients[name]
    else:
        c = 0

    c = c + 1
    clients[name] = c
    return c


queueName = 'inproc://test_zmq'

clientSocket1 = zmq.Context.instance().socket(zmq.REQ)
clientSocket1.connect(queueName)

clientSocket2 = zmq.Context.instance().socket(zmq.REQ)
clientSocket2.connect(queueName)

serverSocket =  zmq.Context.instance().socket(zmq.ROUTER)
serverSocket.bind(queueName)

#
# Test
#

clientSocket1.send('A')

# this is the default format of the message as received and transformed from ROUTER socket.
# Note that:
# - the address frame is used for identifying the caller in a unique way
# - the empty frame is mandatory, and it is used from ZMQ for identifying the start of the message body
address, empty, msg = serverSocket.recv_multipart()
c = update_client(msg)
print "\n  server received requested from " + msg

# Construct the result message.
serverSocket.send_multipart([address, b'', str(c)])

a = clientSocket1.recv()
print "\n  client A" + " received answer " + a
