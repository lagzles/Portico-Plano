import numpy as np
import math as m
from Secao import Section


class Barras(object):
    def __init__(self, ni, nf, id, kx, ky, tipo):
        self.ni = ni
        self.nf = nf
        self.e = 20394320000.0  #kgf/m2 = 200.000,0 MPa
        self.fy = 3569006.0 # kgf/m2 = 350 Mpa
        self.fu = 42318214.0 # kgf/m2 = 415 MPa 
        self.id = id

        self.gdl = nf.gz # gdl # graus de liberdade
        # self.compressao = {}#[]
        self.normal = {}#[]
        self.cortanteInicio = {}#[]
        self.momentoInicio = {}#[]
        self.cortanteFinal = {}#[]
        self.momentoFinal = {}

        self.tipo = tipo
        self.fboi ={}#np.zeros((6))#
        self.ua = {}

        # definição das seções iniciais para as barras
        secao = 'soldado'
        # valores estão indo em metros
        d = 75.0 / 100
        tw = 0.635 / 100
        bf = 17.5 / 100
        tf = 0.635 / 100

        # seção default para barras
        self.sectionInicio = Section(secao, d, bf, tw, tf, self.e, self.fy)
        self.sectionFinal = Section(secao, d, bf, tw, tf, self.e, self.fy)
        self.set_peso()
        self.set_kx(kx)
        self.set_ky(ky)
        self.ratio_compressao = 0
        self.ratio_tracao = 0
        self.ratio = 0

       
    # metodos de retorno de parametros
    def get_sections_area(self):
        area1 = self.sectionInicio.get_area()
        area2 = self.sectionFinal.get_area()
        return (area1 + area2) / 2.0

    def get_sections_ix(self):
        ix1 = self.sectionInicio.get_ix()
        ix2 = self.sectionFinal.get_ix()
        return (ix1 + ix2) / 2.0

    def get_peso(self):
        return self.peso
    
    
    def get_kci(self):
        return self.kci

       ######################################################
    ## 1 - FUNÇÔES PARA METODO DOS DESLOCAMENTOS!
    def set_gdl(self, gdl):
        self.gdl = gdl
        self.set_kci()


    def comprimento(self):
        x1 = self.ni.x
        x2 = self.nf.x
        y1 = self.ni.y
        y2 = self.nf.y
        
        self.lb = ((x2 - x1)**2 + (y2 - y1)**2)**(0.5)        
        return self.lb


    def set_theta(self):
        x1 = self.ni.x
        x2 = self.nf.x
        y1 = self.ni.y
        y2 = self.nf.y
        
        if (y1 - y2) == 0: # caso a barra esteja na horizontal
            self.theta = m.acos(0)
        elif (x1 - x2) == 0: # caso a barra esteja na vertical
            self.theta = 1.5708 # 90 graus em radianos
        else:
            # retorna em radianos            
            self.theta = m.atan((y2 - y1)/ (x2 - x1))


    def set_ki(self):
        e = self.e
        a = self.get_sections_area()
        ix = self.get_sections_ix()
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

        elif self.ni().apoio == 'bi-articulado':
            # situação de barras articulada em ambas extremidades
            # print('bi-articulada gy', self.ni.gy-1, self.ni.y)
            kbi[0][0] = e * a / l
            kbi[0][3] = - e * a / l

            kbi[3][0] = - e * a / l
            kbi[3][3] = e * a / l
        
        elif self.ni().apoio == 'rotuladoInicial':
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

        elif self.nf().apoio == 'rotuladoFinal':
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
        # gera a atriz de rigidez local e global da barra
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

    def esforcos_nodais(self, tipoCarregamento, ua_list, liv, fo):
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

            uaBarra = [u[self.ni.gx-1],u[self.ni.gy-1],u[self.ni.gz-1],
                        u[self.nf.gx-1],u[self.nf.gy-1],u[self.nf.gz-1]]

            self.fbi = fbi + self.fboi[tipoCarregamento]
            self.ua[tipoCarregamento] = uaBarra
            # self.compressao[tipoCarregamento] = round(1*self.fbi[0],2)
            self.normal[tipoCarregamento] = round(1*self.fbi[0],2)
            self.cortanteInicio[tipoCarregamento] =  round(abs(1*self.fbi[1]),2)
            self.momentoInicio[tipoCarregamento] =  round(abs(1*self.fbi[2]),2)
            self.cortanteFinal[tipoCarregamento] =  round(abs(1*self.fbi[4]),2)
            self.momentoFinal[tipoCarregamento] =  round(abs(1*self.fbi[5]),2)


    def set_kx(self, kx):
        self.kx = kx
        # seta os comprimentos de flambagem da seção
        self.sectionInicio.set_lx(self.comprimento(), kx)
        self.sectionFinal.set_lx(self.comprimento(), kx)


    def set_ky(self, ky):
        self.ky = ky
        # seta os comprimentos de flambagem da seção
        self.sectionInicio.set_ly(self.comprimento(), ky)
        self.sectionFinal.set_ly(self.comprimento(), ky)


    def set_peso(self):
        lb = self.comprimento() # m

        areaMedia = self.get_sections_area()
        pesoLinear = areaMedia * 7850 # 7850 kg/m3

        peso = (lb) * pesoLinear
        self.peso_linear = pesoLinear
        self.peso = peso
        return peso

    def set_section(self, dicionarioInicio, dicionarioFinal, kx, ky): 
        self.section.set_section(dicionarioInicio)
        self.sectionFinal.set_section(dicionarioFinal)
        self.set_kx(kx)
        self.set_ky(ky)
        self.set_peso()
        # refaz a matriz de rigidez em coordenadas local e global da barra
        self.set_kci()



    # TODO ajustar metodo para fazer combinações dos esforços,
    # TODO ajustar para verificar estado limite ultimo
    # TODO ajustar para verificar estado limite de serviço (talvez separar em 2 metodos)
    def verificar(self):
        nci_rd = self.sectionInicio.verificar_compressao()
        ncf_rd = self.sectionFinal.verificar_compressao()

        nti_rd = self.sectionInicio.verificar_tracao()
        ntf_rd = self.sectionFinal.verificar_tracao()
        
        mi_rd = self.sectionInicio.verificar_flexao()
        mf_rd = self.sectionFinal.verificar_flexao()
        
        ratio1 = round(abs(self.compressao) / nci_rd,2)
        ratio2 = round(abs(self.tracao) / nti_rd,2)

        self.ratio_compressao = ratio1
        self.ratio_tracao = ratio2

        self.ratio = round(max(ratio1, ratio2),2)

        return self.ratio


    def set_combinacoes_esforcos(self):
        print()

 

def red(numero):
    return round(numero,2)