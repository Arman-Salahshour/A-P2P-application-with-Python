
from functools import partial
import socket
import pickle
import numpy as np
import pandas as pd
from constants import *


'''It's a class for server side of the peer.'''
class Server():
    def __init__(self):
        self.ip=None
        self.port=None


'''The peer requests 7 another peers.'''
def peer_request():
    send_message(client,REQUEST_PEERS)


'''This function releases used peer.'''
def release_request():
    global peers
    global peers_clientSide
    global limited_flag

    if(isinstance(peers, pd.DataFrame)):
        print(peers)
        peers=None
        for i in range(len(peers_clientSide)):
            peers_clientSide[i].close()

        peers_clientSide=[]
        send_message(client,RElEASE_REQUEST)

        print('\n---------->Peers are released\n')
    else:
        print('\n---------->There is no peers to release\n')
    
    limited_flag=None
    


'''This function is always listening to the data received from the main server.'''
'''The data is a tuple, index zero is the main data identifier'''
def server_recving():
    global peers
    global server
    global peers_clientSide
    global limited_flag

    while True:
        init=client.recv(HEADER)
        if(init):
            try:
                init=pickle.loads(init)
                msg=init[0]
                if(msg==CONNECTION_ADDR):
                    config=init[1]
                    server.ip,server.port=config
                    server_thread=threading.Thread(target=server_isListening)
                    server_thread.start()
                elif(msg==PEERS):
                    peers=init[1]
                    limited_flag=False
                    '''Connecting to the peers server side'''
                    for i in range(7):
                        clientSide=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        config=(peers['ip'].iloc[i],int(peers['port'].iloc[i]))
                        clientSide.connect(config)
                        peers_clientSide.append(clientSide)
                    
                
                #'''pass every message that includes CHECK_LOOP'''
                elif(msg==CHECK_LOOP):
                    if(init[1]==WAIT):
                        limited_flag=True
                        print('\n\n----------> Seven peers will be reserved when they are released\n\n')
                    elif(init[1]==CONTINUE):
                        limited_flag=False
                        print('\n---------->Seven peers are reserved\n\n')
                    else:
                        limited_flag=True
                        if(len(peers_clientSide)!=0):
                            limited_flag=False
                        # pass
                         
            except:
                print('An error occured')
                release_request()
                client.close()
                break



def server_isListening():
    server_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    config=(server.ip,server.port,)
    server_socket.bind(config)
    print(f"[LISTENING] peer's server side is listening on {config}\n")
    print('\n----------> \n')

    server_socket.listen()

    while True:
        try:
            conn,addr=server_socket.accept()
            print(addr)
            peer_handler_thread=threading.Thread(target=peer_handler, args=(conn,addr))
            peer_handler_thread.start()
            print(f"[Active connection] peer's server side : {threading.activeCount()-1}")

        except:
            print(f"[LISTENING] peer's server side is not listening on {config}\n")
            server_socket.close()
            break


def peer_handler(conn,addr):
    import pickle
    global limited_flag
    # peers=None
    print(f"[NEW CONNECTION] peer's client side '{addr}' is connected\n")
    connected=True
    while connected:
        try:
            init=conn.recv(HEADER)
            if(init):
                if(len(peers_clientSide)==0):
                    peer_request()
                    
                while(limited_flag==None):
                    pass

                init=pickle.loads(init)
                solution=strassen(init[1][0],init[1][1])
                solution=(init[0],solution,)
                solution=pickle.dumps(solution)
                conn.send(solution)
                release_request()
        except:
            break

    print(f"[DISCONNECTING] peer's client side '{addr}' is disconnected\n")
    conn.close()




def input_handler():
    global X
    global Y
    while True:
        # try:
        command =input('Please write your command and press Enter:\n')
        if(command == REQUEST_PEERS):
            peer_request()
            print('\n\n---------->\n\n')
        elif(command == RElEASE_REQUEST):
            release_request()
            # print('\n\n---------->Peers are released\n\n')
            print('\n\n---------->\n\n')

        elif(command == MAKE_MATRICES):
            X,Y =make_two_matrix(5)
            print(f' X : \n {X}')
            print('--------------')
            print(f' Y : \n {Y}\n')

        elif(command == MULTIPLY_MATRIX):
            if(len(peers_clientSide)==0):
                peer_request()
            print('\n\n---------->\n\n')

            while limited_flag==None:
                pass
            while (len(peers_clientSide)!=7 ):
                if(limited_flag==True):
                    break
            solution=strassen(X,Y)
            print(f' Solution is :\n {solution}\n')
            
            if(len(peers_clientSide)!=0):
                release_request()

            # while(solution==None):
            #     pass
            # release_request()



        # except:
        #     print("Please set again the peer")
        #     client.close()
        #     break



def split(matrix):

	row, col = matrix.shape
	row2, col2 = row//2, col//2
	return matrix[:row2, :col2], matrix[:row2, col2:], matrix[row2:, :col2], matrix[row2:, col2:]




