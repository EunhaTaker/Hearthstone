from ..Interface import *

class EdwinVanCleef(Minion, Rogue, NonRace, Legendary):
    name='埃德温 范里克夫'
    desc='连击：本回合你每打出一张牌，获得+2/+2'
    exts = ['combo']
    cost, attack, life = 3,2,2

    def combo(self):
        count = self.holder.comboCount
        self.attack += count*2
        self.life += count*2
        self.health += count*2
