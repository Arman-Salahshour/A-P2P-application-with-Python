import socket
import threading



SERVER=socket.gethostbyname(socket.gethostname())
PORT=5050
HEADER=4096
DISCONNECT_MESSAGE="!disconnect"
REQUEST_PEERS="I need seven peers"
RElEASE_REQUEST="release these peers"
CONNECTION_ADDR="ipPort"
CHECK_LOOP="just loop"
WAIT="wait"
CONTINUE='continue'
MAKE_MATRICES='make matrices'
MULTIPLY_MATRIX="multiply matrices"
FORMAT='utf-8'
PEERS='peers'
request_lock = threading.Semaphore()
table_lock = threading.Semaphore()
peer_lock=threading.Semaphore()
