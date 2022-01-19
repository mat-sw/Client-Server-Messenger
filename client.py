import os
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

        self.window = Tk()
        self.window.withdraw()

        self.login_window = Toplevel()

        # self.nickname = simpledialog.askstring("Login", "Enter your login: ", parent = msg)
        # self.nickname = simpledialog.askstring("Password", "Enter your password:", show = '*')

        self.login_window.configure(bg="lightgray")

        self.login_label = tkinter.Label(self.login_window, text="Login or register", bg="blue", width="200", height="2",
                                         font=("Calibri", 13)).pack(padx=20, pady=5)

        self.login_button = tkinter.Button(self.login_window, text="Login", height="2", width="30", command=self.login).pack(
            padx=20, pady=5)

        self.register_button = tkinter.Button(self.login_window, text="Register", height="2", width="30",
                                              command=self.register).pack(padx=20, pady=5)

        self.window.mainloop()


    def register(self):
        self.register_screen = tkinter.Toplevel(self.login_window)
        self.register_screen.title("Register")
        self.register_screen.geometry("200x200")

        self.register_label = tkinter.Label(self.register_screen, text="Please enter details below", bg="blue").pack(padx=20, pady=5)

        self.username = tkinter.StringVar(self.register_screen)
        self.password = tkinter.StringVar(self.register_screen)

        self.username_label = tkinter.Label(self.register_screen, text="Username * ")
        self.username_label.pack(padx=20, pady=5)

        self.username_entry = tkinter.Entry(self.register_screen, textvariable=self.username)
        self.username_entry.pack(padx=20, pady=5)

        self.password_label = tkinter.Label(self.register_screen, text="Password * ")
        self.password_label.pack(padx=20, pady=5)

        self.password_entry = tkinter.Entry(self.register_screen, textvariable=self.password, show='*')
        self.password_entry.pack(padx=20, pady=5)

        self.reg_button = tkinter.Button(self.register_screen, text="Register", width=10, height=1, bg="blue", command = self.register_user).pack(padx=20, pady=5)


    def register_user(self):
        username_info = self.username.get()
        password_info = self.password.get()

        file = open(username_info, "w")

        file.write(username_info + "\n")
        file.write(password_info)
        file.close()

        self.username_entry.delete(0,END)
        self.password_entry.delete(0,END)

        Label(self.register_screen, text = "Registration Success", fg = "green", font=("calibri", 11)).pack()


    def delete_login_success(self):
        self.login_sucess_screen.destroy()
        self.login_window.destroy()
        self.gui_done = False
        self.running = True

        gui_thread = threading.Thread(target=self.gui_loop)
        receive_thread = threading.Thread(target=self.receive)

        gui_thread.start()
        receive_thread.start()

    def login_sucess(self):
        self.login_sucess_screen = tkinter.Toplevel(self.login_screen)
        self.login_sucess_screen.title("Success")
        self.login_sucess_screen.geometry("150x100")
        Label(self.login_sucess_screen, text = "Login success").pack()

        Button(self.login_sucess_screen, text = "OK", command = self.delete_login_success).pack()


    def delete_password_not_recognised(self):
        self.password_not_recog_screen.destroy()


    def password_not_recognised(self):
        self.password_not_recog_screen = tkinter.Toplevel(self.login_screen)
        self.password_not_recog_screen.title("Unsuccess")
        self.password_not_recog_screen.geometry("150x100")

        Label(self.password_not_recog_screen, text = "Invalid password").pack()
        Button(self.password_not_recog_screen, text = "OK", command = self.delete_password_not_recognised).pack()

    def delete_user_not_found_screen(self):
        self.user_not_found_screen.destroy()

    def user_not_found(self):
        self.user_not_found_screen = tkinter.Toplevel(self.login_screen)
        self.user_not_found_screen.title("Unsuccess")
        self.user_not_found_screen.geometry("150x100")

        Label(self.user_not_found_screen, text = "User not found").pack()
        Button(self.user_not_found_screen, text = "OK", command = self.delete_user_not_found_screen).pack()

    def login_verification(self):
        username1 = self.username_verify.get()
        password1 = self.password_verify.get()

        self.username_login_entry.delete(0, END)
        self.password_login_entry.delete(0, END)

        self.list_of_files = os.listdir()

        if username1 in self.list_of_files:
            file1 = open(username1, "r")

            verify = file1.read().splitlines()
            if password1 in verify:
                self.login_sucess()
                self.nickname = username1
            else:
                self.password_not_recognised()

        else:
            self.user_not_found()


    def login(self):
        self.login_screen = tkinter.Toplevel(self.login_window)
        self.login_screen.title("Login")
        self.login_screen.geometry("200x200")

        self.login_lab = tkinter.Label(self.login_screen, text="Please enter details below to login", bg="blue").pack(padx=20, pady=5)

        self.username_verify = tkinter.StringVar(self.login_screen)
        self.password_verify = tkinter.StringVar(self.login_screen)

        Label(self.login_screen, text = "Username * ").pack()
        self.username_login_entry = tkinter.Entry(self.login_screen, textvariable = self.username_verify)
        self.username_login_entry.pack()

        Label(self.login_screen, text = "Password * ").pack()
        self.password_login_entry = tkinter.Entry(self.login_screen, textvariable = self.password_verify, show = '*')
        self.password_login_entry.pack()

        Button(self.login_screen, text = "Login", width = 10, height = 1, command = self.login_verification).pack()




    def gui_loop(self):
        self.win = tkinter.Tk()
        self.win.configure(bg="lightgray")

        self.chat_label = tkinter.Label(self.win, text="Chat:", bg="lightgray")
        self.chat_label.config(font=("Arial", 12))
        self.chat_label.pack(padx=20, pady=5)

        self.text_area = tkinter.scrolledtext.ScrolledText(self.win)
        self.text_area.pack(padx=20, pady=5)
        self.text_area.config(state='disabled')

        self.msg_label = tkinter.Label(self.win, text="Message:", bg="lightgray")
        self.msg_label.config(font=("Arial", 12))
        self.msg_label.pack(padx=20, pady=5)

        self.input_area = tkinter.Text(self.win, height=3)
        self.input_area.pack(padx=20, pady=5)

        self.send_button = tkinter.Button(self.win, text="Send:", command=self.write)
        self.send_button.config(font=("Arial", 12))
        self.send_button.pack(padx=20, pady=5)


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