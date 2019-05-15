from math import ceil
import copy

class Minion():
    def __init__(self, name, atk, hp, ads, dds):
        self.name = name
        self.atk = atk
        self.curHp = hp
        self.maxHp = hp
        self.mana = min(10, ceil((self.atk + self.maxHp)/2))
        self.ads = []
        self.dds = []
        d = [u"\u2190",u"\u2191",u"\u2193","←","↑","↓"]
        for i in range(3):
            if d[i] in ads or d[i+3] in ads:
                self.ads.append(d[i])
            else:
                self.ads.append("_")
            if d[i] in dds or d[i+3] in dds:
                self.dds.append(d[i])
            else:
                self.dds.append("_")

    def getName(self):
        print(self.name,"\'s name (",self.name,") has been retrieved")
        return self.name
    def getAtk(self):
        print(self.name,"\'s atk (",self.atk,") has been retrieved")
        return self.atk
    def getCurHp(self):
        print(self.name,"\'s curHp (",self.curHp,") has been retrieved")
        return self.curHp
    def getMaxHp(self):
        print(self.name,"\'s maxHp (",self.maxHp,") has been retrieved")
        return self.maxHp
    def getMana(self):
        #print(self.name,"\'s mana (",self.mana,") has been retrieved")
        return self.mana
    def getADS(self):
        print(self.name,"\'s ads (",self.ads,") has been retrieved")
        return self.ads
    def getDDS(self):
        print(self.name,"\'s dds (",self.dds,") has been retrieved")
        return self.dds

    def setName(self, newName):
        print(self.name,"\'s name (",self.name,") has been set to",newName)
        self.name = newName
    def setAtk(self, newAtk):
        print(self.name,"\'s atk (",self.atk,") has been set to",newAtk)
        self.atk = newAtk
    def setCurHp(self, newCurHp):
        print(self.name,"\'s curHp (",self.curHp,") has been set to",newCurHp)
        self.curHp = newCurHp
    def setMaxHp(self, newMaxHp):
        print(self.name,"\'s maxHp (",self.maxHp,") has been set to",newMaxHp)
        self.maxHp = newMaxHp
    def setMana(self, newMana):
        print(self.name,"\'s mana (",self.mana,") has been set to",newMana)
        self.mana = newMana
    def setADS(self, newADS):
        print(self.name,"\'s ads (",self.ads,") has been set to",newADS)
        self.ads = newADS
    def setDDS(self, newDDS):
        print(self.name,"\'s dds (",self.dds,") has been set to",newDDS)
        self.dds = newDDS

    def modName(self, mod):
        print(self.name,"\'s name (",self.name,") has been modded with",mod)
        self.name += mod
    def modAtk(self, mod):
        print(self.name,"\'s atk (",self.atk,") has been modded with",mod)
        self.atk += mod
    def modCurHp(self, mod):
        print(self.name,"\'s curHp (",self.curHp,") has been modded with",mod)
        self.curHp += mod
    def modMaxHp(self, mod):
        print(self.name,"\'s maxHp (",self.maxHp,") has been modded with",mod)
        self.maxHp += mod
    def modMana(self, mod):
        print(self.name,"\'s mana (",self.mana,") has been modded with",mod)
        self.mana += mod

    def __str__(self):
        ads = ' '
        dds = ' '
        for i in range(3):
            ads += str(self.ads[i])
            dds += str(self.dds[i])
        return "{:5s}{:<4s}{:>3s}{:7s}{:>2s}{:5s}{:>2s}/{:2s}{:3s}{:4s}\
".format(str(self.name),ads,str(self.mana)," Mana,",str(self.atk),"Atk,\
",str(self.curHp),str(self.maxHp),"Hp",dds)

class Player(Minion):
    def __init__(self, name):
        Minion.__init__(self, name, 0, 30, [u"\u2190"], [u"\u2190"])
        self.mana = "0/0"
        self.deck = []

    def getDeck(self):
        return self.deck

    def setDeck(self, newDeck):
        self.deck = newDeck

    def addCardToDeck(self, newCard):
        if len(self.deck) < 30:
            self.deck.append(newCard)
        else:
            print("Your deck is full.")

    def removeCardFromDeck(self, card):
        if card in self.deck:
            self.deck.remove(card)

    def showDeck(self):
        print(str(self.name)+"'s Current Deck")
        for card in self.deck:
            print(card)

    def sortDeckByMana(self):
        oldDeck = copy.copy(self.deck)
        newDeck = [None]*len(self.deck)
        for oldCard in oldDeck:
            place = 0
            for curCard in self.deck:
                if oldCard.getMana() > curCard.getMana():
                    place += 1
            while True:
                if newDeck[place] == None:
                    newDeck[place] = oldCard
                    break
                else:
                    place += 1
        self.deck = newDeck

    def __str__(self):
        return "{:10s}{:>2s}{:6s}{:>2s}/{:2s}{:3s}\
".format(str(self.name),str(self.mana),"Mana,",str(self.curHp),str(self.maxHp),"Hp")
