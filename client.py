import subprocess
import pipes
import socket
import os

#Check if file to be downloaded exists at remote location
def exists_remote(host, path):

    stat = subprocess.call(['ssh', host, 'test -e '+pipes.quote(path)])
    if stat == 0:
        return True
    if stat == 1:
        return False
    raise Exception('Failed')



s1 = socket.socket()

while True:
    #Client command to connect to server
    command=input('enter client command: ')

    #Extract host no. and port no.
    conn=command.split()
    host=conn[1]
    port=int(conn[2])

    #Check if ip address or host name is used to connect cliet to server
    if host[0]=='l':
        num=10
    else:
        num=13
    if len(host)!=num:
        print ('wrong command, try again!')
        continue

    #Connect to server
    try:
        s1.connect((host,port))
        break
    except:
        print ('wrong command, try again!')

login=os.environ['USER']

while True:

    #List of operations
    print (' ')
    print ('Menu: ')
    print ('1) upload')
    print ('2) download')
    print ('3) list')
    print ('4) delete')
    print ('5) Do you want to exit(yes/no)')

    #The operation to be performed
    operation=input('enter operation:')

    # To upload a file in a directory
    if operation[:7]=='upload ':
        string=operation[7:]
        s1.send(operation.encode())
        d2=s1.recv(1024).decode()

        index=string.find('/')
        username=string[:index]
        filename=string[index+1:]

        #Check if file to be uploaded exists
        if os.path.isfile('./'+filename):
            print ('uploaded file to: ',d2)
            pathname1='ssh '+d2+' mkdir -p /tmp/'+login+'/'+username
            pathname2='ssh '+host+' mkdir -p /tmp/'+login+'/'+username
            os.system(pathname1)
            os.system(pathname2)

            comm='scp -B '+filename+' '+login+'@'+host+':/tmp/'+login+'/'+username+'/'
            comm1='scp -B '+filename+' '+login+'@'+d2+':/tmp/'+login+'/'+username+'/'
            os.system(comm1)
            os.system(comm)
        else:
            print ('File not found!')

    #To download a file from a directory
    elif operation[:9]=='download ':
        string=operation[9:]
        s1.send(operation.encode())
        d2=s1.recv(1024).decode()

        index=string.find('/')
        username=string[:index]
        filename=string[index+1:]

        if (exists_remote(login+'@'+d2,'/tmp/'+login+'/'+string)):
            print('downloaded file from: ',d2)
            comm='scp -B '+login+'@'+d2+':/tmp/'+login+'/'+string+' .'
            os.system(comm)
        else:
            print('File not found!')

    #To list files in a directory
    elif operation[:4]=='list':
        username=operation[5:]
        print ('list is:')
        s1.send(operation.encode())

        if host[0]=='l':
            num=10
        else:
            num=13

        for i in range(4):
            d2=s1.recv(num).decode()
            print ('Disk: ',d2)
            os.system('ssh '+d2+' ls -lrt /tmp/'+login+'/'+username+'/')

    #To delete a file
    elif operation[:7]=='delete ':
        string=operation[7:]
        s1.send(operation.encode())

        d2=s1.recv(16).decode()
        index=string.find('/')
        username=string[:index]
        filename=string[index+1:]

        print('deleted file from: ',d2,' and ',host)
        pathname1='ssh '+login+'@'+d2+' rm -rf /tmp/'+login+'/'+string
        pathname2='ssh '+login+'@'+host+' rm -rf /tmp/'+login+'/'+string
        os.system(pathname1)
        os.system(pathname2)

    #To exit from the program
    elif operation[:3]=='yes':
        break
    elif operation[:2]=='no':
        continue

    #Entered the wrong operation command
    else:
        print ('You entered the wrong command')

s1.close()
