import socket
from tkinter import *
from pygame import mixer
import threading
import time
COLORS = [("RoyalBlue1", "RoyalBlue3")]
server_ip = "127.0.0.1"

# the main window for the program
class MainWindow:
    # input: none output: window to the screen. explanation: the main window.
    def __init__(self, master):
        self.master = master
        window_width = self.master.winfo_reqwidth()
        window_height = self.master.winfo_reqheight()
        self.master.protocol("WM_DELETE_WINDOW", self.quit)
        w, h = 500, 600
        self.master.geometry("{}x{}".format(w, h))
        self.main = Frame(self.master, width=w, height=h, bg=COLORS[0][1])
        self.main.pack()
        Label(self.main, fg="white", text="Welcome to YAHOOT!", font=('Bold', '36',), bg=COLORS[0][1]).place(x=6)
        self.join = Button(self.main, width=28, height=3, text="JOIN A QUIZ!",
                           command=lambda: self.move_page(self.main, "join"), font=('Bold', '16',), fg="white",
                           bg=COLORS[0][0], borderwidth=5, relief=RIDGE)
        self.join.place(x=80, y=80)
        self.create = Button(self.main, width=28, height=3, text="CREATE A QUIZ!",
                             command=lambda: self.move_page(self.main, "create"), font=('Bold', '16',), fg="white",
                             bg=COLORS[0][0], borderwidth=5, relief=RIDGE)
        self.create.place(x=80, y=200)
        self.make = Button(self.main, width=28, height=3, text="MAKE A QUIZ!",
                           command=lambda: self.move_page(self.main, "make"),
                           font=('Bold', '16',), fg="white", bg=COLORS[0][0], borderwidth=5, relief=RIDGE)
        self.make.place(x=80, y=320)
        self.up_down = Button(self.main, width=28, height=3, text="UPLOAD AND DOWNLOAD A QUIZ!",
                           command=lambda: self.move_page(self.main, "up"),
                           font=('Bold', '16',), fg="white", bg=COLORS[0][0], borderwidth=5, relief=RIDGE)
        self.up_down.place(x=80, y=440)

    # input: window, destination variable. output: moving to the desire window.
    def move_page(self, main, name=""):
        main.destroy()
        if name == "join":
            JoinWindow(self.master)
        elif name == "create":
            QuizWindow(self.master)
        elif name == "make":
            NameWindow(self.master)
        elif name == "up":
            UploadDownload(self.master)

    # input: none. output: closing the current window.
    def quit(self):
        root.destroy()


