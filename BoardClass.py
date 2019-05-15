class Board():
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
        self.atks = [[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0]]
        self.board = [[[0,self.p1],None,None,None,None,None,None,None,None],
        [None,None,None,None,None,None,None,None,[8,self.p2]]]
        self.defenders = [[[],[],[],[],[],[],[],[],[]],
        [[],[],[],[],[],[],[],[],[]]]

    def getBoard(self):
        print("Board retrieved")
        return self.board
    def getAtks(self, turn, lane):
        turn = int(turn)
        lane = int(lane)
        print("Atks available for lane",lane,"retrieved")
        return self.atks[turn][lane]
    def getResPkg(self, turn, lane):
        turn = int(turn)
        lane = int(lane)
        print("Resident of lane",lane,"retrieved")
        return self.board[turn][lane]
    def getDefenders(self, turn, lane):
        turn = int(turn)
        lane = int(lane)
        print("Defenders being retrieved before sort: ",self.defenders[turn][lane])
        self.defenders[turn][lane].sort()
        print("Defenders being retrieved after sort: ",self.defenders[turn][lane])
        return self.defenders[turn][lane]

    def setRes(self, turn, lane, newResPkg):
        turn = int(turn)
        lane = int(lane)
        if newResPkg != None:
            print("Resident of lane",lane,"has been set to",newResPkg[1])
        else:
            print("lane",lane,"is now vacant")
        self.board[turn][lane] = newResPkg
    def setDefenders(self,turn, lane, newDefenders):
        turn = int(turn)
        lane = int(lane)
        print("Defenders of lane",lane,"have been set to",newDefenders)
        self.defenders[turn][lane] = newDefenders

    def modAtks(self, turn, lane, mod):
        turn = int(turn)
        lane = int(lane)
        mod = int(mod)
        self.atks[turn][lane] += mod

    def addMinion(self, turn, lane, minion):
        turn = int(turn)
        lane = int(lane)
        print("Minion",minion," being added to the board")
        print("Setting them as a lane resident")
        self.setRes(turn, lane, [lane,minion])
        print("Adding them to defense rosters")
        self.addDefender(turn, lane, minion)

    def remMinion(self, turn, lane, minionPkg):
        turn = int(turn)
        lane = int(lane)
        print("Searching for",minionPkg[1],"to remove from lane",lane)
        if minionPkg == self.board[turn][minionPkg[0]]:
            print("Minion",minionPkg[1],"found in lane",lane)
            print("Minion",minionPkg[1],"removed from lane",lane)
            self.setRes(turn, minionPkg[0], None)
        self.remDefender(turn, minionPkg[0], minionPkg)

#"left":u"\u2190","right":u"\u2192","up":u"\u2191","down":u"\u2193",None:"_"}
    def addDefender(self, turn, lane, newDefender):
        turn = int(turn)
        lane = int(lane)
        print("Adding minion",newDefender,"to the defense rosters")
        dds = newDefender.getDDS().copy()
        dds[0],dds[1] = dds[1],dds[0]
        dlane = lane - 1
        for i in dds:
            if i != "_":
                print(newDefender,"is defending lane",dlane)
                self.defenders[turn][dlane].append([lane,newDefender])
                print(self.defenders[turn][dlane],"are the brave souls defending lane",dlane)
            dlane += 1

    def remDefender(self, turn, lane, defenderPkg):
        turn = int(turn)
        lane = int(lane)
        print("Removing minion",defenderPkg[1],"from the defense rosters")
        dlane = lane - 1
        for i in range(3):
            if defenderPkg in self.defenders[turn][dlane]:
                print(defenderPkg[1],"is no longer defending lane",dlane)
                self.defenders[turn][dlane].remove(defenderPkg)
                print(self.defenders[turn][dlane],"are the brave souls defending lane",dlane)
            dlane += 1

    def resetAtks(self, turn):
        turn = int(turn)
        self.atks = [[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0]]
        count = 0
        for lane in self.board[turn]:
            if lane != None:
                self.atks[turn][count]+=1
            count += 1

    def resolveAtk(self, attackerPkg, defenderPkg, turn, clane):
        turn = int(turn)
        clane = int(clane)
        print(attackerPkg[1],"is attacking",defenderPkg[1],"in lane",clane)
        attackerPkg[1].modCurHp(defenderPkg[1].getAtk()*-1)
        defenderPkg[1].modCurHp(attackerPkg[1].getAtk()*-1)
        if attackerPkg[1].getCurHp() <= 0 and attackerPkg[0] != 0 and attackerPkg[0] != 8:
            print(attackerPkg[1],"has perished")
            self.remMinion(turn, attackerPkg[0], attackerPkg)
        else:
            print(attackerPkg[1],"lives on")
        if defenderPkg[1].getCurHp() <= 0 and defenderPkg[0] != 0 and defenderPkg[0] != 8:
            self.remMinion((turn+1)%2, defenderPkg[0], defenderPkg)
            print(defenderPkg[1],"has perished")
        else:
            print(defenderPkg[1],"lives on")

    def showBoard(self,hand1,hand2):
        line = "_"*100
        print(line)
        print("Hand: ")
        pos = 0
        for card in hand1:
            print("  Pos:",pos,card)
            pos += 1
        print(line)
        print("{:42s}{:5s}{:7s}{:5s}\
".format(self.p1.__str__(),"Atks","Lanes","Atks"))
        for i in range(1,8):
            minion1 = "Vacant"
            lane = "|Lane " + str(i) + "|"
            minion2 = "Vacant"
            if self.board[0][i] != None:
                minion1 = self.board[0][i][1].__str__()
            if self.board[1][i] != None:
                minion2 = self.board[1][i][1].__str__()
            print(line)
            print("{:45s}{:1s}{:1s}{:1s}{:>45s}\
".format(minion1,str(self.atks[0][i]),lane,str(self.atks[1][i]),minion2))
        print(line)
        print("{:42s}{:5s}{:7s}{:5s}{:>42s}\
".format("","Atks","Lanes","Atks",self.p2.__str__()))
        print(line)
        print("{:55s}Hand: ".format(""))
        pos = 0
        for card in hand2:
            print("{:55s} Pos:".format("")+str(pos) + " " + card.__str__())
            pos += 1
        print(line)
