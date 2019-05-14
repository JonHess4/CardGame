import socket
perk = socket.gethostbyname(socket.gethostname())
print(perk)
import threading
import sys

class Server:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    def __init__(self):
        self.connections = []
        self.gameLobbies = []
        self.sock.bind(('0.0.0.0', 10000))
        self.sock.listen(1)

    def handler(self, c, a):
        while True:
            data = c.recv(1024)

            wholeIncoming = str(data, 'utf-8')

            incoming = wholeIncoming.split()
            if len(incoming) > 3 and incoming[0] == "sendto":
                message = " ".join(incoming[2:])
                incoming = [incoming[0], incoming[1], message]

            # ↓ Basic server commands ↓
            if incoming[0] == "login":
                loggedIn = False
                for user in self.connections:
                    if c == user[0]:
                        if user[2] == "loggedIn":
                            c.send(bytes("You are already logged in", 'utf-8'))
                        else:
                            user[1] = incoming[1]
                            user[2] = "loggedIn"
                        c.send(bytes("Success", 'utf-8'))
                        break
            elif incoming[0] == "list":
                loggedIn = ""
                for user in self.connections:
                    if user[2] == "loggedIn":
                        loggedIn = loggedIn + user[1] + "\n"
                c.send(bytes(loggedIn, 'utf-8'))
            elif incoming[0] == "sendto":
                sender = ""
                for user in self.connections:
                    if c == user[0]:
                        if user[2] != "loggedIn":
                            c.send(bytes("You must be logged in to send a message", 'utf-8'))
                        else:
                            sender = user[1]
                        break
                if sender != "":
                    rec = False
                    for user in self.connections:
                        if incoming[1] == user[1]:
                            if user[2] == "loggedIn":
                                rec = True
                                message = sender + ": " + incoming[2]
                                user[0].send(bytes(message, 'utf-8'))
                                c.send(bytes("Success", 'utf-8'))
                            break
                    if rec == False:
                        c.send(bytes("That user is currently not logged in", 'utf-8'))
            elif incoming[0] == "logout":
                for user in self.connections:
                    if c == user[0]:
                        user[2] = "loggedOut"
                        c.send(bytes("Success", 'utf-8'))
                        break
            elif incoming[0] == "exit":
                for user in self.connections:
                    if c == user[0]:
                        self.connections.remove(user)
                        break
                c.close()
                print(str(a[0]) + ':' + str(a[1]) + " disconnected")
                break
            elif incoming[0] == "startgame":
                newLobby = []
                rec = 0
                for user in self.connections:
                    if c == user[0]:
                        if user[2] == "loggedIn":
                            newLobby.append(user)
                            rec += 1
                    if incoming[1] == user[1]:
                        if user[2] == "loggedIn":
                            newLobby.append(user)
                            rec += 1
                    if rec >= 2:
                        break
                if rec < 2:
                    c.send(bytes("Both players must be logged in to start a game", 'utf-8'))
                else:
                    newLobby.append(0)
                    newLobby[0][0].send(bytes("startgame " + newLobby[1][1] + " " + str(0) + " " + str(len(self.gameLobbies)), 'utf-8'))
                    newLobby[1][0].send(bytes("startgame " + newLobby[0][1] + " " + str(1) + " " + str(len(self.gameLobbies)), 'utf-8'))
                    self.gameLobbies.append(newLobby)
            # ↑ Basic server commands ↑

            # ↓ In-game commands ↓
            elif incoming[0] == "attack" or incoming[0] == "play":
                lobby = self.gameLobbies[int(incoming[-1])]
                lobby[0][0].send(bytes(wholeIncoming, 'utf-8'))
                lobby[1][0].send(bytes(wholeIncoming, 'utf-8'))
            elif incoming[0] == "endturn":
                lobby = self.gameLobbies[int(incoming[-1])]
                lobby[2] += 1
                lobby[0][0].send(bytes(wholeIncoming, 'utf-8'))
                lobby[1][0].send(bytes(wholeIncoming, 'utf-8'))
            # ↑ In-game commands ↑

            else:
                print("Bad message recieved: " + wholeIncoming)

            if not data:
                self.connections.remove(c)
                c.close()
                print(str(a[0]) + ':' + str(a[1]) + " disconnected")
                break

    def run(self):
        print("Server is running ... ")
        while True:
            c, a = self.sock.accept()
            cThread = threading.Thread(target=self.handler, args=(c, a))
            cThread.daemon = True
            cThread.start()
            self.connections.append([c, "<userName>", "loggedOut"])
            print(str(a[0]) + ':' + str(a[1]) + " connected")
            c.send(bytes("Success", 'utf-8'))


def main():
    server = Server()
    server.run()

main()
