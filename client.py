from email import message
from email.errors import FirstHeaderLineIsContinuationDefect
import os
import socket
import threading
import tkinter
import tkinter.scrolledtext
from tkinter import simpledialog
from tkinter import *
import glob

HOST = '192.168.1.19'
PORT = 9090

""" Czyści wiadomość ze znaków białych na początku i na końcu + ewentualnie z dziwnych i niechcianych znaczków odbieranych z serwera """
def trim_recv_msg(message):
    splitted = message.split(' : ', 1)
    if splitted[1][0] == '\n':
        return ""
    end = 1
    while splitted[1][end] != '\n':
        end += 1
    text = splitted[1][:end]
    return " : ".join([splitted[0], text])


def trim_send_msg(message):
    splitted = message.split(' : ', 1)
    if len(splitted[1]) <= 1:
        return ""
    start = 0
    end = len(splitted[1])
    while (splitted[1][start] in [' ', '\n']) and (start < len(splitted[1])):
        start += 1
    while splitted[1][end - 1] in [' ', '\n'] and end > start:
        end -= 1
    text = splitted[1][start:end]
    return " : ".join([splitted[0], text])

class Client:
    def __init__(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        self.send_from_enter = False

        self.window = Tk()
        self.window.withdraw()

        self.chats = []

        self.login_window = Toplevel()
        self.login_window.geometry("300x300")
        self.login_window.title("Login")

        self.login_window.configure(bg="lightgray")

        self.login_label = tkinter.Label(self.login_window, text="Login or register", bg="lightblue", width="200", height="2",
                                         font=("Calibri", 13)).pack(padx=10, pady=10)

        self.login_button = tkinter.Button(self.login_window, text="Login", height="2", width="30", command=self.login).pack(padx=10, pady=10)

        self.register_button = tkinter.Button(self.login_window, text="Register", height="2", width="30",
                                              command=self.register).pack(padx=10, pady=10)

        self.window.mainloop()

    """ Rejestracja """
    def register(self):
        self.register_screen = tkinter.Toplevel(self.login_window)
        self.register_screen.title("Register")
        self.register_screen.geometry("300x300")
        self.register_screen.configure(bg = "lightgray")

        self.register_label = tkinter.Label(self.register_screen, text="Please enter details below", bg="lightblue").pack(padx=20, pady=5)

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

        self.reg_button = tkinter.Button(self.register_screen, text="Register", width=10, height=1, bg="lightblue", command = self.register_user).pack(padx=20, pady=5)

    """ Rejestrowanie użytkownika """
    def register_user(self):
        username_info = self.username.get()
        password_info = self.password.get()

        filename = "%s.txt" % username_info

        file = open(filename, "w")

        file.write(username_info + "\n")
        file.write(password_info)
        file.close()

        self.username_entry.delete(0,END)
        self.password_entry.delete(0,END)

        Label(self.register_screen, text = "Registration Success", fg = "green", font=("calibri", 11)).pack()

    """ Włączenie konwersacji ze znajomym """
    def start_messaging(self, friend):
        self.gui_done = False
        self.running = True
        self.friend = friend
        """ Utworzenie wątków na główne okno czatu i na pętlę odbierania """
        self.gui_thread = threading.Thread(target=self.gui_loop)
        self.receive_thread = threading.Thread(target=self.receive)
        self.gui_thread.start()
        self.receive_thread.start()

    """ Odnotowanie pomyślnego zalogowania """
    def delete_login_success(self):
        self.login_window.destroy()
        self.friends_window = tkinter.Tk()
        self.friends_window.title(f"{self.nickname}'s friends")
        self.friends_window.geometry("500x500")
        self.running = True

        Label(self.friends_window, text = "Choose a friend with whom you want to chat", background="lightblue",
        width="200", height="2", font=("Calibri", 14)).pack(padx=5, pady=5)

        for n in self.list_of_files:
            splitted = n.split(".", 1)
            # Label(self.friends_window, text = f"Użytkownik: {splitted[0]}", font=("Calibri", 13)).pack()
            """ Pomijamy siebie """
            if splitted[0] != self.nickname:
                Button(self.friends_window, text = f"Chat with {splitted[0]}", font=("Calibri", 13), command = lambda splitted=splitted : self.start_messaging(splitted[0])).pack()

    """ Pop-up o pomyślnym zalogowaniu """
    def login_sucess(self):
        self.login_sucess_screen = tkinter.Toplevel(self.login_screen)
        self.login_sucess_screen.title("Success")
        self.login_sucess_screen.geometry("150x100")
        Label(self.login_sucess_screen, text = "Login success", fg = "green", font=("calibri", 11)).pack()

        Button(self.login_sucess_screen, text = "OK", command = self.delete_login_success).pack()


    def delete_password_not_recognised(self):
        self.password_not_recog_screen.destroy()

    """ Pop-up z informacją, że błędne hasło """
    def password_not_recognised(self):
        self.password_not_recog_screen = tkinter.Toplevel(self.login_screen)
        self.password_not_recog_screen.title("Unsuccess")
        self.password_not_recog_screen.geometry("150x100")

        Label(self.password_not_recog_screen, text = "Invalid password", fg = "red", font=("calibri", 11)).pack()
        Button(self.password_not_recog_screen, text = "OK", command = self.delete_password_not_recognised).pack()

    def delete_user_not_found_screen(self):
        self.user_not_found_screen.destroy()

    """ Pop-up z informacją, że podano błędną nazwę użytkownika (Taki użytkownik nie jest zarejestrowany) """
    def user_not_found(self):
        self.user_not_found_screen = tkinter.Toplevel(self.login_screen)
        self.user_not_found_screen.title("Unsuccess")
        self.user_not_found_screen.geometry("150x100")

        Label(self.user_not_found_screen, text = "User not found", fg = "red", font=("calibri", 11)).pack()
        Button(self.user_not_found_screen, text = "OK", command = self.delete_user_not_found_screen).pack()

    """ Weryfikacja logowania """
    def login_verification(self):
        username1 = self.username_verify.get()
        password1 = self.password_verify.get()

        self.username_login_entry.delete(0, END)
        self.password_login_entry.delete(0, END)

        filename = "%s.txt" % username1

        self.list_of_files = [f for f in os.listdir() if f.endswith('.txt')]
        print(self.list_of_files)

        if filename in self.list_of_files:
            file1 = open(filename, "r")

            verify = file1.read().splitlines()
            if password1 in verify:
                self.login_sucess()
                self.nickname = username1
                self.sock.send((self.nickname + '\0').encode('utf-8'))
            else:
                self.password_not_recognised()

        else:
            self.user_not_found()
    

    def login_verification_OC(self, event):
        self.login_verification()

    """ Ekran logowania """
    def login(self):
        self.login_screen = tkinter.Toplevel(self.login_window)
        self.login_screen.title("Login")
        self.login_screen.geometry("300x300")
        self.login_screen.bind('<Return>', self.login_verification_OC)

        self.login_lab = tkinter.Label(self.login_screen, text="Please enter details below to login", bg="lightblue").pack(padx=20, pady=5)

        self.username_verify = tkinter.StringVar(self.login_screen)
        self.password_verify = tkinter.StringVar(self.login_screen)

        Label(self.login_screen, text = "Username * ").pack(padx=10, pady=10)
        self.username_login_entry = tkinter.Entry(self.login_screen, textvariable = self.username_verify)
        self.username_login_entry.pack(padx=10,pady=10)

        Label(self.login_screen, text = "Password * ").pack(padx=10,pady=10)
        self.password_login_entry = tkinter.Entry(self.login_screen, textvariable = self.password_verify, show = '*')
        self.password_login_entry.pack(padx=10,pady=10)

        Button(self.login_screen, text = "Login", width = 10, height = 1, command=self.login_verification).pack()


    """ Pętla z oknem czatu """
    def gui_loop(self):
        self.win = tkinter.Tk()
        self.win.title(f"{self.nickname}'s chat")
        self.win.configure(bg="lightgray")
        self.win.bind('<Return>', self.send_on_click)

        self.chats.append(self.friend)

        self.chat_label = tkinter.Label(self.win, text=f"Chat with {self.friend}:", bg="lightgray")
        self.chat_label.config(font=("Arial", 12))
        self.chat_label.pack(padx=20, pady=5)

        self.text_area = tkinter.scrolledtext.ScrolledText(self.win)
        self.text_area.pack(fill='both', expand=True)
        self.text_area.tag_configure('tag-right', justify='right')
        self.text_area.tag_configure('tag-left', justify='left')
        self.text_area.config(state='disabled')

        self.msg_label = tkinter.Label(self.win, text="Message:", bg="lightgray")
        self.msg_label.config(font=("Arial", 12))
        self.msg_label.pack(padx=20, pady=5)

        self.input_area = tkinter.Text(self.win, height=3)
        self.input_area.pack(padx=20, pady=5)

        self.send_button = tkinter.Button(self.win, text="Send", command = lambda : self.write())
        self.send_button.config(font=("Arial", 12))
        self.send_button.pack(padx=20, pady=5)

        self.gui_done = True
        self.win.protocol("WM_DELETE", self.stop)
        self.win.mainloop()

    def stop(self):
        self.running = False
        self.win.destroy()
        self.gui_thread.join()
        self.sock.close()
        exit(0)

    """ Wysłanie wiadomości na przycisk ENTER """
    def send_on_click(self, event):
        self.send_from_enter = True
        self.write()

    """ Wysłanie wiadomości - pobranie tekstu z 'Input area', wytrymowanie go ze znaków białych a następnie wysłanie na socket """
    def write(self):
        msg = f"{self.nickname} -> {self.friend} : {self.input_area.get('1.0', 'end')}"
        if self.send_from_enter:
            msg = msg[:-1]
            self.send_from_enter = False
        if (len(msg)):
            msg = trim_send_msg(msg)
            self.sock.send((msg+'\n').encode('utf-8'))
            self.input_area.delete('1.0', 'end')

    """ Pętla na odbieranie wiadomości """
    def receive(self):
        while self.running:
            try:
                msg = self.sock.recv(1024).decode('utf-8')
                if msg == '#NICK':
                    self.sock.send(self.nickname.encode('utf-8'))
                else:
                    if self.gui_done and len(msg) > 0 and msg.split(" : ", 1)[0] in [self.friend, self.nickname]:
                        msg = trim_recv_msg(msg)
                        splitted = msg.split(' : ', 1)
                        self.text_area.config(state='normal')
                        print(msg)
                        """ Sprawdzenie nadawcy i podział przyjaicel - na lewo, ja - na prawo """
                        if splitted[0] == self.nickname:
                            label_me = Label(self.text_area, text=splitted[1], background='#ffffd0', justify='left', padx=10, pady=5)
                            self.text_area.insert('end', '\n ', 'tag-right')
                            self.text_area.window_create('end', window=label_me)
                            # self.text_area.insert('end', msg)
                        else:
                            label_nme = Label(self.text_area, text=splitted[1], background='#d0ffff', justify='left', padx=10, pady=5)
                            self.text_area.insert('end', '\n')
                            self.text_area.window_create('end', window=label_nme)
                            # self.text_area.insert('end', msg)
                        self.text_area.yview('end')
                        self.text_area.config(state='disabled')
            except ConnectionAbortedError:
                break
            except:
                print("Error")
                self.sock.close()
                break

client = Client(HOST, PORT)
exit(0)