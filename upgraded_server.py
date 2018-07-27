import os
import subprocess
import pipes
import socket
from threading import Thread
import hashlib

#Check if file exists in remote location
def exists_remote(host, path):

    stat = subprocess.call(['ssh', host, 'test -e '+pipes.quote(path)])
    if stat == 0:
        return True
    if stat == 1:
        return False
    raise Exception('Failed')

#Divide total size in partitions
def make_parts(x):
        sizes = []
        total = 2**16
        part_size = total/x
        while total>0:
                if total>=part_size:
                        sizes.append(part_size)
                        total -= part_size
                else:
                        sizes[0]+= total
                        total = 0
        return sizes

def reverse_dicto(dicto):
        reverse = {}
        for i in dicto:
                if dicto[i] not in reverse:
                        reverse[dicto[i]] = []
                reverse[dicto[i]].append(i)
        return reverse

#Create Main table
def initial_dictionary(partitions):
        all_sizes =make_parts(partitions)
        liz = []
        for i in range(partitions):
                for j in range(int(all_sizes[i])):
                        liz.append(i)
        return dict(zip(range(2**16),liz))

#Create Backup table
def initial_backup(partitions):
        all_sizes =make_parts(partitions)
        liz = []
        for i in range(partitions-1,-1,-1):
                for j in range(int(all_sizes[i])):
                        liz.append(i)
        return dict(zip(range(2**16-1,-1,-1),liz))

def added_partition_reverse_dictionary(partitions,reverse):
        all_sizes = make_parts(partitions)
        new_dicto = {}
        new_part = max(reverse.keys()) + 1
        leftover = []
        for i in reverse:
                new_dicto[i] = list(reverse[i][:int(all_sizes[i])])
                leftover.extend(list(reverse[i][int(all_sizes[i]):]))
        new_dicto[new_part] = list(leftover)
        return new_dicto

def reverse_reverse_dicto(reverse):
        new_dicto ={}
        for i in reverse:
                for j in reverse[i]:
                        new_dicto[j] = i
        return new_dicto

#Delete the disk from the main table
def delete_partition_reverse_dictionary(partitions,reverse):
        all_prev_sizes = make_parts(partitions+1)
        part_to_delete = partitions
        leftover = all_prev_sizes[part_to_delete]
        all_sizes = make_parts(partitions)
        differences = []
        for i in range(partitions):
                differences.append(int(all_sizes[i]-all_prev_sizes[i]))
        summer = 0
        for i in range(len(differences)):
                temp = list(reverse[part_to_delete][summer:summer+differences[i]])
                reverse[i].extend(temp)
        del reverse[part_to_delete]
        return reverse



