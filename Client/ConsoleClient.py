import pymysql
import socket
import pickle
import pyaes, pbkdf2, binascii, os, secrets
import base64

global username, available_files, dirname

def getKey(): #generating key with PBKDF2 for AES
    password = "s3cr3t*c0d3"
    passwordSalt = '76895'
    key = pbkdf2.PBKDF2(password, passwordSalt).read(32)
    return key

def encrypt(plaintext): #AES data encryption
    aes = pyaes.AESModeOfOperationCTR(getKey(), pyaes.Counter(31129547035000047302952433967654195398124239844566322884172163637846056248223))
    ciphertext = aes.encrypt(plaintext)
    return ciphertext

def decrypt(enc): #AES data decryption
    aes = pyaes.AESModeOfOperationCTR(getKey(), pyaes.Counter(31129547035000047302952433967654195398124239844566322884172163637846056248223))
    decrypted = aes.decrypt(enc)
    return decrypted

def createDirectory():
    global username, dirname
    print("\nPlease enter directory name")
    dirname = input()
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    client.connect(('localhost', 2222))
    features = []
    features.append("createdir")
    features.append(username)
    features.append(dirname)
    features = pickle.dumps(features)
    client.send(features)
    data = client.recv(100)
    data = data.decode()

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    client.connect(('localhost', 3333))
    client.send(features)
    data = client.recv(100)
    data = data.decode()
    print(data+"\n")

def createFile():
    global username, dirname
    print("\nPlease enter directory name to create file")
    dirname = input()
    print("Please enter file name")
    filename = input()
    
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    client.connect(('localhost', 2222))
    features = []
    features.append("createfile")
    features.append(username)
    features.append(dirname)
    features.append(filename)
    features = pickle.dumps(features)
    client.send(features)
    data = client.recv(100)
    data = data.decode()
    available_files.append('files/'+username+"/"+dirname+"/"+filename)
    
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    client.connect(('localhost', 3333))
    client.send(features)
    print(data+"\n")

def getOldData(dirname, filename):
    global username
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    client.connect(('localhost', 2222))
    features = []
    features.append("readfile")
    features.append(username)
    features.append(dirname)
    features.append(filename)
    features = pickle.dumps(features)
    client.send(features)
    rec = client.recv(10000)
    dataset = pickle.loads(rec)
    request = dataset[0]
    data = ""
    if request == "correct":
        data = dataset[1]
    if len(data) > 0:
        data = base64.b64decode(data)
        data = decrypt(data)
        data = data.decode("utf-8")
    return data    

def writeFile():
    global username, text
    global dirname
    print("\nPlease enter directory name to write data")
    dirname = input()
    print("Please enter file name")
    filename = input()
    print("Please enter file content")
    filetext = input()
    oldData = getOldData(dirname, filename)
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    client.connect(('localhost', 2222))
    features = []
    features.append("writefile")
    features.append(username)
    features.append(dirname)
    features.append(filename)
    data = oldData+"\n"+filetext
    data = encrypt(data)
    data = str(base64.b64encode(data),'utf-8')
    features.append(data)
    features = pickle.dumps(features)
    client.send(features)
    data = client.recv(100)
    data = data.decode()
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('localhost', 3333))
    client.send(features)
    print(data+"\n")

def readFile():
    global username, dirname
   
    print("\nPlease enter directory name to read file")
    dirname = input()
    print("Please enter file name to read it")
    filename = input()
    
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    client.connect(('localhost', 2222))
    features = []
    features.append("readfile")
    features.append(username)
    features.append(dirname)
    features.append(filename)
    features = pickle.dumps(features)
    client.send(features)
    rec = client.recv(10000)
    dataset = pickle.loads(rec)
    request = dataset[0]
    if request == "correct":
        data = dataset[1]
        if len(data) > 0:
            data = base64.b64decode(data)
            data = decrypt(data)
            data = data.decode("utf-8")
        print("File Content Showing in Below lines\n\n")
        print(data)
        print("File Contenet ended here=================================")
    else:
        print("Given file does not exists\n")

