import numpy as np
import math as m
from Secao import Section


class Barras(object):
    def __init__(self, ni, nf, id, kx, ky, tipo, portico):
        self.ni = ni
        self.nf = nf
        self.e = 20000000000.0  #kgf/m2 = 200.000,0 MPa
        self.fy = 34500000.0 # kgf/m2 = 350 Mpa
        self.fu = 41500000.0 # kgf/m2 = 415 MPa 
        self.id = id
        self.portico = portico

        self.gdl = nf.gz # gdl # graus de liberdade
        # self.compressao = {}#[]
        self.normal = {}#[]
        self.cortante_inicio = {}#[]
        self.momento_inicio = {}#[]
        self.cortante_final = {}#[]
        self.momento_final = {}

        self.tipo = tipo
        self.fboi ={}#np.zeros((6))#
        self.ua = {}

        # definição das seções iniciais para as barras
        secao = 'soldado'
        # valores estão indo em metros
        d = 45.0 / 100
        tw = 0.635 / 100
        bf = 15.0 / 100
        tf = 0.635 / 100

        # seção default para barras
        self.section_inicio = Section(secao, d, bf, tw, tf, self.e, self.fy)#, kx, ky)
        self.section_final = Section(secao, d, bf, tw, tf, self.e, self.fy)#, kx, ky)
        self.set_peso()
        self.set_kx(kx)
        self.set_ky(ky)

        # esforços combinados do inicio e final da barra
        self.elu_ntsd = 0
        self.elu_ncsd = 0
        self.elu_msdi = 0
        self.elu_msdf = 0
        self.elu_vsdi = 0
        self.elu_vsdf = 0

        # ratio's de momentos, cortantes e ratios combinados
        self.ratio_mi = 0
        self.ratio_vi = 0
        self.ratio_mf = 0
        self.ratio_vf = 0
        self.ratio_inicio = 0
        self.ratio_final = 0

       
    # metodos de retorno de parametros
    def get_sections_area(self):
        area1 = self.section_inicio.get_area()
        area2 = self.section_final.get_area()
        return (area1 + area2) / 2.0

    def get_sections_ix(self):
        ix1 = self.section_inicio.get_ix()
        ix2 = self.section_final.get_ix()
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
            self.cortante_inicio[tipoCarregamento] =  round((1*self.fbi[1]),2)
            self.momento_inicio[tipoCarregamento] =  round((1*self.fbi[2]),2)
            self.cortante_final[tipoCarregamento] =  round((1*self.fbi[4]),2)
            self.momento_final[tipoCarregamento] =  round((1*self.fbi[5]),2)


    def set_kx(self, kx):
        self.kx = kx
        # seta os comprimentos de flambagem da seção
        self.section_inicio.set_lx(self.comprimento(), kx)
        self.section_final.set_lx(self.comprimento(), kx)


    def set_ky(self, ky):
        self.ky = ky
        # seta os comprimentos de flambagem da seção
        self.section_inicio.set_ly(self.comprimento(), ky)
        self.section_final.set_ly(self.comprimento(), ky)


    def set_peso(self):
        lb = self.comprimento() # m

        areaMedia = self.get_sections_area()
        pesoLinear = areaMedia * 7850 # 7850 kg/m3

        peso = (lb) * pesoLinear
        self.peso_linear = pesoLinear
        self.peso = peso
        return peso

    def set_section(self, dicionarioInicio, dicionarioFinal, kx, ky): 
        self.section_inicio.set_section(dicionarioInicio)
        self.section_final.set_section(dicionarioFinal)
        self.set_kx(kx)
        self.set_ky(ky)
        self.set_peso()
        # refaz a matriz de rigidez em coordenadas local e global da barra
        self.set_kci()
    
    def set_section_inicio(self, dicionarioInicio):
        self.section_inicio.set_section(dicionarioInicio)
        self.set_peso()
        # refaz a matriz de rigidez em coordenadas local e global da barra
        self.set_kci()

    def set_section_final(self, dicionarioFinal): 
        self.section_final.set_section(dicionarioFinal)
        self.set_peso()
        # refaz a matriz de rigidez em coordenadas local e global da barra
        self.set_kci()



    # TODO ajustar metodo para fazer combinações dos esforços,
    # TODO ajustar para verificar estado limite ultimo
    # TODO ajustar para verificar estado limite de serviço (talvez separar em 2 metodos)
    def verificar(self):
        nci_rd = self.section_inicio.verificar_compressao()
        ncf_rd = self.section_final.verificar_compressao()

        nti_rd = self.section_inicio.verificar_tracao()
        ntf_rd = self.section_final.verificar_tracao()
        
        mi_rd = self.section_inicio.verificar_flexao()
        mf_rd = self.section_final.verificar_flexao()

        vi_rd = self.section_inicio.verificar_cisalhamento()
        vf_rd = self.section_final.verificar_cisalhamento()
        
        ratio_mi = round(abs(self.elu_msdi) / mi_rd, 2)
        ratio_mf = round(abs(self.elu_msdf) / mf_rd, 2)
        ratio_vi = round(abs(self.elu_vsdi) / vi_rd, 2)
        ratio_vf = round(abs(self.elu_vsdf) / vf_rd, 2)

        ratio1 = round(abs(self.elu_ncsd) / nci_rd,2)
        ratio2 = round(abs(self.elu_ntsd) / nti_rd,2)

        self.ratio_compressao = ratio1
        self.ratio_tracao = ratio2

        self.ratio_mi = ratio_mi
        self.ratio_mf = ratio_mf
        self.ratio_vi = ratio_vi
        self.ratio_vf = ratio_vf

        # forcas combinadas
        ratioi = abs(self.elu_ncsd)/(2*nci_rd) + abs(self.elu_msdi) / mi_rd + 0.02
        self.ratio_inicio = ratioi

        ratiof = abs(self.elu_ncsd)/(2*ncf_rd) + abs(self.elu_msdf) / mf_rd + 0.02
        self.ratio_final = ratiof

        return max(self.ratio_inicio, self.ratio_inicio)


    def verificar_secao_inicio(self):
        nci_rd = self.section_inicio.verificar_compressao()
        nti_rd = self.section_inicio.verificar_tracao()
        mi_rd = self.section_inicio.verificar_flexao()
        vi_rd = self.section_inicio.verificar_cisalhamento()
        
        ratio_mi = round(abs(self.elu_msdi) / mi_rd, 2)
        ratio_vi = round(abs(self.elu_vsdi) / vi_rd, 2)

        ratio1 = round(abs(self.elu_ncsd) / nci_rd,2)
        ratio2 = round(abs(self.elu_ntsd) / nti_rd,2)

        self.ratio_compressao = ratio1
        self.ratio_tracao = ratio2

        self.ratio_mi = ratio_mi
        self.ratio_vi = ratio_vi
        
        # forcas combinadas
        ratioi = abs(self.elu_ncsd)/(2*nci_rd) + abs(self.elu_msdi) / mi_rd + 0.02
        self.ratio_inicio = ratioi

        return ratioi


    def verificar_secao_final(self):
        ncf_rd = self.section_final.verificar_compressao()
        ntf_rd = self.section_final.verificar_tracao()
        mf_rd = self.section_final.verificar_flexao()
        vf_rd = self.section_final.verificar_cisalhamento()
        
        ratio_mf = round(abs(self.elu_msdf) / mf_rd, 2)
        ratio_vf = round(abs(self.elu_vsdf) / vf_rd, 2)

        ratio1 = round(abs(self.elu_ncsd) / ncf_rd,2)
        ratio2 = round(abs(self.elu_ntsd) / ntf_rd,2)

        self.ratio_compressao = ratio1
        self.ratio_tracao = ratio2

        self.ratio_mf = ratio_mf
        self.ratio_vf = ratio_vf

        # forcas combinadas
        ratio = abs(self.elu_ncsd)/(2*ncf_rd) + abs(self.elu_msdf) / mf_rd + 0.02
        self.ratio_final = ratio

        return ratio


    def x_do_momento_maximo(self):
        # ELU = Estado Limite Ultimo
        # momento_elu = Momento de ELU no inicio da barra
        # cortante_elu = Cortante de ELU no inicio da barra
        # carregamento_elu = Carregamento de ELU da barra
        momento_elu = float(self.elu_msdi)
        cortante_elu = float(self.elu_vsdi)
        carregamento_elu = float(self.carregamento_elu)
        comprimento = float(self.comprimento())

        # Função usando os coeficientes encontrados
        # usando o metodo 'Curve Fitting'
        # f(x) = Momento
        def f(x):
            y = - carregamento_elu * x ** 2 / 2 - cortante_elu * x + momento_elu
            return y

        # df(x) = Derivada do momento
        # df(x) = Cortante
        def df(x):
            y = carregamento_elu * x + cortante_elu
            return y

        # ddf(x) = Derivada do Cortante
        # ddf(x) = inclinação da Função cortante
        def ddf(x):
            y = carregamento_elu
            return y
        
        raiz_mais_alta = max(newton(df, ddf, 0), newton(df, ddf, self.comprimento()))

        return [raiz_mais_alta, f(raiz_mais_alta)]










