from constants import *
import socket
import pickle
import threading
import pandas as pd
import time


''' IT'S A TABLE FOR SAVING PEER'S ADDRESS AND ( CONNECTION OBJECT AS CLENT ) '''
class Peers_Table():
    def __init__(self):
        self.table =pd.DataFrame({'ip':[],'port':[],'used':[]})
        # self.table['used'].astype(bool)

    '''ADD NEW ROW TO THE TABLE'''
    def register(self,addr):
        self.table.loc[len(self.table.index)]=[addr[0],addr[1],False]
    
    '''IF THERE ARE MORE THAN 7 PEERS WHICH USED COL IS TRUE THIS METHODS RETURN RANDOMLY 7 PEERS'''
    def request(self,conn,addr):
        
        with request_lock:
            unused_peers_count =self.table[self.table['used']==False].shape[0]
            

            if(unused_peers_count<7):
                print(f"Resource constraints\n{addr}: Please wait until the restrictions will be lifted")
                data_string=(CHECK_LOOP,)+(WAIT,)
                data_string=pickle.dumps(data_string)
                conn.send(data_string)
                while True:
                    unused_peers_count =self.table[self.table['used']==False].shape[0]
                    '''Check connection'''
                    try:
                        data_string=(CHECK_LOOP,)+(CHECK_LOOP,)
                        data_string_obj=pickle.dumps(data_string)
                        conn.send(data_string_obj)
                        return data_string
                    except:
                        self.remove(addr)
                        return

                    # if(unused_peers_count>7):
                    #     data_string=(CHECK_LOOP,)+(CONTINUE,)
                    #     data_string=pickle.dumps(data_string)
                    #     conn.send(data_string)
                    #     break


            unused_peers=self.table.loc[(self.table['used']==False) & (self.table['port']!=self.table['port'].loc[len(self.table.index)-1])].sample(n=7)
            unused_peers.reset_index(drop=True, inplace=True)
            unused_peers.drop('used',axis=1,inplace=True)
            
            '''CHANGE PEERS USING TO TRUE'''
            for i in range(7):
                # print(unused_peers['client'].iloc[i])
                self.table['used'].loc[(self.table['port']==unused_peers['port'].iloc[i]) & (self.table['ip']==unused_peers['ip'].iloc[i])]=True

            print(f'7 peers are reserved for {addr}')
            return unused_peers
    
    '''RELEASE PEERS'''
    def release(self,user_peers):
        '''CHANGE PEERS USING TO FALSE'''

        for i in range(7):
            self.table['used'].loc[(self.table['port']==user_peers['port'].iloc[i]) & (self.table['ip']==user_peers['ip'].iloc[i])]=False
        print('7 peers are released')

    '''IF PEER IS DISCONNECTED, IT WILL BE REMOVE FROM THE TABLE'''
    def remove(self,addr):
        try:
            
            self.table.drop(self.table[(self.table['ip']==addr[0]) & (self.table['port']==addr[1])].index[0],inplace=True)
            self.table.reset_index(drop=True, inplace=True)
        except:
            print('The table is empty')






'''This method handle peer (client side) request'''
def client_registration(conn,addr):
    import pickle
    peers=None
    print(f"[NEW CONNECTION] '{addr}' is connected\n")
    connected=True
    while connected:
        try:
            msg_length=conn.recv(HEADER).decode(FORMAT)
            if msg_length:
                msg_length=int(msg_length)
                msg=conn.recv(msg_length).decode(FORMAT)

                if(msg==REQUEST_PEERS):
                    try:
                        peers=peers_table.request(conn,addr)
                        if(isinstance(peers, pd.DataFrame)):
                            peers_tuple=(PEERS,)+(peers,)
                        else:
                            peers_tuple=(CHECK_LOOP,)+(CHECK_LOOP,)
                        data_string=pickle.dumps(peers_tuple)
                        conn.send(data_string)
                    except Exception:
                        print('Sending was unsuccessful')
                        peers_table.release(peers)

                        break

                elif(msg==RElEASE_REQUEST):
                    if(isinstance(peers, pd.DataFrame)):
                        peers_table.release(peers)


                elif msg==DISCONNECT_MESSAGE:
                    connected=False

        except:
            break

    print(f"[DISCONNECTING] '{addr}' is disconnected\n")
    if(isinstance(peers, pd.DataFrame)):
        peers_table.release(peers)

    peers_table.remove(addr)
    conn.close()






def start():
    print(f"[LISTENING] server is listening on {SERVER}\n")
    server.listen()

    while True:
        conn,addr=server.accept()
        send_connectionAddr(conn,addr)

        '''Add new peer to peers table and'''
        with table_lock:
            peers_table.register(addr)

        thread=threading.Thread(target=client_registration, args=(conn,addr))
        thread.start()
        print(f"[Active connection] : {threading.activeCount()-1}")


def send_connectionAddr(conn,addr):
    # message=CONNECTION_ADDR.encode(FORMAT)
    # conn.send(message)
    addr=(CONNECTION_ADDR,)+(addr,)
    data_string=pickle.dumps(addr)
    conn.send(data_string)

def send_message(conn,message):
    msg_length=len(message)
    send_length=str(msg_length).encode(FORMAT)
    send_length+= b' '*(HEADER-len(send_length))
    conn.send(send_length)
    conn.send(message.encode(FORMAT))

'''Binding server to the specific ip and port'''
ADDR=(SERVER,PORT)
server=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)
peers_table=Peers_Table()



print("[STARTING] main server is starting...")

start()