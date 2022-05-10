import pymysql
from tkinter import messagebox
from tkinter import *
from tkinter import simpledialog
import tkinter
from tkinter import ttk
import socket
import pickle
import pyaes, pbkdf2
import base64

main = tkinter.Tk()
main.title("Distributed File System") 
main.maxsize(width=500 ,  height=300)
main.minsize(width=500 ,  height=300)

global login_user, login_pass, sign_user, sign_pass, contact, username, count, winsignup, winlogin, text, dirname, filecombo, accessList
count = 0
global available_files

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
    global username, text
    global dirname
    dirname = simpledialog.askstring(title="Please enter directory name", prompt="Please enter directory name")
    dirname = encrypt(dirname)
    dirname = str(base64.b64encode(dirname),'utf-8')
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    client.connect(('localhost', 2223))
    features = []
    features.append("createdir")
    features.append(username)
    features.append(dirname)
    features = pickle.dumps(features)
    client.send(features)
    data = client.recv(100)
    data = data.decode()

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    client.connect(('localhost', 2224))
    client.send(features)
    data = client.recv(100)
    data = data.decode()
    text.insert(END,data+"\n")
    
def createFile():
    global username, text
    global dirname
    dirname = simpledialog.askstring(title="Please enter directory name", prompt="Please enter directory name")
    filename = simpledialog.askstring(title="Please enter file name", prompt="Please enter file name")
    dirname = encrypt(dirname)
    dirname = str(base64.b64encode(dirname),'utf-8')
    filename = encrypt(filename)
    filename = str(base64.b64encode(filename),'utf-8')
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    client.connect(('localhost', 2223))
    features = []
    features.append("createfile")
    features.append(username)
    features.append(dirname)
    features.append(filename)
    features = pickle.dumps(features)
    client.send(features)
    data = client.recv(100)
    data = data.decode()
    dirname = base64.b64decode(dirname)
    dirname = decrypt(dirname)
    dirname = dirname.decode("utf-8")
    filename = base64.b64decode(filename)
    filename = decrypt(filename)
    filename = filename.decode("utf-8")
    available_files.append('files/'+username+"/"+dirname+"/"+filename)
    filecombo['values'] = available_files

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    client.connect(('localhost', 2224))
    client.send(features)
    text.insert(END,data+"\n")

def deleteFile():
    global username, text
    global dirname
    dirname = simpledialog.askstring(title="Please enter directory name to delete", prompt="Please enter directory name to delete")
    filename = simpledialog.askstring(title="Please enter file name to delete", prompt="Please enter file name to delete")
    dirname = encrypt(dirname)
    dirname = str(base64.b64encode(dirname),'utf-8')
    filename = encrypt(filename)
    filename = str(base64.b64encode(filename),'utf-8')
    '''dirname = filecombo.get()
    dirname = dirname.replace("\\","/")
    arr = dirname.split("/")
    usernames = arr[1]
    dirname = arr[2]+"/"+arr[3]'''
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    client.connect(('localhost', 2223))
    features = []
    features.append("deletefile")
    features.append(username)
    features.append(dirname+"/"+filename)
    features = pickle.dumps(features)
    client.send(features)
    data = client.recv(100)
    data = data.decode()
    for i in range(len(available_files)):
        names = available_files[i]
        names = names.replace("\\","/")
        arr = names.split("/")
        if arr[3] == filename:
            del available_files[i]
    text.insert(END,data+"\n")    
    
