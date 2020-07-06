# -*- coding: utf-8 -*-


class Nos(object):
    def __init__(self, x, y, gx, gy, gz, apoio):
        self.x = x
        self.y = y
        
        self.gx = gx
        self.gy = gy
        self.gz = gz

        self.id = gz / 3

        self.apoio = apoio
        self.rx = {}#0
        self.ry = {}#0
        self.mz = {}#0
    
    def __str__(self):
        return "nó " + str(self.id)
    
    def printReacoes(self):
        print('no ',self.id, self.apoio)
        for key in sorted(self.rx):
            print(key,'\t',
                        round(self.rx[key],1),'\t',
                        round(self.ry[key],1),'\t',
                        round(self.mz[key],1))
        return True

