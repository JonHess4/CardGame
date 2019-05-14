import socket  #127.0.0.1
import threading
import sys
from random import shuffle
from random import randint
import copy
import pickle
from MinionAndPlayerClass import *
from BoardClass import *

class Client:
    def __init__(self, address, player):
        self.player = player
        self.gameCopy = None
        self.board = None
        self.hand = []
        self.turn = None
        self.curTurn = None
        self.gameLobby = None
        self.opponent = None
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.cmds = ["editdeck", "save", "attack", "endgame", "endturn", "play",
            "exit", "list", "login", "logout", "sendto", "startgame"]
        self.cmdsDic = {"attack": 2, "editdeck": 1, "endgame": 1, "endturn": 1,
            "exit": 1, "list": 1, "login": 1, "logout": 1, "play": 3, "save": 1,
            "sendto": 3, "startgame": 2}
        self.sock.connect((address, 10000))

        iThread = threading.Thread(target=self.sendMsg)
        iThread.daemon = True
        iThread.start()

        while True:
            data = self.sock.recv(1024)
            if not data:
                break
            print(str(data, 'utf-8'))
            incoming = str(data, 'utf-8')
            incList = incoming.split()
            if incList[0] == "attack":
                self.attack(incList, self.curTurn % 2)
                self.board.showBoard([], self.hand)
            elif incList[0] == "endgame":
                self.board = None
                self.gameCopy = None
                self.hand = []
                self.turn = None
                self.curTurn = None
                self.gameLobby = None
                self.opponent = None
            elif incList[0] == "endturn":
                self.curTurn += 1
                self.board.resetAtks(self.curTurn % 2)
                mana = min(10, self.curTurn // 2 + 1)
                if self.curTurn % 2 == self.turn:
                    self.gameCopy.setMana(str(mana) + "/" + str(mana))
                    self.draw()
                else:
                    self.opponent.setMana(str(mana) + "/" + str(mana))
                self.board.showBoard([], self.hand)
            elif incList[0] == "play": #play & <card info> & <lane> & <lobby>
                self.play(incoming, self.curTurn % 2)
                card = self.board.getResPkg(self.curTurn % 2, incList[-3])[1]
                if self.curTurn % 2 == self.turn:
                    self.gameCopy.setMana(str((int(self.gameCopy.getMana()[0]) - card.getMana())) + self.gameCopy.getMana()[1:])
                else:
                    self.opponent.setMana(str((int(self.opponent.getMana()[0]) - card.getMana())) + self.opponent.getMana()[1:])
                self.board.showBoard([], self.hand)
            elif incList[0] == "startgame": #startgame <opponent> <turn> <lobby>
                self.gameLobby = int(incList[-1])
                self.gameCopy = copy.copy(player)
                shuffle(self.gameCopy.deck)
                self.turn = int(incList[2])
                self.curTurn = 0
                self.gameCopy.setMana("1/1")
                self.opponent = Player(incList[1])
                self.opponent.setMana("1/1")
                pList = [None, None]
                pList[self.turn] = self.gameCopy
                pList[(self.turn + 1)%2] = self.opponent
                self.board = Board(pList[0], pList[1])
                for i in range(4):
                    self.draw()
                self.board.showBoard([], self.hand)

    def sendMsg(self):
        while True:
            message = input("")
            msgList = message.split()
            if len(msgList) > 3 and msgList[0] == "sendto":
                words = " ".join(msgList[2:])
                msgList = [msgList[0],msgList[1], words]
            if len(msgList) > 0:
                cmd = msgList[0].lower()

                # ↓ check for invalid commands ↓
                if cmd not in self.cmds or len(msgList) != self.cmdsDic[cmd]:
                    print("Invalid command")
                elif cmd == "sendto" and len(msgList[2]) > 65535:
                    print("Bad message: too long")
                # ↑ check for invalid commands ↑

                # ↓ Commands that DON'T need to communicate with the server ↓
                elif cmd == "editdeck":
                    self.deckEditor()
                elif cmd == "save":
                    file = str(self.player.getName()) + ".dat"
                    with open(file, 'wb') as f:
                        pickle.dump(self.player, f, pickle.HIGHEST_PROTOCOL)
                # ↑ Commands that DON'T need to communicate with the server ↑

                # ↓ Commands that DO need to communicate with the server ↓
                else:

                    # ↓ In-game commands ↓
                    if cmd in self.cmds[2:6] and self.gameLobby != None:
                        if cmd == "attack":
                            if self.board.getResPkg(self.turn, int(msgList[1])) == None:
                                print("You do not have a minion in that lane")
                            elif self.board.getAtks(self.turn, int(msgList[1])) <= 0:
                                print("That minion has no attacks left this turn")
                            elif self.curTurn % 2 != self.turn:
                                print("It is not your turn currently")
                            else:
                                message = message + " " + str(self.gameLobby)
                                self.sock.send(bytes(message, 'utf-8'))
                        elif cmd == "endgame":
                            message = message + " " + str(self.gameLobby)
                            self.sock.send(bytes(message, 'utf-8'))
                            self.board = None
                            self.gameCopy = None
                            self.hand = []
                            self.turn = None
                            self.gameLobby = None
                        elif cmd == "endturn":
                            if self.curTurn % 2 != self.turn:
                                print("It is not your turn currently")
                            else:
                                message = message + " " + str(self.gameLobby)
                                self.sock.send(bytes(message, 'utf-8'))
                        elif cmd == "play":
                            if int(msgList[1]) >= len(self.hand):
                                print("No minion in that hand position")
                            elif self.hand[int(msgList[1])].getMana() > int(self.gameCopy.getMana()[0]):
                                print("You do not have enough mana to play that minion")
                            elif int(msgList[2]) not in range(1, 8):
                                print("Not a valid lane")
                            elif self.board.getResPkg(self.turn, int(msgList[2])) != None:
                                print("You can only play minions in vacant lanes")
                            elif self.curTurn % 2 != self.turn:
                                print("It is not your turn currently")
                            else:
                                card = self.hand.pop(int(msgList[1]))
                                cardInfo = str(card.getName())+" "+str(card.getAtk())+" "+str(card.getMaxHp())+" "+ " ".join(card.getADS())+" "+ " ".join(card.getDDS())
                                message = "play" + " & " + cardInfo + " & " + str(msgList[2]) + " & " + str(self.gameLobby)
                                print("The play message is: ", message)
                                self.sock.send(bytes(message, 'utf-8'))
                    # ↑ In-game commands ↑

                    # ↓ Basic server commands ↓
                    elif cmd in self.cmds[6:]:
                        if cmd == "login":
                            message = "login " + str(self.player.getName())
                            self.sock.send(bytes(message, 'utf-8'))
                        elif cmd == "startgame":
                            if len(self.player.deck) != 30:
                                print("Your deck is incomplete")
                            elif self.gameLobby != None:
                                print("You are already in a game")
                            else:
                                self.sock.send(bytes(message, 'utf-8'))
                        else:
                            self.sock.send(bytes(message, 'utf-8'))
                    # ↑ Basic server commands ↑
                    else:
                        print("You are currently not in a game.")

                # ↑ Commands that DO need to communicate with the server ↑

    def attack(self, info, turn):
        lane = int(info[1])
        self.board.modAtks(turn, lane, -1)
        attackerPkg = self.board.getResPkg(turn, lane)
        ads = attackerPkg[1].getADS().copy()
        ads[0], ads[1] = ads[1], ads[0]
        targetLanes = []
        for i in range(3):
            if ads[i] != "_":
                targetLanes.append(lane+i-1)
        passes = 0
        hasDefended = []
        for cLane in targetLanes:
            defenders = copy.copy(self.board.getDefenders((turn+1)%2, cLane))
            if defenders == []:
                passes += 1
                pass
            else:
                for defenderPkg in defenders:
                    if defenderPkg not in hasDefended:
                        hasDefended.append(defenderPkg)
                        self.board.resolveAtk(attackerPkg, defenderPkg, turn, cLane)
                    if self.board.getResPkg(turn, lane) == None:
                        break
                if self.board.getResPkg(turn, lane) == None:
                    break
        if passes == len(targetLanes):
            opponentPkg = self.board.getResPkg((turn+1)%2, ((turn+1)%2)*8)
            self.board.resolveAtk(attackerPkg, opponentPkg, turn, ((turn+1)%2)*8)

    def draw(self):
        if len(self.hand) < 10:
            card = self.gameCopy.deck.pop()
            self.hand.append(card)

    def play(self, message, turn):
        print("In the play() function:")
        print("message is: ", message)
        info = message.split("&")
        print("info is: ", info)
        minStuff = info[1].split()
        print("minStuff is: ", minStuff)
        minStuff[3] = [minStuff[3], minStuff[4], minStuff[5]]
        minStuff[4] = [minStuff[6], minStuff[7], minStuff[8]]
        print("minStuff[3] ", minStuff[3])
        print("minStuff[4] ", minStuff[4])
        minion = Minion(minStuff[0], int(minStuff[1]), int(minStuff[2]), minStuff[3], minStuff[4])
        self.board.addMinion(turn, info[2], minion)

    def deckEditor(self):
        print("\nWelcome to the Deck Editor")
        while True:
            cmd = input("Would you like to 'addCard', 'removeCard', 'showDeck', 'sortDeck', make a 'randomDeck' or 'exit'? ").lower()
            if cmd == "addcard":
                if len(self.player.deck) >= 30:
                    print("Your deck is full")
                else:
                    print("Feature in development")
                    name = input("Enter Card's Name: ")
                    atk = input("Enter Attack Value: ")
                    hp = input("Enter HP Value: ")
                    dirDict = {'straight': u"\u2190", 'up': u"\u2191", 'down': u"\u2193", 'none': "_"}
                    directions = ['straight', 'up', 'down']
                    tempads = input("Enter some direction(s) for attack? ('straight', 'up', 'down'): ").split()
                    ads = []
                    for i in range(3):
                        if directions[i] in tempads:
                            ads.append(dirDict[directions[i]])
                        else:
                            ads.append('_')
                    tempdds = input("Enter some direction(s) to defend? ('straight', 'up', 'down'): ").split()
                    dds = []
                    for i in range(3):
                        if directions[i] in tempdds:
                            dds.append(dirDict[directions[i]])
                        else:
                            dds.append('_')
                    self.player.addCardToDeck(Minion(name[:9], int(atk), int(hp), ads, dds))
            elif cmd == "removecard":
                cardName = input("Enter name of card to be removed: ")
                for card in self.player.getDeck():
                    if card.getName() == cardName:
                        print("Card removed")
                        self.player.removeCardFromDeck(card)
                        break
            elif cmd == "showdeck":
                self.player.showDeck()
            elif cmd == "sortdeck":
                self.player.sortDeckByMana()
            elif cmd == "exit":
                break
            elif cmd == 'randomdeck':
                self.player.setDeck(self.deckMkr())
            else:
                print("Unrecognized Command")

    def deckMkr(self):
        deck = []
        d = [u"\u2190",u"\u2191",u"\u2193"]
        for i in range(30):
            stat = randint(0, 20)
            atk = max(1, min(10,randint(0,stat)))
            hp = max(1, min(10,stat - atk))
            ad,dd = [],[]
            for j in range(3):
                if randint(0,1) == 1:
                    ad.append(d[j])
                if randint(0,1) == 1:
                    dd.append(d[j])
            if ad == []:
                ad.append(d[randint(0,2)])
            if dd == []:
                dd.append(d[randint(0,2)])
            deck.append(Minion("M"+str(i+10),atk,hp,ad,dd))
        return deck

def main():
    player = Player("NewPlayer")
    userName = input("Enter a user name: ")
    file = userName + ".dat"
    try:
        with open(file, 'rb') as f:
            player = pickle.load(f)
        print("Welcome back " + userName)
    except:
        print("Welcome " + userName + ". Enjoy your new account")
    finally:
        player.setName(userName)

#    print("""Enter the ip address needed to connect to the server.
#    (if the server and client are on the same computer, 127.0.0.1 will work)
#    (client.py will error and close if you enter an invalid IP address or if the server is not currently running)""")
#    address = input("IP address: ")
    address = "127.0.0.1" #server IP address when server and client on same computer
    #address = "192.168.1.14" #server IP address
    client = Client(address, player)
    save = input("Enter 'save' to save befor exiting: ").lower()
    if save == "save":
        file = player.getName() + ".dat"
        with open(file, 'wb') as f:
            pickle.dump(player, f, pickle.HIGHEST_PROTOCOL)

main()