def writeFile():
    global username, text
    global dirname
    # dirname = simpledialog.askstring(title="Please enter directory name", prompt="Please enter directory name")
    # filename = simpledialog.askstring(title="Please enter file name", prompt="Please enter file name")
    # dirname = encrypt(dirname)
    # dirname = str(base64.b64encode(dirname),'utf-8')
    # filename = encrypt(filename)
    # filename = str(base64.b64encode(filename),'utf-8')
    dirname = filecombo.get()
    dirname = dirname.replace("\\","/")
    arr = dirname.split("/")
    current_name = arr[1]
    dirname = arr[2]
    filename = arr[3]
    dirname = encrypt(dirname)
    dirname = str(base64.b64encode(dirname),'utf-8')
    filename = encrypt(filename)
    filename = str(base64.b64encode(filename),'utf-8')
    #current_name = username
    status = 'none'
    if current_name != username:
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'toor@123', database = 'distributed',charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("select access_mode FROM access where user='"+username+"' and filename='"+filecombo.get()+"'")
            rows = cur.fetchall()
            for row in rows:
                status = row[0]        
    if current_name == username or status == 'Write':
        filetext = simpledialog.askstring(title="Please enter file content", prompt="Please enter file content")
        filetext = encrypt(filetext)
        filetext = str(base64.b64encode(filetext),'utf-8')
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        client.connect(('localhost', 2223))
        features = []
        features.append("writefile")
        features.append(current_name)
        features.append(dirname)
        features.append(filename)
        features.append(filetext)
        features = pickle.dumps(features)
        client.send(features)
        data = client.recv(100)
        data = data.decode()
        text.insert(END,data+"\n")

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        client.connect(('localhost', 2224))
        features = pickle.dumps(features)
        client.send(features)
    else:
        messagebox.showinfo("You dont have permission to write to this file",username + "You dont have permission to write to this file" + current_name)
        

def shareAccess():
    global username, text, accessList
    global dirname
    dirname = filecombo.get()
    dirname = dirname.replace("\\","/")
    share_user = simpledialog.askstring(title="Please enter username to share file with", prompt="Please enter username to share file with")
    access_mode = accessList.get()

    db_connection = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'toor@123', database = 'distributed',charset='utf8')
    db_cursor = db_connection.cursor()
    student_sql_query = "INSERT INTO access(owner,user,filename,access_mode) VALUES('"+username+"','"+share_user+"','"+dirname+"','"+access_mode+"')"
    db_cursor.execute(student_sql_query)
    db_connection.commit()
    messagebox.showinfo("File access control details saved in database","File access control details saved in database")

def readFile():
    global username, text
    global dirname
    text.delete('1.0', END)
    # dirname = simpledialog.askstring(title="Please enter directory name", prompt="Please enter directory name")
    # filename = simpledialog.askstring(title="Please enter file name", prompt="Please enter file name")
   
    dirname = filecombo.get()
    dirname = dirname.replace("\\","/")
    arr = dirname.split("/")
    usernames = arr[1]
    dirname = arr[2]
    filename = arr[3]
    dirname = encrypt(dirname)
    dirname = str(base64.b64encode(dirname),'utf-8')
    filename = encrypt(filename)
    filename = str(base64.b64encode(filename),'utf-8')
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    client.connect(('localhost', 2223))
    features = []
    features.append("readfile")
    features.append(usernames)
    features.append(dirname)
    features.append(filename)
    features = pickle.dumps(features)
    client.send(features)
    rec = client.recv(10000)
    dataset = pickle.loads(rec)
    request = dataset[0]
    if request == "correct":
        data = dataset[1]
        data = base64.b64decode(data)
        data = decrypt(data)
        data = data.decode("utf-8")
        text.insert(END,"File Content Showing in Below lines\n\n")
        text.insert(END,data)
    else:
        text.insert(END,"files does not exists\n")    


def renameFile():
    global username, text
    global dirname
    '''dirname = filecombo.get()
    dirname = dirname.replace("\\","/")
    arr = dirname.split("/")
    usernames = arr[1]
    dirname = arr[2]
    oldname = arr[3]'''
    dirname = simpledialog.askstring(title="Please enter directory name", prompt="Please enter directory name")
    oldname = simpledialog.askstring(title="Please enter old file name", prompt="Please enter old file name")
    newname = simpledialog.askstring(title="Please enter new file name", prompt="Please enter new file name")
    dirname = encrypt(dirname)
    dirname = str(base64.b64encode(dirname),'utf-8')
    oldname = encrypt(oldname)
    oldname = str(base64.b64encode(oldname),'utf-8')
    newname = encrypt(newname)
    newname = str(base64.b64encode(newname),'utf-8')
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    client.connect(('localhost', 2223))
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
    available_files.append('files/'+username+"/"+dirname+"/"+newname)
    for i in range(len(available_files)):
        if oldname in available_files:
            old = available_files[i]
            available_files.remove(old)
    filecombo['values'] = available_files
    text.insert(END,data+"\n")