##########################################################################################
##########################################################################################
#########################  COMBINAÇÔES DE ESFORÇOS  ######################################
##########################################################################################
##########################################################################################

    def set_combinacoes_esforcos(self):
        carregamentos = ['pp','cp','sc','su','cv 0','cv 90 i', 'cv 90 ii', 'cv 270 i', 'cv 270 ii']
        # normal, cortante_inicio, cortante_final, momento_inicio, momento_final
        pp = self.portico.carregamentos[0][1][0]
        cp = self.portico.carregamentos[1][1][0]
        sc = self.portico.carregamentos[2][1][0]
        su = self.portico.carregamentos[3][1][0]

        cv_0 = self.portico.carregamentos[4][1][0]

        carr_elu_sc = 1.25*(pp +cp) + 1.5*sc + 1.4*su
        carr_elu_cv = pp + cp + 1.4 * cv_0

        if abs(carr_elu_cv) > abs(carr_elu_sc):
            self.carregamento_elu = carr_elu_cv
        else:
            self.carregamento_elu = carr_elu_sc

        ### ESFORÇO NORMAL DA BARRA
        n_pp = self.normal['pp']
        n_cp = self.normal['cp']
        n_sc = self.normal['sc']
        n_su = self.normal['su']

        n_cv_0 = self.normal['cv 0']
        n_cv_90i = self.normal['cv 90 i']
        n_cv_90ii = self.normal['cv 90 ii']
        n_cv_270i = self.normal['cv 270 i']
        n_cv_270ii = self.normal['cv 270 ii']

        ### ESFORÇOS DE CORTANTE NO INICIAL DA BARRA
        vi_pp = self.cortante_inicio['pp']
        vi_cp = self.cortante_inicio['cp']
        vi_sc = self.cortante_inicio['sc']
        vi_su = self.cortante_inicio['su']

        vi_cv_0 = self.cortante_inicio['cv 0']
        vi_cv_90i = self.cortante_inicio['cv 90 i']
        vi_cv_90ii = self.cortante_inicio['cv 90 ii']
        vi_cv_270i = self.cortante_inicio['cv 270 i']
        vi_cv_270ii = self.cortante_inicio['cv 270 ii']
        
        ### ESFORÇOS DE MOMENTO NO INICIAL DA BARRA
        mi_pp = self.momento_inicio['pp']
        mi_cp = self.momento_inicio['cp']
        mi_sc = self.momento_inicio['sc']
        mi_su = self.momento_inicio['su']

        mi_cv_0 = self.momento_inicio['cv 0']
        mi_cv_90i = self.momento_inicio['cv 90 i']
        mi_cv_90ii = self.momento_inicio['cv 90 ii']
        mi_cv_270i = self.momento_inicio['cv 270 i']
        mi_cv_270ii = self.momento_inicio['cv 270 ii']
        
        ### ESFORÇOS DE CORTANTE NO FINAL DA BARRA
        vf_pp = self.cortante_final['pp']
        vf_cp = self.cortante_final['cp']
        vf_sc = self.cortante_final['sc']
        vf_su = self.cortante_final['su']

        vf_cv_0 = self.cortante_final['cv 0']
        vf_cv_90i = self.cortante_final['cv 90 i']
        vf_cv_90ii = self.cortante_final['cv 90 ii']
        vf_cv_270i = self.cortante_final['cv 270 i']
        vf_cv_270ii = self.cortante_final['cv 270 ii']
        
        ### ESFORÇOS DE MOMENTO NO FINAL DA BARRA
        mf_pp = self.momento_final['pp']
        mf_cp = self.momento_final['cp']
        mf_sc = self.momento_final['sc']
        mf_su = self.momento_final['su']

        mf_cv_0 = self.momento_final['cv 0']
        mf_cv_90i = self.momento_final['cv 90 i']
        mf_cv_90ii = self.momento_final['cv 90 ii']
        mf_cv_270i = self.momento_final['cv 270 i']
        mf_cv_270ii = self.momento_final['cv 270 ii']
        
        #################################################################
        # elu_sc = 1.25x(pp+cp) + 1.5xSC + 1.4xSU
        # elu_cv = 1.00x(pp+cp) + 1.4xCV
        # elu_sc_cv = 1.25x(pp+cp) + 1.5xSC + 1.4xSU + 0,84xCV
        # elu_cv_sc = 1.25x(pp+cp) + 1.2xSC + 1.05xSU + 1,4xCV
        #################################################################
        ##### COMBINAÇÃO DE NORMAL DAS BARRAS
        # elu_sc = 1.25x(pp+cp) + 1.5xSC + 1.4xSU
        # elu_cv = 1.00x(pp+cp) + 1.4xCV
        elu_n_a =  1.25 * (n_pp + n_cp) + 1.5 * n_sc + 1.4 * n_su
        elu_nc = min((elu_n_a), 0)
        elu_nt = max((elu_n_a), 0)

        elu_n_b = 1.00 * (n_pp + n_cp) + 1.4 * n_cv_0
        elu_nc = min((elu_nc), (elu_n_b))
        elu_nt = max((elu_nt), (elu_n_b))

        elu_n_b = 1.00 * (n_pp + n_cp) + 1.4 * n_cv_90i
        elu_nc = min((elu_nc), (elu_n_b))
        elu_nt = max((elu_nt), (elu_n_b))

        elu_n_b = 1.00 * (n_pp + n_cp) + 1.4 * n_cv_90ii
        elu_nc = min((elu_nc), (elu_n_b))
        elu_nt = max((elu_nt), (elu_n_b))

        elu_n_b = 1.00 * (n_pp + n_cp) + 1.4 * n_cv_270i
        elu_nc = min((elu_nc), (elu_n_b))
        elu_nt = max((elu_nt), (elu_n_b))

        elu_n_b = 1.00 * (n_pp + n_cp) + 1.4 * n_cv_270ii
        elu_nc = min((elu_nc), (elu_n_b))
        elu_nt = max((elu_nt), (elu_n_b))



        ##### COMBINAÇÃO DE CORTANTE INICIO DAS BARRAS
        # elu_sc = 1.25x(pp+cp) + 1.5xSC + 1.4xSU
        # elu_cv = 1.00x(pp+cp) + 1.4xCV
        elu_vi_a =  1.25 * (vi_pp + vi_cp) + 1.5 * vi_sc + 1.4 * vi_su
        elu_vi_b = 1.00 * (vi_pp + vi_cp) + 1.4 * vi_cv_0
        if abs(elu_vi_a) > abs(elu_vi_b):
            elu_vi = -elu_vi_a
        else:
            elu_vi = -elu_vi_b
        # elu_vi = max(abs(elu_vi_a), abs(elu_vi_b))

        elu_vi_b = 1.00 * (vi_pp + vi_cp) + 1.4 * vi_cv_90i
        if abs(elu_vi) < abs(elu_vi_b):
            elu_vi = -elu_vi_b
        # elu_vi = max(abs(elu_vi), abs(elu_vi_b))

        elu_vi_b = 1.00 * (vi_pp + vi_cp) + 1.4 * vi_cv_90ii
        if abs(elu_vi) < abs(elu_vi_b):
            elu_vi = -elu_vi_b
        # elu_vi = max(abs(elu_vi), abs(elu_vi_b))

        elu_vi_b = 1.00 * (vi_pp + vi_cp) + 1.4 * vi_cv_270i
        if abs(elu_vi) < abs(elu_vi_b):
            elu_vi = -elu_vi_b
        # elu_vi = max(abs(elu_vi), abs(elu_vi_b))

        elu_vi_b = 1.00 * (vi_pp + vi_cp) + 1.4 * vi_cv_270ii
        if abs(elu_vi) < abs(elu_vi_b):
            elu_vi = -elu_vi_b
        # elu_vi = max(abs(elu_vi), abs(elu_vi_b))


        ##### COMBINAÇÃO DE MOMENTOS INICIO DAS BARRAS
        # elu_sc = 1.25x(pp+cp) + 1.5xSC + 1.4xSU
        # elu_cv = 1.00x(pp+cp) + 1.4xCV
        elu_mi_a =  1.25 * (mi_pp + mi_cp) + 1.5 * mi_sc + 1.4 * mi_su
        elu_mi_b = 1.00 * (mi_pp + mi_cp) + 1.4 * mi_cv_0
        if abs(elu_mi_a) > abs(elu_mi_b):
            elu_mi = -elu_mi_a
        else:
            elu_mi = -elu_mi_b
        # elu_mi = max(abs(elu_mi_a), abs(elu_mi_b))

        elu_mi_b = 1.00 * (mi_pp + mi_cp) + 1.4 * mi_cv_90i
        if abs(elu_mi) < abs(elu_mi_b):
            elu_mi = -elu_mi_b
        # elu_mi = max(abs(elu_mi), abs(elu_mi_b))

        elu_mi_b = 1.00 * (mi_pp + mi_cp) + 1.4 * mi_cv_90ii
        if abs(elu_mi) < abs(elu_mi_b):
            elu_mi = -elu_mi_b
        # elu_mi = max(abs(elu_mi), abs(elu_mi_b))

        elu_mi_b = 1.00 * (mi_pp + mi_cp) + 1.4 * mi_cv_270i
        if abs(elu_mi) < abs(elu_mi_b):
            elu_mi = -elu_mi_b
        # elu_mi = max(abs(elu_mi), abs(elu_mi_b))

        elu_mi_b = 1.00 * (mi_pp + mi_cp) + 1.4 * mi_cv_270ii
        if abs(elu_mi) < abs(elu_mi_b):
            elu_mi = -elu_mi_b
        # elu_mi = max(abs(elu_mi), abs(elu_mi_b))

        
        ##### COMBINAÇÃO DE CORTANTE FINAL DAS BARRAS
        # elu_sc = 1.25x(pp+cp) + 1.5xSC + 1.4xSU
        # elu_cv = 1.00x(pp+cp) + 1.4xCV
        elu_vf_a =  1.25 * (vf_pp + vf_cp) + 1.5 * vf_sc + 1.4 * vf_su
        elu_vf_b = 1.00 * (vf_pp + vf_cp) + 1.4 * vf_cv_0
        if abs(elu_vf_a) > abs(elu_vf_b):
            elu_vf = elu_vf_a
        else:
            elu_vf = elu_vf_b
        # elu_vf = max(abs(elu_vf_a), abs(elu_vf_b))

        elu_vf_b = 1.00 * (vf_pp + vf_cp) + 1.4 * vf_cv_90i
        if abs(elu_vf) < abs(elu_vf_b):
            elu_vf = elu_mi_b
        # elu_vf = max(abs(elu_vf), abs(elu_vf_b))

        elu_vf_b = 1.00 * (vf_pp + vf_cp) + 1.4 * vf_cv_90ii
        if abs(elu_vf) < abs(elu_vf_b):
            elu_vf = elu_mi_b
        # elu_vf = max(abs(elu_vf), abs(elu_vf_b))

        elu_vf_b = 1.00 * (vf_pp + vf_cp) + 1.4 * vf_cv_270i
        if abs(elu_vf) < abs(elu_vf_b):
            elu_vf = elu_mi_b
        # elu_vf = max(abs(elu_vf), abs(elu_vf_b))

        elu_vf_b = 1.00 * (vf_pp + vf_cp) + 1.4 * vf_cv_270ii
        if abs(elu_vf) < abs(elu_vf_b):
            elu_vf = elu_mi_b
        # elu_vf = max(abs(elu_vf), abs(elu_vf_b))


        ##### COMBINAÇÃO DE MOMENTOS FINAL DAS BARRAS
        # elu_sc = 1.25x(pp+cp) + 1.5xSC + 1.4xSU
        # elu_cv = 1.00x(pp+cp) + 1.4xCV
        elu_mf_a =  1.25 * (mf_pp + mf_cp) + 1.5 * mf_sc + 1.4 * mf_su
        elu_mf_b = 1.00 * (mf_pp + mf_cp) + 1.4 * mf_cv_0
        if abs(elu_mf_a) > abs(elu_mf_b):
            elu_mf = elu_mf_a
        else:
            elu_mf = elu_mf_b
        # elu_mf = max(abs(elu_mf_a), abs(elu_mf_b))

        elu_mf_b = 1.00 * (mf_pp + mf_cp) + 1.4 * mf_cv_90i
        if abs(elu_mf) < abs(elu_mf_b):
            elu_mf = elu_mf_b
        # elu_mf = max(abs(elu_mf), abs(elu_mf_b))

        elu_mf_b = 1.00 * (mf_pp + mf_cp) + 1.4 * mf_cv_90ii
        if abs(elu_mf) < abs(elu_mf_b):
            elu_mf = elu_mf_b
        # elu_mf = max(abs(elu_mf), abs(elu_mf_b))

        elu_mf_b = 1.00 * (mf_pp + mf_cp) + 1.4 * mf_cv_270i
        if abs(elu_mf) < abs(elu_mf_b):
            elu_mf = elu_mf_b
        # elu_mf = max(abs(elu_mf), abs(elu_mf_b))

        elu_mf_b = 1.00 * (mf_pp + mf_cp) + 1.4 * mf_cv_270ii
        if abs(elu_mf) < abs(elu_mf_b):
            elu_mf = elu_mf_b
        # elu_mf = max(abs(elu_mf), abs(elu_mf_b))
        
        self.elu_ntsd = elu_nt # Tração
        self.elu_ncsd = elu_nc # Compressão

        self.elu_msdi = elu_mi # Momento Inicio da Barra
        self.elu_msdf = elu_mf # Momento Final da Barra

        self.elu_vsdi = elu_vi # Cortante Inicio da Barra
        self.elu_vsdf = elu_vf # Cortante Final da Barra

        


def newton(f, fl, x):
    if fl(x) == 0.0:
        xnew = x
        return xnew
    
    for i in range(1,101):
        xnew = x - f(x) / fl(x)
        if abs(xnew - x) < 0.00000001:
            break
   
    return xnew    




def red(numero):
    return round(numero,2)