# the joining quiz window
class JoinWindow:
    def __init__(self, master):
        self.master = master
        self.master.title("JOIN YAHOOT!")
        self.master.protocol("WM_DELETE_WINDOW", self.quit)
        w, h = 500, 400
        self.master.geometry("{}x{}".format(w, h))
        self.main = Frame(self.master, width=w, height=h, bg=COLORS[0][1])
        self.main.pack()
        Label(self.main, text="Room ID", font=('Bold', '14'), fg="white", bg=COLORS[0][1]).place(x=25, y=80)
        Label(self.main, text="Password", font=('Bold', '14'), fg="white", bg=COLORS[0][1]).place(x=25, y=140)
        Label(self.main, text="name", font=('Bold', '14'), fg="white", bg=COLORS[0][1]).place(x=25, y=200)
        self.game_code1 = Entry(self.main, width=30, font=('Bold', '14'), fg="white", bg=COLORS[0][0], borderwidth=3,
                                relief=RIDGE)
        self.game_code1.place(x=115, y=80)
        self.game_code2 = Entry(self.main, width=30, font=('Bold', '14'), fg="white", bg=COLORS[0][0], borderwidth=3,
                                relief=RIDGE)
        self.game_code2.place(x=115, y=140)
        self.game_code3 = Entry(self.main, width=15, font=('Bold', '14'), fg="white", bg=COLORS[0][0], borderwidth=3,
                                relief=RIDGE)
        self.game_code3.place(x=85, y=200)
        self.b_join = Button(self.main, text="Join Game", font=('Bold', '14'), fg="white",
                             bg=COLORS[0][0], borderwidth=3, relief=RIDGE, command=lambda: self.join())
        self.b_join.place(x=84, y=260)
        b_back = Button(self.main, text="back", font=('Bold', '14'), fg="white",
                        bg=COLORS[0][0], borderwidth=3, relief=RIDGE, command=lambda: self.move_page(self.main))
        b_back.place(x=10, y=350)
        self.name = ""

    # input: none. output: moving the page back to the main window.
    def move_page(self, main,):
        main.destroy()
        MainWindow(self.master)

    # input: none. output: name, joining thread. explanation: starting a thread and taking  a given name.
    def join(self):
        self.name = self.game_code3.get()
        threading.Thread(target=lambda: self.joining()).start()

    # the window for the joining game
    def joining(self):
        # decrypting the Room ID
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        address_decrypt = ''
        for i in self.game_code1.get():
            address_decrypt += chr(ord(i) - 8)
        # establishing connection with the room creator
        client_socket.connect((address_decrypt, int(self.game_code2.get())))
        q_file = open("tamp_quiz\TAMP QUIZ.txt", "a")
        base = Frame(self.main, width=500, height=400, bg=COLORS[0][1])
        base.pack()
        Label(base, text="wait to start", font=('Bold', '24'), fg="white", bg=COLORS[0][1]).place(x=150, y=120)
        # sending the quiz file to the player
        data = client_socket.recv(8000)
        while data != b"o":
            q_file.write(data.decode("utf-8"))
            data = client_socket.recv(8000)
        q_file.close()
        question = []
        q_file = open("tamp_quiz\TAMP QUIZ.txt")
        # moving all the questions into array
        while True:
            data = q_file.readline()

            if data == "\n" or data == "":
                break
            if data[0] == "q":
                question.append([data[2:-1]])
            if data[0] == "t":
                question[-1].append(["t", data[2:-1]])
            if data[0] == "f":
                question[-1].append(["f", data[2:-1]])
        self.new_question(question, client_socket, base)
        q_file.close()

    # displaying the questions to the screen
    def new_question(self, question, c, b):

        base = Frame(b, width=500, height=400, bg=COLORS[0][1])
        base.pack()
        ans = ""
        self.wait = True
        self.win = True
        self.wins = 0

        qu = Label(base, fg="white", text="", font=('Bold', '24'), bg=COLORS[0][1],
                   borderwidth=2, relief=RIDGE, width=21)
        qu.place(x=45, y=40)
        self.b1 = Button(base, fg="white", text="", font=('Bold', '26'), bg="red",
                         borderwidth=4, relief=RIDGE, width=9, command=lambda: self.get_my_ans(ans, "a"))
        self.b1.place(x=45, y=120)
        self.b2 = Button(base, fg="white", text="", font=('Bold', '26'), bg="green",
                         borderwidth=4, relief=RIDGE, width=9, command=lambda: self.get_my_ans(ans, "b"))
        self.b2.place(x=260, y=120)
        self.b3 = Button(base, fg="white", text="", font=('Bold', '26'), bg="purple",
                         borderwidth=4, relief=RIDGE, width=9, command=lambda: self.get_my_ans(ans, "c"))
        self.b3.place(x=45, y=220)
        self.b4 = Button(base, fg="white", text="", font=('Bold', '26'), bg="blue",
                         borderwidth=4, relief=RIDGE, width=9, command=lambda: self.get_my_ans(ans, "d"))
        self.b4.place(x=260, y=220)

        # going over all the quistions and displaying to the screen
        for q in question:
            ans = ""
            self.wait = True
            qu.config(text=q[0])
            if q[1][0] == "t":
                self.b1.config(text=q[1][1])
                ans = q[1][1]
            else:
                self.b1.config(text=q[1][1])
            if q[2][0] == "t":
                self.b2.config(text=q[2][1])
                ans = q[2][1]
            else:
                self.b2.config(text=q[2][1])
            if q[3][0] == "t":
                self.b3.config(text=q[3][1])
                ans = q[3][1]
            else:
                self.b3.config(text=q[3][1])
            if q[4][0] != "":
                if q[4][0] == "t":
                    self.b4.config(text=q[4][1])
                    ans = q[4][1]
                else:
                    self.b4.config(text=q[4][1])
            while self.wait:
                pass
            else:
                if self.win:
                    win = Frame(base, width=500, height=400, bg="green")
                    win.place(x=0, y=0)
                    time.sleep(0.5)
                    win.destroy()
                else:
                    win = Frame(base, width=500, height=400, bg="red")
                    win.place(x=0, y=0)
                    time.sleep(0.5)
                    win.destroy()
        base = Frame(self.main, width=500, height=400, bg=COLORS[0][1])
        c.send((str(self.wins) + "/" + self.name).encode("utf-8"))
        base.place(x=0, y=0)
        winner = str(c.recv(1000))
        winner = winner[2:-1]
        Label(base, text="the winner is: \n" + str(winner), font=('Bold', '24'), fg="white",
              bg=COLORS[0][1]).place(x=50, y=120)
        q_file = open("tamp_quiz\TAMP QUIZ.txt", "w").close()

    def get_my_ans(self, ans, name):
        if name == "a":
            if self.b1["text"] == ans:
                self.wait = False
                self.win = True
                self.wins += 1
            else:
                self.wait = False
                self.win = False
        if name == "b":
            if self.b2["text"] == ans:
                self.wait = False
                self.win = True
                self.wins += 1
            else:
                self.wait = False
                self.win = False
        if name == "c":
            if self.b3["text"] == ans:
                self.wait = False
                self.win = True
                self.wins += 1
            else:
                self.wait = False
                self.win = False
        if name == "d":
            if self.b4["text"] == ans:
                self.wait = False
                self.win = True
                self.wins += 1
            else:
                self.wait = False
                self.win = False

    def quit(self):
        root.destroy()