#Running multiple threads for multiple clients
class SThread(Thread):
    def __init__(self,address,connection,partitions,reverse,dicto,backup):
        Thread.__init__(self)
        self.address = address
        self.s= connection
        self.partitions=partitions
        self.reverse=reverse
        self.dicto=dicto
        self.backup=backup
    def run(self):

            print ('new connection')
            while True:
                    login='agupta1'
                    print (' ')
                    #newdisks=noOfdisks

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
                        #d2=maintable[slot]
                        key=self.dicto[slot]
                        d2=client[key]

                        addTable[slot]=[string,d2]
                        arr=string.split('/')

                        d.setdefault(arr[0], [])
                        d[arr[0]].append(arr[1])
                        d[arr[0]].append(d2)
                        print (d)

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
                        #print ('Informed client to download file from disk: ',d2)
                        #d2=maintable[slot]
                        key=self.dicto[slot]
                        d2=client[key]
                        print ('Informed client to download file from disk: ',d2)
                        self.s.send(d2.encode())
                        string=self.s.recv(1024).decode()
                        log = open('/tmp/'+login+'/'+string, "r")
                        for line in log:
                            self.s.send(line.encode())

                    #List all files in a directory
                    elif operation[:4]=='list':
                        username=operation[5:]


                        username=self.s.recv(1024).decode()
                        host=socket.gethostbyname(socket.gethostname())
                        print (host)
                        lis=[]
                        lis=d[username]
                        for i in range(0,len(lis),2):
                          if (exists_remote(login+'@'+lis[i+1],'/tmp/'+login+'/'+username+'/'+lis[i])):
                            if (not exists_remote(login+'@'+host,'/tmp/'+login+'/'+username+'/'+lis[i])):

                                comm1='scp -B -q -o LogLevel=QUIET '+lis[i]+' '+login+'@'+lis[i+1]+':/tmp/'+login+'/'+username+'/ '+login+'@'+host+':/tmp/'+login+'/'+username+'/'
                                os.system(comm1)
                          elif (exists_remote(login+'@'+host,'/tmp/'+login+'/'+username+'/'+lis[i])):

                            comm1='scp -B -q -o LogLevel=QUIET '+lis[i]+' '+login+'@'+host+':/tmp/'+login+'/'+username+'/ '+login+'@'+lis[i+1]+':/tmp/'+login+'/'+username+'/'
                            os.system(comm1)

                        self.s.send(str(self.partitions).encode())
                        for i in range(self.partitions):
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

                        key=self.dicto[slot]
                        d2=client[key]

                        print ('Informed client to delete file from disk: ',d2)
                        self.s.send(d2.encode())

                    #Add disk operation
                    elif operation[:3]=='add':
                        ip=operation[4:]
                        print (ip+' added')
                        client.append(ip)
                        self.partitions += 1
                        self.reverse = added_partition_reverse_dictionary(self.partitions,self.reverse)
                        self.dicto = reverse_reverse_dicto(self.reverse)

                        list2=[]
                        list3=[]
                        for item in self.reverse[self.partitions-1]:

                            if item in addTable:

                                list2=addTable[item]
                                list3=list2[0].split('/')
                                comm1='scp -B '+list3[1]+' '+login+'@'+list2[1]+':/tmp/'+login+'/'+list3[0]+'/ '+login+'@'+client[self.partitions-1]+':/tmp/'+login+'/'+list3[0]+'/'
                                print ('file moved')
                                #update table to have new ip address
                                addTable.pop(item,None)
                                addTable[item]=[list2[0],client[self.partitions-1]]


                        for i,j in sorted(self.dicto.items(), reverse=True):
                            self.backup.update({i:j})

                    #Remove disk operation    
                    elif operation[:6]=='remove':
                        ip=operation[7:]
                        index=client.index(ip)

                        list2=[]
                        list3=[]
                        for item in self.reverse[index]:

                            if item in addTable:

                                list2=addTable[item]
                                list3=list2[0].split('/')
                                comm1='scp -B '+list3[1]+' '+login+'@'+list2[1]+':/tmp/'+login+'/'+list3[0]+'/ '+login+'@'+client[0]+':/tmp/'+login+'/'+list3[0]+'/'
                                #update table to have new ip address
                                addTable.pop(item,None)
                                addTable[item]=[list2[0],client[0]]

                        print (addTable)
                        for i,j in sorted(self.dicto.items(), reverse=True):
                            self.backup.update({i:j})
                        client.remove(ip)

                        self.partitions -= 1
                        self.reverse = delete_partition_reverse_dictionary(self.partitions,self.reverse)
                        self.dicto = reverse_reverse_dicto(self.reverse)
                        print (ip+' removed')

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

        while(j<len(command)):
            if command[j:j+11]=='129.210.16.' and command[j+11:j+13]>'79' and command [j+11:j+13]<='99':
                client.append(command[j:j+13])
                count=count+1
                j=j+14

            elif command[j:j+8]=='linux608' and command[j+8:j+10]>='10' and command[j+8:j+10]<='29':
                client.append(command[j:j+10])
                count=count+1
                j=j+11

            else:
                print('Try again, enter server command: ')
                command=input()
                continue
        flag=0
    else:
        print('Try again, enter server command: ')
        command=input()


#Main and backup tables
noOfdisks=len(client)

d={}
addTable={}
partitions = noOfdisks
dicto = initial_dictionary(partitions)
backup=initial_backup(partitions)
reverse = reverse_dicto(dicto)

#For client to connect to server
hostip = socket.gethostbyname(host)
print('host name is: ',host)
print('host ip is: ',hostip)
print ('port is: ',port)

#Connect to multiple clients using multithreading
while True:
    s1.listen(1)
    connection, address = s1.accept()
    newthread = SThread(address, connection,partitions,reverse,dicto,backup)
    newthread.start()
