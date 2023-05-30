import socket
import threading
import time


#   This function facilitates the handshake between the data being sent 
#   between nodes.  It accepts a send or recieve flag depending on the usage.
#   It confirms if the data reached the recipiant.

#   @param connection: live connection variable for server
#   @param message: message being sent
#   @param flag: send or recieve flag. S for send R for recieve
#   @return message from recived flag 

def handshake(connection, message, flag):

    match flag:
        case "S":
            connection.send(message.encode()) #encodes the message and sends
            if connection.recv(1024).decode() != message: #checks to see if recieved conformation message is correct
                print("ERR: MESSAGE NOT RECIEVED")
        case "R":
            rmessage = connection.recv(1024) #recives message
            connection.send(rmessage)
            return rmessage.decode() #decodes the message and returns

#Node A
def nodeA():

    with open('confA.txt', 'r') as file: #open config file
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Sets up a network socket and sets its streams variables.
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        send_port = int(file.readline()) #Gets port number  from config file
        try:
            while s.connect_ex(('', send_port)) != 0: #Waits for connection between node B.
                time.sleep(1)
        except:
            print("PORT BIND FALURE NODE A") #Sends and exception if there is a port bind error.
            exit()
        for line in file:
            handshake(s, line.strip(), "S") #Sends each line of text through the handshake method to confirm data
        handshake(s, "stop", "S")
        s.close #closes port
        

#Node B
def nodeB():

    with open('confB.txt', 'r') as file: 
        #Node B (Recive)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        recv_port = int(file.readline()) #gets port number for node A
        send_port = int(file.readline()) #gets port number for node B
        try:
            s.bind(('', recv_port)) #binds to the client port
        except:
            print("PORT BIND FALURE NODE B (RECIEVE)") #Sends and exception if there is a port bind error.
            exit()
        s.listen(1)
        connection, address = s.accept() #creates connection enviroment
        print("Node B recived connection from node A at: " + str(address))
        data = handshake(connection, None, "R")
        while data != "stop": #recieves data from connected node
            print(f'Data Recived from Node A: {data}')
            data = handshake(connection, None, "R")
        connection.close() #closes data stream
        s.close() #closes socket


        #Node B (Send)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            while s.connect_ex(('', send_port)) != 0: #Waits for connection between node C.
                time.sleep(1)
        except:
            print("PORT BIND FALURE NODE B (SEND)") #Sends and exception if there is a port bind error.
            exit()
        for line in file:
            handshake(s, line.strip(), "S") #Sends each line of text through the handshake method to confirm data
        handshake(s, "stop", "S")
        s.close #closes port


#Node C
def nodeC():
    
    with open('confC.txt', 'r') as file:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        recv_port = int(file.readline())
        try:
            s.bind(('', recv_port)) #binds to the client port
        except:
            print("PORT BIND FALURE NODE C") #port exception
            exit()

        s.listen(1)
        connection, address = s.accept() #creats connection enviroment
        print("Node C recived connection from node B at: " + str(address)) 
        data = handshake(connection, None, "R")
        while data != "stop": #recieves data from connected node
            print(f'Data Recived from Node B: {data}')
            data = handshake(connection, None, "R")
        connection.close() #closes stream data
        s.close() #closes socket

# Sets up each thread to be run
NODE_A = threading.Thread(target=nodeA)
NODE_B = threading.Thread(target=nodeB)
NODE_C = threading.Thread(target=nodeC)

#Starts each thread
NODE_A.start()
NODE_B.start()
NODE_C.start()