# going to the select quiz window
class QuizWindow:
    def __init__(self, master):
        self.running = True
        self.master = master
        self.master.title("MAKE YAHOOT!")
        w, h = 500, 500
        self.master.geometry("{}x{}".format(w, h))
        self.main = Frame(self.master, width=w, height=h, bg=COLORS[0][1])
        self.main.pack()
        Label(self.main, bg=COLORS[0][1], font=('Bold', '18'), fg="white",
              text="Enter Your quiz name:").place(x=45, y=20)
        self.qq = Entry(self.main, width=30, font=('Bold', '18'), fg="white",
                            bg=COLORS[0][0], borderwidth=5, relief=RIDGE)
        self.qq.place(x=48, y=50)
        Label(self.main, bg=COLORS[0][1], font=('Bold', '18'), fg="white",
              text="Enter Your name:").place(x=45, y=110)
        self.entername = Entry(self.main, width=30, font=('Bold', '18'), fg="white",
                        bg=COLORS[0][0], borderwidth=5, relief=RIDGE)
        self.entername.place(x=48, y=140)
        self.join = Button(self.main, width=28, height=3, text="GO start A QUIZ!",
                           command=lambda: self.move_page(self.main), font=('Bold', '16',), fg="white",
                           bg=COLORS[0][0], borderwidth=5, relief=RIDGE)
        self.join.place(x=80, y=220)
        b_back = Button(self.main, text="back", font=('Bold', '14'), fg="white",
                        bg=COLORS[0][0], borderwidth=3, relief=RIDGE, command=lambda: self.move_back(self.main))
        b_back.place(x=10, y=450)

    # moving back to the main page
    def move_back(self, main, name=""):
        main.destroy()
        MainWindow(self.master)

    # moving the page to the waiting room
    def move_page(self, main):
        if not self.entername.get().strip(" ") == "":
            qq = self.qq.get()
            admin = self.entername.get().strip(" ")
            try:
                open("my quizs\\"+ qq+".txt")
                main.destroy()
                CreateWindow(self.master, qq+".txt", admin)
            except:
                print("not a real quiz")
        else:
            print("name cant be blank")