def fileSystem():
    global username, text, available_files, filecombo, accessList
    fs = tkinter.Tk()
    fs.title("Distributed File System Client Screen")
    fs.maxsize(width=1300 ,  height=900)
    fs.minsize(width=1300 ,  height=900)
    font1 = ('times', 13, 'bold')

    cdButton = Button(fs, text="Create Directory", command=createDirectory)
    cdButton.place(x=50,y=100)
    cdButton.config(font=font1)

    cfButton = Button(fs, text="Create File", command=createFile)
    cfButton.place(x=300,y=100)
    cfButton.config(font=font1)

    filecombo = ttk.Combobox(fs,values=available_files,postcommand=lambda: filecombo.configure(values=available_files))
    filecombo.place(x=50,y=150)
    if len(available_files) > 0:
        filecombo.current(0)
    filecombo.config(font=font1)

    dfButton = Button(fs, text="Delete File", command=deleteFile)
    dfButton.place(x=300,y=150)
    dfButton.config(font=font1)

    rfButton = Button(fs, text="Read File", command=readFile)
    rfButton.place(x=50,y=200)
    rfButton.config(font=font1)

    wfButton = Button(fs, text="Write File", command=writeFile)
    wfButton.place(x=300,y=200)
    wfButton.config(font=font1)

    renButton = Button(fs, text="Rename File", command=renameFile)
    renButton.place(x=50,y=250)
    renButton.config(font=font1)

    saButton = Button(fs, text="Share Access", command=shareAccess)
    saButton.place(x=300,y=250)
    saButton.config(font=font1)

    accessList = ttk.Combobox(fs,values=['Read', 'Write'],postcommand=lambda: filecombo.configure(values=['Read', 'Write']))
    accessList.place(x=450,y=250)
    accessList.current(0)
    accessList.config(font=font1)

    text=Text(fs,height=15,width=120)
    scroll=Scrollbar(text)
    text.configure(yscrollcommand=scroll.set)
    text.place(x=10,y=300)
    text.config(font=font1)

    fs.config(bg='chocolate1')
    fs.mainloop()

def readFiles():
    global username, available_files
    if len(available_files) > 0:
        available_files.clear()
    available_files.append("Available Files")
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    client.connect(('localhost', 2223))
    features = []
    features.append("listfiles")
    features.append(username)
    features = pickle.dumps(features)
    client.send(features)
    data = client.recv(10000)
    data = pickle.loads(data)
    for i in range(len(data)):
        available_files.append(data[i])

    con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'toor@123', database = 'distributed',charset='utf8')
    with con:
        cur = con.cursor()
        cur.execute("select filename FROM access where user='"+username+"'")
        rows = cur.fetchall()
        for row in rows:
            available_files.append(row[0])

    

def validateLogin():
    global login_user, login_pass, username, available_files
    available_files = []
    usr = login_user.get()
    password = login_pass.get()

    output = "none"
    con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'toor@123', database = 'distributed',charset='utf8')
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
        winlogin.destroy()
        fileSystem()
    else:
        messagebox.showinfo("Login Failed. Please Retry")
                

