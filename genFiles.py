dirs = ['Spells','Weapons','Heros']
profs = ['druid','hunter','mage','paladin','priest','rogue','shaman','warlock','warrior']
import os,time
path = os.path.dirname(__file__)
for a in ['hsClient','hsServer']:
    for d in dirs:
        dstr = path+'/'+a+'/gameModules/'+d
        os.mkdir(dstr)
        with open(dstr+'/__init__.py','w') as f:
            importstr = ''
            for prof in profs:
                with open(dstr+'/'+prof+d+'.py', 'w') as ff:
                    pass
                importstr+='from .'+prof+d+' import *\n'
            f.write(importstr)