# the host room
class CreateWindow:
    def __init__(self, master, name, admin):
        self.master = master
        self.master.title("CREATE YAHOOT!")
        self.master.protocol("WM_DELETE_WINDOW", self.quit)
        w, h = 600, 400
        self.master.geometry("{}x{}".format(w, h))
        self.main = Frame(self.master, width=w, height=h, bg=COLORS[0][1])
        self.main.pack()
        self.points = []
        self.admin = admin
        """
        finding a free port--------------------------------------
        """
        tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp.bind(('', 0))
        address, port = tcp.getsockname()
        tcp.close()
        address = ip
        """
        ---------------------------------------------------------
        """
        threading.Thread(target=lambda: self.server(address, port)).start()
        self.run2 = True
        Button(self.main, text="start Game", font=('Bold', '14'), fg="white",
               bg=COLORS[0][0], borderwidth=3, relief=RIDGE, command=lambda: self.connecting(address, port)).place(x=250, y=300)
        self.q = name

    # connecting to the client
    def connecting(self, a, p):
        self.run2 = False
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((a, p))

    # making all the preparation in the waiting room
    def server(self, address, port):
        server_socket = socket.socket()
        server_socket.bind((address, port))
        server_socket.listen(15)
        """
        show ip and port
        """
        address_crypt = ''
        for i in address:
            address_crypt += chr(ord(i) + 8)


        Label(self.main, text=address_crypt + " Room ID", bg=COLORS[0][1], font=('Bold', '24'), fg="white").place(x=70,
                                                                                                             y=80)
        Label(self.main, text=str(port) + " Password", bg=COLORS[0][1], font=('Bold', '24'), fg="white").place(x=70,
                                                                                                               y=120)
        c_list = []

        while self.run2:
            s, a = server_socket.accept()
            c_list.append(s)
            print("accept")
        c_list.pop(-1)
        print("start")
        """
        start the game(send the word start)
        """
        time.sleep(0.1)
        q_file = open("my quizs\\"+ self.q)
        for c1 in c_list:
            for line in q_file:
                c1.send(line.encode('utf-8'))
            time.sleep(0.1)
            c1.send(b"o")
        q_file.close()
        question = []
        q_file = open("my quizs\\"+ self.q)
        while True:
            data = q_file.readline()

            if data == "\n" or data == "":
                break
            if data[0] == "q":
                question.append([data[2:-1]])
            if data[0] == "t":
                question[-1].append(["t", data[2:-1]])
            if data[0] == "f":
                question[-1].append(["f", data[2:-1]])

        for c2 in c_list:
            threading.Thread(target=lambda: self.listen(c2)).start()

        self.new_question(question, c_list)
        q_file.close()

    # counting all the score from the players
    def listen(self, soc):
        d = soc.recv(4096)
        d = d.decode()
        print(d)
        d = d.split("/")
        print(d)
        self.points.append([d[0], d[1]])

    # displaying all the questions to the screen
    def new_question(self, question, c_list):
        base = Frame(self.main, width=600, height=400, bg=COLORS[0][1])
        base.pack()
        ans = ""
        self.wait = True
        self.win = True
        self.wins = 0

        qu = Label(base, fg="white", text="", font=('Bold', '24'), bg=COLORS[0][1],
                   borderwidth=2, relief=RIDGE, width=21)
        qu.place(x=45, y=40)
        self.b1 = Button(base, fg="white", text="", font=('Bold', '26'), bg="red",
                         borderwidth=4, relief=RIDGE, width=9, command=lambda: self.get_my_ans(ans, "a"))
        self.b1.place(x=45, y=120)
        self.b2 = Button(base, fg="white", text="", font=('Bold', '26'), bg="green",
                         borderwidth=4, relief=RIDGE, width=9, command=lambda: self.get_my_ans(ans, "b"))
        self.b2.place(x=260, y=120)
        self.b3 = Button(base, fg="white", text="", font=('Bold', '26'), bg="purple",
                         borderwidth=4, relief=RIDGE, width=9, command=lambda: self.get_my_ans(ans, "c"))
        self.b3.place(x=45, y=220)
        self.b4 = Button(base, fg="white", text="", font=('Bold', '26'), bg="blue",
                         borderwidth=4, relief=RIDGE, width=9, command=lambda: self.get_my_ans(ans, "d"))
        self.b4.place(x=260, y=220)

        for q in question:
            ans = ""
            self.wait = True
            qu.config(text=q[0])
            if q[1][0] == "t":
                self.b1.config(text=q[1][1])
                ans = q[1][1]
            else:
                self.b1.config(text=q[1][1])
            if q[2][0] == "t":
                self.b2.config(text=q[2][1])
                ans = q[2][1]
            else:
                self.b2.config(text=q[2][1])
            if q[3][0] == "t":
                self.b3.config(text=q[3][1])
                ans = q[3][1]
            else:
                self.b3.config(text=q[3][1])
            if q[4][0] == "t":
                self.b4.config(text=q[4][1])
                ans = q[4][1]
            else:
                self.b4.config(text=q[4][1])
            while self.wait:
                pass
            else:
                if self.win:
                    win = Frame(base, width=500, height=400, bg="green")
                    win.place(x=0, y=0)
                    time.sleep(0.5)
                    win.destroy()
                else:
                    win = Frame(base, width=500, height=400, bg="red")
                    win.place(x=0, y=0)
                    time.sleep(0.5)
                    win.destroy()
        base = Frame(self.main, width=600, height=400, bg=COLORS[0][1])
        base.place(x=0, y=0)
        while True:
            if len(self.points) == len(c_list):
                break
        self.points.append([self.wins, self.admin])
        print(self.points)
        """
        send the winner(the one with the most points and if there is a tie so the first one who sent his answer will win
        """
        highscore = -1
        winner = ""
        for a in self.points:
            if int(a[0]) > highscore:
                highscore = int(a[0])
                winner = a[1]

        for d in c_list:
            d.send(winner.encode("utf-8"))
        Label(base, text="the winner(s) is(are)-\n" + winner, font=('Bold', '24'), fg="white",
              bg=COLORS[0][1]).place(x=50, y=120)

    # checking if your answer is the right one
    def get_my_ans(self, ans, name):
        if name == "a":
            if self.b1["text"] == ans:
                self.wait = False
                self.win = True
                self.wins += 1
            else:
                self.wait = False
                self.win = False
        if name == "b":
            if self.b2["text"] == ans:
                self.wait = False
                self.win = True
                self.wins += 1
            else:
                self.wait = False
                self.win = False
        if name == "c":
            if self.b3["text"] == ans:
                self.wait = False
                self.win = True
                self.wins += 1
            else:
                self.wait = False
                self.win = False
        if name == "d":
            if self.b4["text"] == ans:
                self.wait = False
                self.win = True
                self.wins += 1
            else:
                self.wait = False
                self.win = False

    # making the X button work
    def quit(self):
        root.destroy()


