import os
import socket
from threading import Thread
import hashlib

#Running multiple threads for multiple clients
class SThread(Thread):
    def __init__(self,address,connection):
        Thread.__init__(self)
        self.address = address
        self.s= connection
    def run(self):
            print ('new connection')
            while True:
                    print (' ')

                    #Operation to be performed by server
                    operation=self.s.recv(1024).decode()

                    #Upload operation: hash the user/object string and inform client the disk to upload to
                    if operation[:6]=='upload':
                        string=operation[7:]
                        h=hashlib.md5(string.encode("utf")).hexdigest()
                        value=bin(int(h, 16)).zfill(128)
                        value= int(value,2)
                        shift=bin(value >> 112)
                        diff= 16-len(shift)
                        shift=str(shift[2:])
                        slot = int(shift,2)
                        d2=maintable[slot]
                        print ('Informed client to upload file to disk: ',d2)
                        self.s.send(d2.encode())

                    #Download operation: hash the user/object string and inform client the disk to download from
                    elif operation[:8]=='download':
                        string=operation[9:]
                        h=hashlib.md5(string.encode("utf")).hexdigest()
                        value=bin(int(h, 16))
                        value= int(value,2)
                        shift=bin(value >> 112)
                        diff= 16-len(shift)
                        shift=str(shift[2:])
                        slot = int(shift,2)
                        print ('Informed client to download file from disk: ',d2)
                        d2=maintable[slot]
                        self.s.send(d2.encode())

                    #List all files in a directory
                    elif operation[:4]=='list':
                        for i in range(noOfdisks):
                            print ('Disk: ',client[i])
                            self.s.send(client[i].encode())

                    #Delete operation: hash the user/object string and inform client the disk to delete from
                    elif operation[:6]=='delete':
                        string=operation[7:]
                        h=hashlib.md5(string.encode("utf")).hexdigest()
                        value=bin(int(h, 16))
                        value= int(value,2)
                        shift=bin(value >> 112)
                        diff= 16-len(shift)
                        shift=str(shift[2:])
                        slot = int(shift,2)

                        d2=maintable[slot]
                        print ('Informed client to delete file from disk: ',d2)
                        self.s.send(d2.encode())
                    else:
                        break;

#Socket connection
s1 = socket.socket()
host = socket.gethostname()
s1.bind((host, 0))
port=s1.getsockname()[1]

#Validate server command
client=[]
command=input('enter server command')
flag=1
while flag:
    if command[:9] == 'server 16':
        j=10
        count=0
        for i in range(4):
            if command[j:j+11]=='129.210.16.' and command[j+11:j+13]>'79' and command [j+11:j+13]<='99':
                client.append(command[j:j+13])
                count=count+1
                j=j+14
                if count==4:
                    flag=0
            elif command[j:j+8]=='linux608' and command[j+8:j+10]>='10' and command[j+8:j+10]<='29':
                client.append(command[j:j+10])
                count=count+1
                j=j+11
                if count==4:
                    flag=0
            else:
                print('Try again, enter server command: ')
                command=input()
                break


#Main and backup tables
noOfdisks=4
liz = []
for i in range(noOfdisks):
   liz.extend([client[i]]*2**14)
maintable = dict(zip(range(2**16),liz))

liz1=[]
for j in range(3,-1,-1):
    liz1.extend([client[j]]*2**14)
backup = dict(zip(range(2**16-1,-1,-1),liz))

#For client to connect to server
hostip = socket.gethostbyname(host)
print('host name is: ',host)
print('host ip is: ',hostip)
print ('port is: ',port)

#Connect to multiple clients using multithreading
while True:
    s1.listen(1)
    connection, address = s1.accept()
    newthread = SThread(address, connection)
    newthread.start()
