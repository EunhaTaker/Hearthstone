from ..Interface import *

class ScavengingHyena(Minion, Hunter, Beast, Common):
    name = '食腐土狼'
    desc = '每当一个友方野兽死亡，获得+2/+1'
    exts = ['tigger']
    cost,attack,life = 2,2,2

    def tigger(self, event, char, amount=0):
        if event==Event.死亡 and self.getRole(char)&Role.友方 and char.race=='beast':
            logger.warning('野兽死了一个')
            self.attack+=2
            self.life+=1
            self.health+=1