class NameWindow:
    def __init__(self, master):
        self.running = True
        self.master = master
        self.master.title("MAKE YAHOOT!")
        w, h = 500, 500
        self.master.geometry("{}x{}".format(w, h))
        self.main = Frame(self.master, width=w, height=h, bg=COLORS[0][1])
        self.main.pack()
        Label(self.main, bg=COLORS[0][1], font=('Bold', '18'), fg="white",
              text="Enter Your quiz name:").place(x=45, y=20)
        self.qq = Entry(self.main, width=30, font=('Bold', '18'), fg="white",
                            bg=COLORS[0][0], borderwidth=5, relief=RIDGE)
        self.qq.place(x=48, y=50)
        self.join = Button(self.main, width=28, height=3, text="GO MAKE A QUIZ!",
                           command=lambda: self.move_page(self.main), font=('Bold', '16',), fg="white",
                           bg=COLORS[0][0], borderwidth=5, relief=RIDGE)
        self.join.place(x=80, y=100)
        b_back = Button(self.main, text="back", font=('Bold', '14'), fg="white",
                        bg=COLORS[0][0], borderwidth=3, relief=RIDGE, command=lambda: self.move_back(self.main))
        b_back.place(x=10, y=450)

    def move_page(self, main):
        qq = self.qq.get()
        main.destroy()
        MakeWindow(self.master, qq+".txt")

    def move_back(self, main, name=""):
        main.destroy()
        MainWindow(self.master)


