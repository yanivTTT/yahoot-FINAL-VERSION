import socket
import select
import sqlite3
from os import listdir
from os.path import isfile, join
import time
conn = sqlite3.connect("data.db")
c = conn.cursor()
server_socket = socket.socket()
server_socket.bind(("0.0.0.0", 8080))
server_socket.listen(255)
open_client_sockets = []


# registering and adding it into the Database
def register(name, password):
    c.execute("SELECT * FROM users")
    data = c.fetchall()
    u = name
    p = password
    for line in data:
        if line[0] == name:
            return False
    c.execute('INSERT INTO users (username, password) VALUES(? ,? )', (u, p))
    conn.commit()
    return True


# checking if the name and password are correct
def log_in(name, password):
    c.execute("SELECT * FROM users")
    d = c.fetchall()
    for line in d:
        if line[0] == name:
            if line[1] == password:
                return True
            return False
    return False


# uploading a quiz file into the server
def upload(conn, name):
    file = open("quizs\\"+ name, "w").close()
    q_file = open("quizs\\"+ name, "a")
    data = conn.recv(8000)
    while data != b"o":
        q_file.write(data.decode("utf-8"))
        data = conn.recv(8000)
    q_file.close()


# sending the file to the client
def down(conn, name):
    search = []
    onlyfiles = [f for f in listdir("quizs") if isfile(join("quizs", f))]
    for i in onlyfiles:
        if name+".txt" == i:
            search.append(i)
    if len(search)>0:
        conn.send(search[0].encode("utf-8"))
        time.sleep(0.2)
        q_file = open("quizs\\" + search[0])
        for line in q_file:
            conn.send(line.encode('utf-8'))
        time.sleep(0.1)
        conn.send(b"o")
        q_file.close()
    else:
        conn.send(b"f")


while True:
    rlist, wlist, xlist = select.select([server_socket] + open_client_sockets, [], [])
    for current_socket in rlist:
        if current_socket is server_socket:
            (new_socket, address) = server_socket.accept()
            open_client_sockets.append(new_socket)
        else:
            try:
                try:
                    data = current_socket.recv(4096)
                    data = str(data)
                    data = data[2:-1]
                except ConnectionResetError:
                    open_client_sockets.remove(current_socket)
                finally:
                    pass
                if data == "":
                    open_client_sockets.remove(current_socket)
                else:
                    try:
                        data = data.split("+")
                        print(data)
                    except:
                        pass
                    if data[0] == "(REG)":
                        """
                        (REG)+username+password
                        """
                        if register(data[1], data[2]):
                            print("t")
                            current_socket.send(b"true")
                        else:
                            print("f")
                            current_socket.send(b"false")

                    elif data[0] == "(LOG)":
                        """
                        (LOG)+username+password
                        """
                        if log_in(data[1], data[2]):
                            current_socket.send(b"true")
                        else:
                            current_socket.send(b"false")

                    elif data[0] == "(up)":
                        """
                        (up)+filename
                                                """
                        upload(current_socket, data[1])
                        current_socket.send(b"true")

                    elif data[0] == "(down)":
                        """
                        (down)+filename
                        """
                        down(current_socket, data[1])
                        current_socket.send(b"true")

            except:
                pass