def deleteFile():
    global username, dirname
    print("\nPlease enter directory name to delete a file")
    dirname = input()
    print("Please enter file name to delete it")
    filename = input()
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    client.connect(('localhost', 2222))
    features = []
    features.append("deletefile")
    features.append(username)
    features.append(dirname+"/"+filename)
    features = pickle.dumps(features)
    client.send(features)
    data = client.recv(100)
    data = data.decode()
    if data == 'Given file deleted':
        for i in range(len(available_files)):
            names = available_files[i]
            names = names.replace("\\","/")
            arr = names.split("/")
            if arr[3] == filename:
                del available_files[i]
    print(data+"\n")

def renameFile():
    global username, text
    global dirname

    print("\nPlease enter directory name to rename a file")
    dirname = input()
    print("Please enter old file name for renaming")
    oldname = input()
    print("Please enter new file name to rename")
    newname = input()
    
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    client.connect(('localhost', 2222))
    features = []
    features.append("renamefile")
    features.append(username)
    features.append(dirname)
    features.append(oldname)
    features.append(newname)
    features = pickle.dumps(features)
    client.send(features)
    data = client.recv(100)
    data = data.decode()
    for i in range(len(available_files)):
        names = available_files[i]
        names = names.replace("\\","/")
        arr = names.split("/")
        if arr[3] == oldname:
            del available_files[i]
    available_files.append('files/'+username+"/"+dirname+"/"+newname)        
    print(data+"\n")    

def listFiles():
    print("\nAvailable files for this user: "+username+"\n\n")
    for i in range(len(available_files)):
        print(available_files[i])
    print()
    
def print_menu():
    print("\n=====================================================\n")
    print("Enter 1 to Create Directory");
    print("Enter 2 to Create File");
    print("Enter 3 to Write File");
    print("Enter 4 to Read File");
    print("Enter 5 to Delete File");
    print("Enter 6 to Rename File");
    print("Enter 7 to List all files");
    print("Enter 8 to Exit");
    print("\n=====================================================\n")

def showMenu():
    global username, available_files
    while(True):
        print_menu()
        option = ''
        try:
            option = int(input('Enter your choice: '))
        except:
            print('Wrong input. Please enter a number ...')
        #Check what choice was entered and act accordingly
        if option == 1:
           createDirectory()
        elif option == 2:
            createFile()
        elif option == 3:
            writeFile()
        elif option == 4:
            readFile()
        elif option == 5:
            deleteFile()
        elif option == 6:
            renameFile()
        elif option == 7:
            listFiles()    
        elif option == 8:
            print('Successfully Logout. Bye')
            exit()
        else:
            print('Invalid option. Please enter a number between 1 and 7.')

def readFiles():
    global username, available_files
    if len(available_files) > 0:
        available_files.clear()
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    client.connect(('localhost', 2222))
    features = []
    features.append("listfiles")
    features.append(username)
    features = pickle.dumps(features)
    client.send(features)
    data = client.recv(10000)
    data = pickle.loads(data)
    for i in range(len(data)):
        available_files.append(data[i])
    

def validateLogin(usr, password):
    global username, available_files
    available_files = []
    
    output = "none"
    con = pymysql.connect(host='127.0.0.1',port = 3308,user = 'root', password = 'root', database = 'distributed',charset='utf8')
    with con:
        cur = con.cursor()
        cur.execute("select username, password FROM register")
        rows = cur.fetchall()
        for row in rows:
            if row[0] == usr and row[1] == password:
                output = "success"
                username = usr
                readFiles()
                break
    if output == "success":
        showMenu()
    else:
        print("Login Failed. Please Retry")

print("Please enter your username:")
usr = input()
print("Please enter your password:")
password = input()
validateLogin(usr, password)

