class MakeWindow:
    def __init__(self, master, q_name):
        self.running = True
        self.master = master
        self.master.title("MAKE YAHOOT!")
        self.master.protocol("WM_DELETE_WINDOW", self.quit)
        w, h = 500, 500
        self.master.geometry("{}x{}".format(w, h))
        self.main = Frame(self.master, width=w, height=h, bg=COLORS[0][1])
        self.main.pack()
        Label(self.main, bg=COLORS[0][1], font=('Bold', '18'), fg="white",
              text="Enter Your Question:").place(x=45, y=20)
        self.q_name = Entry(self.main, width=30, font=('Bold', '18'), fg="white",
                            bg=COLORS[0][0], borderwidth=5, relief=RIDGE)
        self.q_name.place(x=48, y=50)
        Label(self.main, bg=COLORS[0][1], font=('Bold', '18'), fg="white",
              text="Enter Your answers:").place(x=45, y=95)
        Label(self.main, bg=COLORS[0][1], font=('Bold', '11'), fg="white",
              text="*mark the right one ").place(x=45, y=120)
        self.var = IntVar()

        self.r1 = Radiobutton(self.main, value=1, variable=self.var, bg=COLORS[0][1])
        self.r1.place(x=48, y=149)
        self.q_1 = Entry(self.main, width=30, font=('Bold', '11'), fg="white", bg=COLORS[0][0], borderwidth=2,
                         relief=RIDGE)
        self.q_1.place(x=82, y=149)

        self.r2 = Radiobutton(self.main, value=2, variable=self.var, bg=COLORS[0][1])
        self.r2.place(x=48, y=179)
        self.q_2 = Entry(self.main, width=30, font=('Bold', '11'), fg="white", bg=COLORS[0][0], borderwidth=2,
                         relief=RIDGE)
        self.q_2.place(x=82, y=179)

        self.r3 = Radiobutton(self.main, value=3, variable=self.var, bg=COLORS[0][1])
        self.r3.place(x=48, y=209)
        self.q_3 = Entry(self.main, width=30, font=('Bold', '11'), fg="white", bg=COLORS[0][0], borderwidth=2,
                         relief=RIDGE)
        self.q_3.place(x=82, y=209)

        self.r4 = Radiobutton(self.main, value=4, variable=self.var, bg=COLORS[0][1])
        self.r4.place(x=48, y=239)
        self.q_4 = Entry(self.main, width=30, font=('Bold', '11'), fg="white", bg=COLORS[0][0], borderwidth=2,
                         relief=RIDGE)
        self.q_4.place(x=82, y=239)

        self.b_add = Button(self.main, text="Add question", font=('Bold', '11'), fg="white",
                            bg=COLORS[0][0], borderwidth=2, relief=RIDGE, command=lambda: self.add())
        self.b_add.place(x=48, y=270)
        self.q = q_name
        quizy = open("my quizs\\" + self.q, "w")

        b_back = Button(self.main, text="back", font=('Bold', '14'), fg="white",
                        bg=COLORS[0][0], borderwidth=3, relief=RIDGE, command=lambda: self.move_page(self.main))
        b_back.place(x=10, y=450)

    def move_page(self, main, name=""):
        main.destroy()
        MainWindow(self.master)

    def add(self):
        quiz = open("my quizs\\" + self.q, "a")
        if self.q_name.get() != "" and not self.var.get() == 0:
            quiz.write("q-" + self.q_name.get() + "\n")
            if self.var.get() == 1:
                quiz.write("t-" + self.q_1.get() + "\n")
            else:
                quiz.write("f-" + self.q_1.get() + "\n")
            if self.var.get() == 2:
                quiz.write("t-" + self.q_2.get() + "\n")
            else:
                quiz.write("f-" + self.q_2.get() + "\n")
            if self.var.get() == 3:
                quiz.write("t-" + self.q_3.get() + "\n")
            else:
                quiz.write("f-" + self.q_3.get() + "\n")
            if self.var.get() == 4:
                quiz.write("t-" + self.q_4.get() + "\n")
            else:
                quiz.write("f-" + self.q_4.get() + "\n")
            self.q_name.delete(0, 'end')
            self.q_1.delete(0, 'end')
            self.q_2.delete(0, 'end')
            self.q_3.delete(0, 'end')
            self.q_4.delete(0, 'end')
        quiz.close()

    def quit(self):
        root.destroy()