def signupAction():
    global sign_user, sign_pass, contact, username, count, winsignup
    usr = sign_user.get()
    password = sign_pass.get()
    contactno = contact.get()

    output = "none"
    con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'toor@123', database = 'distributed',charset='utf8')
    with con:
        cur = con.cursor()
        cur.execute("select username FROM register")
        rows = cur.fetchall()
        for row in rows:
            if row[0] == usr:
                output = username+" Username already exists"
                break                
        if output == "none":
            db_connection = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'toor@123', database = 'distributed',charset='utf8')
            db_cursor = db_connection.cursor()
            student_sql_query = "INSERT INTO register(username,password,contact) VALUES('"+usr+"','"+password+"','"+contactno+"')"
            db_cursor.execute(student_sql_query)
            db_connection.commit()
            print(db_cursor.rowcount, "Record Inserted")
            if db_cursor.rowcount == 1:
                output = "Signup process completed. You can login now"
                count = 2
                messagebox.showinfo(output,output)
                winsignup.destroy()
                loginFunction()
        else:
            messagebox.showinfo(output,output)

    
def loginFunction():
    global login_user, login_pass, count, winlogin
    if count == 0:
        main.destroy()
        count = 1
    winlogin = tkinter.Tk()
    winlogin.title("User Login Screen")
    winlogin.maxsize(width=500 ,  height=300)
    winlogin.minsize(width=500 ,  height=300)
	
    l1 = Label(winlogin, text='Login Screen')
    l1.config(font=font1)
    l1.place(x=140,y=30)

    l2 = Label(winlogin, text='Username')
    l2.config(font=font1)
    l2.place(x=50,y=80)

    login_user = Entry(winlogin,width=35)
    login_user.config(font=font1)
    login_user.place(x=150,y=80)

    l3 = Label(winlogin, text='Password')
    l3.config(font=font1)
    l3.place(x=50,y=130)

    login_pass = Entry(winlogin,width=35, show="*")
    login_pass.config(font=font1)
    login_pass.place(x=150,y=130)

    login1Button = Button(winlogin, text="Submit", command=validateLogin)
    login1Button.place(x=100,y=180)
    login1Button.config(font=font1)

    winlogin.mainloop()

def signupFunction():
    main.destroy()
    global sign_user, sign_pass, contact, winsignup
    winsignup = tkinter.Tk()
    winsignup.title("New User Signup Screen")
    winsignup.maxsize(width=500 ,  height=400)
    winsignup.minsize(width=500 ,  height=400)
	
    l1 = Label(winsignup, text='New User Signup Screen')
    l1.config(font=font1)
    l1.place(x=140,y=30)

    l2 = Label(winsignup, text='Username')
    l2.config(font=font1)
    l2.place(x=50,y=80)

    sign_user = Entry(winsignup,width=35)
    sign_user.config(font=font1)
    sign_user.place(x=150,y=80)

    l3 = Label(winsignup, text='Password')
    l3.config(font=font1)
    l3.place(x=50,y=130)

    sign_pass = Entry(winsignup,width=35, show="*")
    sign_pass.config(font=font1)
    sign_pass.place(x=150,y=130)

    l4 = Label(winsignup, text='Contact No')
    l4.config(font=font1)
    l4.place(x=50,y=180)

    contact = Entry(winsignup,width=25)
    contact.config(font=font1)
    contact.place(x=150,y=180)

    sign1Button = Button(winsignup, text="Submit", command=signupAction)
    sign1Button.place(x=100,y=230)
    sign1Button.config(font=font1)

    winsignup.mainloop()

def closeFunction():
    main.destroy()


font = ('times', 16, 'bold')
title = Label(main, text='Distributed File System Client Application',anchor='w')
title.config(bg='darkviolet', fg='gold')  
title.config(font=font)           
title.config(height=3, width=120)       
title.place(x=0,y=5)

font1 = ('times', 12, 'bold')

loginButton = Button(main, text="Login Here", command=loginFunction)
loginButton.place(x=100,y=100)
loginButton.config(font=font1)

loginButton = Button(main, text="New User Signup Here", command=signupFunction)
loginButton.place(x=100,y=150)
loginButton.config(font=font1)

exitButton = Button(main, text="Exit", command=closeFunction)
exitButton.place(x=100,y=200)
exitButton.config(font=font1)

main.config(bg='turquoise')
main.mainloop()