def strassen(x,y):

    global limited_flag
    Pi=[None]*7
    part=[]
    client_side_receiver_list=[]
	# Base case when size of matrices is 1x1
    if (len(x) == 1):
        return x * y

	# Splitting the matrices into quadrants. This will be done recursively
	# untill the base case is reached.
    a, b, c, d = split(x)
    e, f, g, h = split(y)

	# Computing the 7 products, recursively (p1, p2...p7)
    part.append((a, f - h,))
    part.append((a + b, h,))
    part.append((c + d, e,))
    part.append((d, g - e,))
    part.append((a + d, e + h,))	
    part.append((b - d, g + h,))
    part.append((a - c, e + f,))

    
    if(len(peers_clientSide)==0):
        peer_request()
    while limited_flag==None:
        pass
    while (len(peers_clientSide)!=7):
        if(limited_flag==True):
            break

    
    if(limited_flag==False):
        # print(len(peers_clientSide))
        for i in range(7):
            msg=pickle.dumps((i,part[i],))
            peers_clientSide[i].send(msg)
            '''List of client side receiver threads'''
            client_side_receiver_list.append(threading.Thread(target=client_side_receiver,args=(peers_clientSide[i],i,Pi)))
            client_side_receiver_list[i].start()
        
        print('----->Please Wait')
        while (any(v is None for v in Pi)):
            pass
            
        

    elif(limited_flag==True):
        Pi[0] = strassen(a, f - h)
        Pi[1] = strassen(a + b, h)	
        Pi[2] = strassen(c + d, e)	
        Pi[3] = strassen(d, g - e)	
        Pi[4] = strassen(a + d, e + h)	
        Pi[5] = strassen(b - d, g + h)
        Pi[6] = strassen(a - c, e + f)


	# Computing the values of the 7 quadrants of the final matrix c
    c11 = Pi[4] + Pi[3] - Pi[1] + Pi[5]
    c12 = Pi[0] + Pi[1]		
    c21 = Pi[2] + Pi[3]	
    c22 = Pi[0] + Pi[4] - Pi[2] - Pi[6]

	# Combining the 7 quadrants into a single matrix by stacking horizontally and vertically.
    c = np.vstack((np.hstack((c11, c12)), np.hstack((c21, c22))))
    limited_flag=None

    # for i in range(7):
    #     client_side_receiver_list[i].join()

    return c






def client_side_receiver(conn,i,Pi):
    while True:
        try:
            init =conn.recv(HEADER)
            if(init):
                init=pickle.loads(init)
                num = init[0]
                if(num==i):
                    Pi[i]=init[1]
        except:
            # print('Receving was unsuccessful')
            break

def send_message(client,msg):
    message=msg
    msg_length=len(message)
    send_length=str(msg_length).encode(FORMAT)
    send_length+= b' '*(HEADER-len(send_length))
    client.send(send_length)
    client.send(message.encode(FORMAT))

def make_two_matrix(n):
    size=2**n
    x=np.random.randint(10,size=(size,size))  
    y=np.random.randint(10,size=(size,size))

    return x,y  

'''Connecting to the main server'''
ADDR=(SERVER,PORT)
client=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)
# client.recv(HEADER)

'''Recevied peers variable and list of peers connection'''
peers=None
peers_clientSide=[]

'''Server side configuration'''
server=Server()

'''Matrices'''
X=[]
Y=[]

'''flag'''
limited_flag=None



server_recving_thread = threading.Thread(target=server_recving)
input_handler_thread = threading.Thread(target=input_handler)
server_recving_thread.start()
input_handler_thread.start()
# peer_request()









# class client1():
#     def __init__(self):

#         SERVER=socket.gethostbyname(socket.gethostname())
#         # SERVER="192.168.56.1"
#         PORT=5050
#         HEADER=67
#         DISCONNECT_MESSAGE="!disconnect"
#         FORMAT='utf-8'
#         ADDR=(SERVER,PORT)

#         client=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         client.connect(ADDR)



#     def send_message(self,msg):
#         message=msg
#         msg_length=len(message)
#         send_length=str(msg_length).encode(self.FORMAT)
#         send_length+= b' '*(self.HEADER-len(send_length))
#         client.send(send_length)
#         client.send((message))

        # rand=np.random.randint(8,size=(7,7))  
        # data_string=pickle.dumps(rand)
        # send_message(data_string)
        # send_message(DISCONNECT_MESSAGE)






























# import socket
# import threading

# SERVER=socket.gethostbyname(socket.gethostname())
# # SERVER="192.168.56.1"
# PORT=5050
# HEADER=67
# DISCONNECT_MESSAGE="!disconnect"
# FORMAT='utf-8'
# ADDR=(SERVER,PORT)

# client=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# client.connect(ADDR)



# def send_message(msg):
#     message=msg.encode(FORMAT)
#     msg_length=len(message)
#     send_length=str(msg_length).encode(FORMAT)
#     send_length+= b' '*(HEADER-len(send_length))
#     client.send(send_length)
#     client.send((message))

# def receive_message():
#     while True:
#         try:
#             msg=client.recv(HEADER).decode(FORMAT)
#             if msg:
#                 print(msg)
#         except:
#             print('An error occurred')
#             send_message(DISCONNECT_MESSAGE)
#             client.close()
#             break


# receive_threading=threading.Thread(target=receive_message)
# receive_threading.start()
# send_message('Hello My New Friend')
# # send_message(DISCONNECT_MESSAGE)