class UploadDownload:
    def __init__(self, master):
        self.running = True
        self.master = master
        self.master.title("MAKE YAHOOT!")
        self.master.protocol("WM_DELETE_WINDOW", self.quit)
        w, h = 500, 500
        self.master.geometry("{}x{}".format(w, h))
        self.main = Frame(self.master, width=w, height=h, bg=COLORS[0][1])
        self.main.pack()
        self.window_log_in()

    def move_page(self, main, name=""):
        main.destroy()
        MainWindow(self.master)

    def window_log_in(self):
        base = Frame(self.main, width=500, height=500, bg=COLORS[0][1])
        Label(base, text="Please Log In!", font=('Bold', '24'), fg="white", bg=COLORS[0][1]).place(x=155, y=10)
        Label(base, text="username:", font=('Bold', '14'), fg="white", bg=COLORS[0][1]).place(x=5, y=80)
        Label(base, text="password:", font=('Bold', '14'), fg="white", bg=COLORS[0][1]).place(x=5, y=140)
        username = Entry(base, width=30, font=('Bold', '14'), fg="white", bg=COLORS[0][0], borderwidth=3,
                                relief=RIDGE)
        username.place(x=105, y=80)
        password = Entry(base, width=30, font=('Bold', '14'), fg="white", bg=COLORS[0][0], borderwidth=3,
                                relief=RIDGE, show="*")
        password.place(x=105, y=140)
        b_join = Button(base, text="LOG IN", font=('Bold', '14'), fg="white",
                             bg=COLORS[0][0], borderwidth=3, relief=RIDGE, command=lambda: self.logg(username.get(), password.get(), base))
        b_join.place(x=104, y=180)
        b_reg = Button(base, text="register", font=('Bold', '14'), fg="white",
                             bg=COLORS[0][0], borderwidth=3, relief=RIDGE, command=lambda: self.register(base))
        b_reg.place(x=214, y=180)
        b_back = Button(base, text="back", font=('Bold', '14'), fg="white",
                       bg=COLORS[0][0], borderwidth=3, relief=RIDGE, command=lambda: self.move_page(self.main))
        b_back.place(x=10, y=450)
        base.pack()

    # the registering function
    def register(self,base):
        base.destroy()
        bases = Frame(self.main, width=500, height=500, bg=COLORS[0][0])
        bases.pack()
        Label(bases, text="Welcome to Yahoot!", font=('Bold', '24'), fg="white", bg=COLORS[0][0]).place(x=135, y=10)
        Label(bases, text="username:", font=('Bold', '14'), fg="white", bg=COLORS[0][0]).place(x=5, y=80)
        Label(bases, text="password:", font=('Bold', '14'), fg="white", bg=COLORS[0][0]).place(x=5, y=140)
        username = Entry(bases, width=30, font=('Bold', '14'), fg="white", bg=COLORS[0][0], borderwidth=3,
                         relief=RIDGE)
        username.place(x=105, y=80)
        password = Entry(bases, width=30, font=('Bold', '14'), fg="white", bg=COLORS[0][0], borderwidth=3,
                         relief=RIDGE, show="*")
        password.place(x=105, y=140)
        b_join = Button(bases, text="register", font=('Bold', '14'), fg="white",
                        bg=COLORS[0][0], borderwidth=3, relief=RIDGE, command=lambda: self.reg(username.get(), password.get(), bases))
        b_join.place(x=104, y=180)
        b_back = Button(bases, text="back", font=('Bold', '14'), fg="white",
                        bg=COLORS[0][0], borderwidth=3, relief=RIDGE, command=lambda: self.move_page(self.main))
        b_back.place(x=10, y=450)

    # making a new user
    def reg(self, username, password, bases):
        if username != "" and password != "":

                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_socket.connect((server_ip, 8080))
                client_socket.send(("(REG)+"+username+"+"+password).encode('utf-8'))
                data = client_socket.recv(4096)
                print(data)
                if data == b"true":
                    bases.destroy()
                    self.window_log_in()
                else:
                    print("username is taken")
                client_socket.close()

        else:
            print("the filds can't be blank")

    # logging into the server
    def logg(self, username, password, bases):
        if username != "" and password != "":

                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_socket.connect((server_ip, 8080))
                client_socket.send(("(LOG)+"+username+"+"+password).encode('utf-8'))
                data = client_socket.recv(4096)
                print(data)
                if data == b"true":
                    bases.destroy()
                    self.main.destroy()
                    UploadDownload2(self.master, username)
                else:
                    print("try again")
                client_socket.close()

        else:
            print("the filds can't be blank")

    def quit(self):
            root.destroy()


