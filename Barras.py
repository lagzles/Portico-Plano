import numpy as np
import math as m
import secao_002 as section


class Barras(object):
    def __init__(self, ni, nf, id, kx, ky, tipo):
        self.ni = ni
        self.nf = nf
        self.e = 20000.0 * 100.0 / 10000 #kN/cm2 * 100 => kgf/cm2
        self.fy = 3450 #kgf/cm2
        self.fu = 4150 #kgf/cm2
        self.id = id

        self.gdl = nf.gz # gdl # graus de liberdade
        self.compressao = 0
        self.tracao = 0
        self.cortanteInicio = []
        self.momentoInicio = []
        self.cortanteFinal = []
        self.momentoFinal = []

        self.tipo = tipo
        self.fboi = np.zeros((6))

        # definição das seções iniciais para as barras
        secao = 'soldado'
        d = 75.0 / 100.0
        tw = 0.635 / 100.0
        bf = 17.5 / 100.0
        tf = 0.635 / 100.0

        # seção default para barras
        self.section = section.Section(secao, d, bf, tw, tf, self.e, self.fy)
        self.set_propriedades()
        self.set_kx(kx)
        self.set_ky(ky)
        self.ratio_compressao = 0
        self.ratio_tracao = 0
        self.ratio = 0

       
    # metodos de retorno de parametros
    def get_compressao(self):
        return self.compressao

    def get_tracao(self):
        return self.tracao
    
    def get_kci(self):
        return self.kci

    def get_ni(self):
        return self.ni

    def get_nf(self):
        return self.nf

    def get_peso(self):
        return self.peso

    def set_ni(self, ni):
        self.ni = ni
        return ni

    def set_nf(self, nf):
        self.nf = nf
        return nf

    ######################################################
    ## 1 - FUNÇÔES PARA METODO DOS DESLOCAMENTOS!
    def set_gdl(self, gdl):
        self.gdl = gdl
        self.set_kci()


    def comprimento(self):
        x1 = self.ni.get_x()
        x2 = self.nf.get_x()
        y1 = self.ni.get_y()
        y2 = self.nf.get_y()
        
        self.lb = ((x2 - x1)**2 + (y2 - y1)**2)**(0.5)        
        return self.lb


    def set_theta(self):
        x1 = self.ni.get_x()
        x2 = self.nf.get_x()
        y1 = self.ni.get_y()
        y2 = self.nf.get_y()
        
        if (x1 - x2) == 0: # caso a barra esteja na horizontal
            self.theta = m.acos(0)
        elif (y1 - y2) == 0: # caso a barra esteja na vertical
            self.theta = m.asin(0)
        else:
            # retorna em radianos            
            self.theta = m.atan((y2 - y1)/ (x2 - x1))


    def set_ki(self):
        e = self.e
        a = self.section.get_area()
        ix = self.section.get_ix()
        # print(a, ix)
        l = self.comprimento()
        theta = self.theta
        kbi = np.zeros((6, 6))

        if True: #self.ni.apoio == 'engaste' or self.ni.apoio == False:
            # situação de barras engastadas em ambas extremidades
            # print('engaste/engaste')
            # if self.ni.y == 0:
            #     print('engaste gx/gy/gz', self.ni.gx-1, self.ni.gy-1, self.ni.gz-1)
            kbi[0][0] = e * a / l
            kbi[0][3] = - e * a / l

            kbi[1][1] = 12 * e * ix / (l**3)
            kbi[1][2] = 6 * e * ix / (l**2)
            kbi[1][4] = - 12 * e * ix / (l**3)
            kbi[1][5] = 6 * e * ix / (l**2)

            kbi[2][1] = 6 * e * ix / (l**2)
            kbi[2][2] = 4 * e * ix / (l)
            kbi[2][4] = - 6 * e * ix / (l**2)
            kbi[2][5] = 2 * e * ix / (l)

            kbi[3][0] = - e * a / l
            kbi[3][3] = e * a / l

            kbi[4][1] = - 12 * e * ix / (l**3)
            kbi[4][2] = - 6 * e * ix / (l**2)
            kbi[4][4] = 12 * e * ix / (l**3)
            kbi[4][5] = - 6 * e * ix / (l**2)

            kbi[5][1] = 6 * e * ix / (l**2)
            kbi[5][2] = 2 * e * ix / (l)
            kbi[5][4] = - 6 * e * ix / (l**2)
            kbi[5][5] = 4 * e * ix / (l)

        elif self.get_ni().apoio == 'bi-articulado':
            # situação de barras articulada em ambas extremidades
            # print('bi-articulada gy', self.ni.gy-1, self.ni.y)
            kbi[0][0] = e * a / l
            kbi[0][3] = - e * a / l

            kbi[3][0] = - e * a / l
            kbi[3][3] = e * a / l
        
        elif self.get_ni().apoio == 'rotuladoInicial':
            # if self.ni.y == 0:
            #     print('Rotulado inicial gx/gy', self.ni.gx-1, self.ni.gy-1)
            kbi[0][0] = e * a / l
            kbi[0][3] = - e * a / l

            kbi[1][1] = 3 * e * ix / (l**3)
            kbi[1][2] = 0
            kbi[1][4] = - 3 * e * ix / (l**3)
            kbi[1][5] = 3 * e * ix / (l**2)

            kbi[2][1] = 0
            kbi[2][2] = 0
            kbi[2][4] = 0
            kbi[2][5] = 0

            kbi[3][0] = - e * a / l
            kbi[3][3] = e * a / l

            kbi[4][1] = - 3 * e * ix / (l**3)
            kbi[4][2] = 0
            kbi[4][4] = 3 * e * ix / (l**3)
            kbi[4][5] = - 3 * e * ix / (l**2)

            kbi[5][1] = 3 * e * ix / (l**2)
            kbi[5][2] = 0
            kbi[5][4] = - 3 * e * ix / (l**2)
            kbi[5][5] = - 3 * e * ix / (l)

        elif self.get_nf().apoio == 'rotuladoFinal':
            # if self.nf.y == 0:
            #     print('Rotulado Final gx/gy', self.ni.gx-1, self.ni.gy-1)
            kbi[0][0] = e * a / l
            kbi[0][3] = - e * a / l

            kbi[1][1] = 3 * e * ix / (l**3)
            kbi[1][2] = 3 * e * ix / (l**2)
            kbi[1][4] = - 3 * e * ix / (l**3)
            kbi[1][5] = 0

            kbi[2][1] = 3 * e * ix / (l**2)
            kbi[2][2] = 3 * e * ix / (l**1)
            kbi[2][4] = - 3 * e * ix / (l**2)
            kbi[2][5] = 0

            kbi[3][0] = - e * a / l
            kbi[3][3] = e * a / l

            kbi[4][1] = - 3 * e * ix / (l**3)
            kbi[4][2] = - 3 * e * ix / (l**2)
            kbi[4][4] = 3 * e * ix / (l**3)
            kbi[4][5] = 0

            kbi[5][1] = 0
            kbi[5][2] = 0
            kbi[5][4] = 0
            kbi[5][5] = 0

        self.kbi = kbi
        
        ti_t = np.zeros((6,6))
        ti_t[0][0] = round(m.cos(theta),4)
        ti_t[0][1] = round(m.sin(theta),4)
        
        ti_t[1][0] = - round(m.sin(theta),4)
        ti_t[1][1] = + round(m.cos(theta),4)

        ti_t[2][2] = 1

        ti_t[3][3] = round(m.cos(theta),4)
        ti_t[3][4] = round(m.sin(theta),4)
        
        ti_t[4][3] = - round(m.sin(theta),4)
        ti_t[4][4] = + round(m.cos(theta),4)

        ti_t[5][5] = 1

        self.ti = ti_t
        
        a = np.transpose(ti_t)        
        b = np.dot(a, kbi)
        c = np.dot(b, ti_t)

        aa = np.dot(kbi, ti_t)
        bb = np.dot(a, aa)
        self.ki = bb #  c #ki


    def set_kci(self):
        gdl = self.gdl
        self.comprimento()
        self.set_theta()
        self.set_ki()
        li = np.zeros((6, gdl))

        li[0][self.ni.gx - 1] = 1
        li[1][self.ni.gy - 1] = 1
        li[2][self.ni.gz - 1] = 1
        li[3][self.nf.gx - 1] = 1
        li[4][self.nf.gy - 1] = 1
        li[5][self.nf.gz - 1] = 1
        
        self.li = li
        ki = self.ki
        a = np.transpose(li)
        b = np.dot(a, ki)
        c = np.dot(b, li)
        self.kci = c

    # 1 - FIM
    ######################################################

    def esforcos_nodais(self, tipoCarregamento, ua_list, liv):
        # gdl graus de liberdade do sistema
        # matriz de deslocamentos nodais
        # matriz com graus de liberdade livres
        # ua_list - lista com deslocamentos nodais gravitacionais e de vento
        for ua in ua_list:
            # cria uma matriz de 'zeros' de dimensões gdl x gdl
            u = np.zeros((self.gdl,))
            for i in range(len(ua)):
                # para nó livre, atribuir o valor na matriz de zeros
                u[liv[i]] = ua[i]

            ki_ti = np.dot(self.kbi, self.ti)
            ki_li = np.dot(ki_ti, self.li)
            kli_u = np.dot(ki_li, u)
            fbi = kli_u

            self.fbi = fbi + self.fboi
            self.compressao = self.compreesao + [tipoCarregamento, round(1*self.fbi[0],2)]
            self.tracao = self.tracao + [tipoCarregamento, round(1*self.fbi[0],2), self.tracao]
            self.cortanteInicio = self.cortanteInicio + [tipoCarregamento,  round(abs(1*self.fbi[1]),2)]
            self.momentoInicio = self.momentoInicio+ [tipoCarregamento,  round(abs(1*self.fbi[2]),2)]
            self.cortanteFinal = self.cortanteFinal + [tipoCarregamento,  round(abs(1*self.fbi[4]),2)]
            self.momentoFinal = self.momentoFinal + [tipoCarregamento, round(abs(1*self.fbi[5]),2)]


    def set_kx(self, kx):
        self.kx = kx
        # seta os comprimentos de flambagem da seção
        self.section.set_lx(self.comprimento()*100, kx)


    def set_ky(self, ky):
        self.ky = ky
        # seta os comprimentos de flambagem da seção
        self.section.set_ly(self.comprimento()*100, ky)


    def set_propriedades(self):
        self.set_peso()

        # tipo_barra = self.tipo.split("-")[-1]
        # if tipo_barra == 'inferior':
        #     self.set_ky(1) 
        #     self.set_kx(5) 
        # else:
        #     self.set_ky(1) 
        #     self.set_kx(1) 

        self.fy = 35 * 100 # 35 kN/cm² * 100 => 3500 kgf/cm²


    def set_peso(self):
        lb = self.comprimento() # m

        peso = (lb) * self.section.get_peso_linear()
        self.peso = peso
        return peso

    def set_section(self, dicionario):
        self.section.set_section(dicionario)
        self.set_kx(dicionario['kx'])
        self.set_ky(dicionario['ky'])
        self.set_peso()
        self.set_kci()
    
    def verificar(self):
        nc_rd = self.section.verificar_compressao()
        nt_rd = self.section.verificar_tracao()
        
        ratio1 = round(abs(self.compressao) / nc_rd,2)
        ratio2 = round(abs(self.tracao) / nt_rd,2)

        self.ratio_compressao = ratio1
        self.ratio_tracao = ratio2

        self.ratio = round(max(ratio1, ratio2),2)

        return self.ratio

 
