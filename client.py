import socket
import threading
import tkinter
import tkinter.scrolledtext
from tkinter import simpledialog
from tkinter import *

HOST = '127.0.0.1'
PORT = 9090

class Client:

    def __init__(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))

        msg = tkinter.Tk()
        msg.geometry("200x200")
        msg.title("Login")
        msg.withdraw()

        # self.nickname = simpledialog.askstring("Login", "Enter your login: ", parent = msg)
        # self.nickname = simpledialog.askstring("Password", "Enter your password:", show = '*')

        self.gui_done = False
        self.running = True

        gui_thread = threading.Thread(target=self.gui_loop)
        receive_thread = threading.Thread(target=self.receive)

        gui_thread.start()
        receive_thread.start()

    def register(self):
        self.register_screen = tkinter.Toplevel(self.win)
        self.register_screen.title("Register")
        self.register_screen.geometry("200x200")

        self.register_label = tkinter.Label(self.register_screen, text="Please enter details below", bg="blue").pack(padx=20, pady=5)

        username = tkinter.StringVar(self.register_screen)
        password = tkinter.StringVar(self.register_screen)

        self.username_label = tkinter.Label(self.register_screen, text="Username * ")
        self.username_label.pack(padx=20, pady=5)

        self.username_entry = tkinter.Entry(self.register_screen, textvariable=username)
        self.username_entry.pack(padx=20, pady=5)

        self.password_label = tkinter.Label(self.register_screen, text="Password * ")
        self.password_label.pack(padx=20, pady=5)

        self.password_entry = tkinter.Entry(self.register_screen, textvariable=password, show='*')
        self.password_entry.pack(padx=20, pady=5)

        self.reg_button = tkinter.Button(self.register_screen, text="Register", width=10, height=1, bg="blue").pack(padx=20, pady=5)



    def gui_loop(self):


        self.win = tkinter.Tk()
        self.win.configure(bg="lightgray")

        self.login_label = tkinter.Label(self.win, text="Login or register", bg="blue", width="300", height="2",
                                         font=("Calibri", 13)).pack(padx=20, pady=5)

        self.login_button = tkinter.Button(self.win, text="Login", height="2", width="30").pack(padx=20, pady=5)

        self.register_button = tkinter.Button(self.win, text="Register", height="2", width="30", command = self.register).pack(padx=20, pady=5)


        # self.chat_label = tkinter.Label(self.win, text="Chat:", bg="lightgray")
        # self.chat_label.config(font=("Arial", 12))
        # self.chat_label.pack(padx=20, pady=5)
        #
        # self.text_area = tkinter.scrolledtext.ScrolledText(self.win)
        # self.text_area.pack(padx=20, pady=5)
        # self.text_area.config(state='disabled')
        #
        # self.msg_label = tkinter.Label(self.win, text="Message:", bg="lightgray")
        # self.msg_label.config(font=("Arial", 12))
        # self.msg_label.pack(padx=20, pady=5)
        #
        # self.input_area = tkinter.Text(self.win, height=3)
        # self.input_area.pack(padx=20, pady=5)
        #
        # self.send_button = tkinter.Button(self.win, text="Send:", command=self.write)
        # self.send_button.config(font=("Arial", 12))
        # self.send_button.pack(padx=20, pady=5)


        self.gui_done = True
        self.win.protocol("WM_DELETE", self.stop)
        self.win.mainloop()

    def stop(self):
        self.running = False
        self.win.destroy()
        self.sock.close()
        exit(0)

    def write(self):
        msg = f"{self.nickname} : {self.input_area.get('1.0', 'end')}"
        self.sock.send(msg.encode('utf-8'))
        self.input_area.delete('1.0', 'end')

    def receive(self):
        while self.running:
            try:
                msg = self.sock.recv(1024).decode('utf-8')
                if msg == 'NICK':
                    self.sock.send(self.nickname.encode('utf-8'))
                else:
                    if self.gui_done:
                        self.text_area.config(state='normal')
                        self.text_area.insert('end', msg)
                        self.text_area.yview('end')
                        self.text_area.config(state='disabled')
            except ConnectionAbortedError:
                break
            except:
                print("Error")
                self.sock.close()
                break

client = Client(HOST, PORT)