# upload and download quiz from the server
class UploadDownload2:
    def __init__(self, master, name):
        self.running = True
        self.master = master
        self.master.title("YAHOOT!")
        self.master.protocol("WM_DELETE_WINDOW", self.quit)
        w, h = 500, 500
        self.master.geometry("{}x{}".format(w, h))
        self.main = Frame(self.master, width=w, height=h, bg=COLORS[0][1])
        self.main.pack()
        self.name = name
        print(self.name)
        Label(self.main, bg=COLORS[0][1], font=('Bold', '18'), fg="white",
              text="Enter quiz name:").place(x=45, y=20)
        self.search = Entry(self.main, width=30, font=('Bold', '18'), fg="white",
                        bg=COLORS[0][0], borderwidth=5, relief=RIDGE)
        self.search.place(x=48, y=50)
        self.up = Button(self.main, width=15, height=2, text="UPLOAD the QUIZ!",
                           command=lambda: self.upload(), font=('Bold', '12',), fg="white",
                           bg=COLORS[0][0], borderwidth=5, relief=RIDGE)
        self.up.place(x=48, y=100)
        self.down = Button(self.main, width=18, height=2, text="DOWNLOAD the QUIZ!",
                         command=lambda: self.download(), font=('Bold', '12',), fg="white",
                         bg=COLORS[0][0], borderwidth=5, relief=RIDGE)
        self.down.place(x=200, y=100)
        b_back = Button(self.main, text="back", font=('Bold', '14'), fg="white",
                        bg=COLORS[0][0], borderwidth=3, relief=RIDGE, command=lambda: self.move_page(self.main))
        b_back.place(x=10, y=450)

    def move_page(self, main, name=""):
        main.destroy()
        MainWindow(self.master)

    def upload(self):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((server_ip, 8080))
        run = False
        try:
            q_file = open("my quizs\\" + self.search.get() + ".txt")
            q_file.close()
            run = True
        except:
            run = False
            client_socket.send(b"o")

        if run:
            client_socket.send(("(up)+"+ self.search.get()+"-"+self.name+".txt").encode('utf-8'))
            time.sleep(0.2)
            q_file = open("my quizs\\" + self.search.get()+".txt")
            for line in q_file:
                client_socket.send(line.encode('utf-8'))
            time.sleep(0.1)
            client_socket.send(b"o")
            q_file.close()
        client_socket.close()

    def download(self):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((server_ip, 8080))
        client_socket.send(("(down)+" + self.search.get()).encode('utf-8'))
        d = client_socket.recv(4096)
        if b"-" in d:
            d = d.decode("utf-8")
            file = open("my quizs\\" + d, "w").close()
            q_file = open("my quizs\\" + d, "a")
            data = client_socket.recv(8000)
            while data != b"o":
                q_file.write(data.decode("utf-8"))
                data = client_socket.recv(8000)
            q_file.close()
        else:
            print("not such quiz")
        client_socket.close()

    def quit(self):
        root.destroy()
"""
main code
"""

def music():
        mixer.init()
        mixer.music.load('yhaoot_song.mp3')
        mixer.music.play(-1)


music()
root = Tk()
root.title("Yahoot!")
root.resizable(False, False)
ip = socket.gethostbyname(socket.gethostname())
MainWindow(root)
root.mainloop()
quit()

"""
end of code
"""
