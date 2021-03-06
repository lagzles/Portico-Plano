###########################################################
# PERFIL SOLDADO
# ##################################### 
# 
ya1 = 1.1

def verificacao_flexao_FLA(Section): #d, tw, tf, wx, zx, fy):
    hw = Section.d - 2 * Section.tfs
    lambda_ = hw / Section.tw
    lambda_p = 3.76 * (Section.e / Section.fy) ** 0.5
    lambda_r = 5.70 * (Section.e / Section.fy) ** 0.5

    mpl = Section.zx * Section.fy
    mr = Section.wx * Section.fy

    if lambda_ <= lambda_p:
        return mpl  / ya1

    elif lambda_ <= lambda_r:
        return 1  / ya1* (mpl - ( mpl - mr) * ((lambda_ - lambda_p) / (lambda_r - lambda_p)))

    elif lambda_ > lambda_r:
        return mr / ya1
        

def verificacao_flexao_FLM(Section): #bf, tf, kc, wx, zx, tensaor, fy):
    lambda_ = Section.bfs / (2 * Section.tfs)
    lambda_p = 0.38 * (Section.e / Section.fy) ** 0.5
    lambda_r = 0.95 * (Section.e / ((Section.fy - Section.tensaor) / Section.kc)) ** 0.5

    mpl = Section.zx * Section.fy
    mr = Section.wx* (Section.fy - Section.tensaor)
    mcr = Section.wx * 0.9 * Section.e * Section.kc / (lambda_ ** 2)

    if lambda_ <= lambda_p:
        return mpl / ya1

    elif lambda_ <= lambda_r:
        return 1 / ya1* (mpl - ( mpl - mr) * ((lambda_ - lambda_p) / (lambda_r - lambda_p)))

    elif lambda_ > lambda_r:
        return mcr  / ya1


def verificacao_flexao_FLT(Section): #ly, ry, iy, it, wx, zx, cw, tensaor, fy):
    j = Section.it
    b1 = (Section.fy - Section.tensaor) * Section.wx / ( Section.e * j)

    # lambda_ = Section.ly * Section.ky / Section.ry
    lambda_ = Section.ly / Section.ry
    lambda_p = 1.76 * (Section.e / Section.fy) ** 0.5
    lambda_r = (1.38 * (Section.iy * j) ** 0.5) / (Section.ry * Section.j * b1) * ( 1 + (1 + (27 * Section.cw * b1 ** 2) / Section.iy) ** 0.5) ** 0.5
    # lambda_r = (1.38 * (Section.iy * j) ** 0.5) / (Section.ly**2) * ( 1 + (1 + (27 * Section.cw * b1 ** 2) / Section.iy) ** 0.5) ** 0.5

    mpl = Section.zx * Section.fy
    mr = Section.wx * (Section.fy - Section.tensaor)
    mcr = ((1 * 3.14 ** 2) * Section.e * Section.iy / (Section.ly ** 2)) * ( Section.cw / Section.ly * ( 1 + 0.039 * Section.j * (Section.ly ** 2) / Section.cw)) ** 0.5

    if lambda_ <= lambda_p:
        return mpl  / ya1

    elif lambda_ <= lambda_r:
        return 1  / ya1 * (mpl - ( mpl - mr) * ((lambda_ - lambda_p) / (lambda_r - lambda_p)))

    elif lambda_ > lambda_r:
        return mcr / ya1

def verificacao_cisalhamento(Section): #d, tw, tf, fy):
    hw = Section.d - 2 * Section.tfs
    lambda_ = hw / Section.tw
    kv = 5
    lambda_p = 1.10 * (kv * Section.e / Section.fy) ** 0.5
    lambda_r = 1.37 * ( kv * Section.e) ** 0.5

    aw = hw * Section.tw
    vpl = 0.6 * aw * Section.fy
    cv = 0
    # if lambda_ <= lambda_p:
    #     cv = 1
    # elif lambda_ <= lambda_r:
    #     # print('cisalhamento')
    #     continue

    if lambda_ <= lambda_p:
        return vpl / 1.15

    elif lambda_ <= lambda_r:
        return lambda_p / lambda_ * vpl / 1.15

    elif lambda_ > lambda_r:
        return 1.24 * (lambda_p / lambda_) ** 2 * vpl / 1.15

   
###########################################################
# COMPRESSAO
# #####################################    
def compressao_soldado(Section):
    kyly = Section.ly
    kzlz = kyly
    xo = 0
    yo = 0
    rx = Section.set_rx()
    ry = Section.set_ry()
    ro = (rx ** 2 + ry ** 2 + xo ** 2 + yo ** 2) ** 0.5
    area = Section.get_area()
    fy = Section.fy

    fatorXi = 1
    fatorQ = detfatorQ(Section, fatorXi)

    ne = n_e(Section, kzlz, ro)
    lambZero = detlambZero(Section, fatorQ, ne)
    
    fatorXf = fatorXi
    fatorXi = detfatorX(Section, lambZero)
    
    while round(fatorXf,4) != round(fatorXi,4):
    
        fatorQ = detfatorQ(Section, fatorXi)
        ne = n_e(Section, kzlz, ro)
        lambZero = detlambZero(Section, fatorQ, ne)
        
        fatorXf = fatorXi
        fatorXi = detfatorX(Section, lambZero)
    
    fatorX = fatorXf
    
    nc_rd = fatorX * fatorQ * area * fy / 1.15
    return nc_rd


def detfatorQ(Section, fatorX):
    ca = 0.34
    sigma = fatorX * Section.fy

    # Elemento AA
    hw = Section.d - Section.tfs - Section.tfi
    # area_bruta = hw * Section.tw
    area_bruta = Section.get_area()

    largura_efetiva = 1.92 * Section.tw * ((Section.e / sigma) ** 0.5) * (1 - ca / (hw / Section.tw) * ((Section.e / sigma) ** 0.5))
        
    if largura_efetiva >= hw:
        fatorQa = 1
    else:
        area_efetiva = area_bruta - (hw - largura_efetiva) * Section.tw
        fatorQa = area_efetiva / area_bruta
    
    # Elemento AL - Grupo 5 NBR 8800
    b = Section.bfs / 2
    t = Section.tfs
    kc = 4 / ((Section.d - Section.tfs - Section.tfi) / Section.tw) ** 0.5
    if kc <= 0.35:
        kc = 0.35
    elif kc >= 0.76:
        kc = 0.76
        
    btlimite = 0.64 * (Section.e / (Section.fy / kc)) ** 0.5
    btminimo = 1.17 * ((Section.e / (Section.fy / kc)) ** 0.5)
    
    bt = b / t

    if bt <= btlimite:
        fatorQs = 1.0    
    elif bt > btlimite and bt <= btminimo:        
        fatorQs = 1.415 - 0.65 * bt * (Section.fy / (kc * Section.e)) ** 0.5
        
    elif bt > btminimo:
        fatorQs = 0.9 * Section.e * kc / (Section.fy * (bt ** 2))
            
    if fatorQs < 0:        
        fatorQs = 0
        
    detfatorQ = fatorQs * fatorQa
    return detfatorQ

def ne_x(Section):
    return (3.14 ** 2) * Section.e * Section.ix / ((Section.lx) ** 2)


def ne_y(Section):
    return (3.14 ** 2) * Section.e * Section.iy / ((Section.ly) ** 2)


def ne_z(Section, kzlz, ro):
    return (1 / ro ** 2) * (((3.14 ** 2) * Section.e * Section.cw) / ((kzlz) ** 2) + Section.g * Section.j)


def n_e(Section, kzlz, ro):
    nex = ne_x(Section)
    ney = ne_y(Section)
    nez = ne_z(Section, kzlz, ro)    
    n_e = min(nex, ney, nez)
    return n_e


def detlambZero(Section, fatorQ, ne):
    detlambZero = (fatorQ * Section.get_area() * Section.fy / ne) ** 0.5
    return detlambZero


def detfatorX(Section, lambZero):
    if lambZero <= 1.5:
        detfatorX = (0.658 ** (lambZero ** 2))
    else:
        detfatorX = 0.877 / (lambZero ** 2)
    return detfatorX

# #####################################    
# #####################################    
# TRACAO

def tracao_soldado(Section):
    area = Section.get_area()
    fy = Section.fy

    return area * fy / 1.11
# #####################################    
# PERFIL DOBRADO
# #####################################    
# COMPRESSAO
def compressao_dobrado(Section):
    if Section.tw == 0.3 and Section.d == 29.20: # '292x3.00'
        ae = 11.49
        fy = Section.fy
        if Section.lx <= 300:
            lambda_c = 1.27
            pn = ae * fy * (0.658 ** (lambda_c**2))
        else: # comprimento da barra maior que 3m
            lambda_c = 2.11
            pn = ae * fy * (0.877 / (lambda_c**2))

        return 0.85 * pn
    elif Section.tw == 0.265 and Section.d == 29.20: # '292x2.65':
        ae = 9.70
        fy = Section.fy
        if Section.lx <= 300:
            lambda_c = 1.27
            pn = ae * fy * (0.658 ** (lambda_c**2))
        else: # comprimento da barra maior que 3m
            lambda_c = 2.11
            pn = ae * fy * (0.877 / (lambda_c**2))
        return 0.85 * pn
    elif Section.tw == 0.225 and Section.d == 29.20: # '292x2.25':
        ae = 7.48
        fy = Section.fy
        if Section.lx <= 300:
            lambda_c = 1.27
            pn = ae * fy * (0.658 ** (lambda_c**2))
        else: # comprimento da barra maior que 3m
            lambda_c = 2.12
            pn = ae * fy * (0.877 / (lambda_c**2))
        return 0.85 * pn
    else: # self.tw == 2.00 and self.d == 292.0: # '292x2.00':
        ae = 6.31
        fy = Section.fy
        if Section.lx <= 300:
            lambda_c = 1.28
            pn = ae * fy * (0.658 ** (lambda_c**2))
        else: # comprimento da barra maior que 3m
            lambda_c = 2.14
            pn = ae * fy * (0.877 / (lambda_c**2))
        return 0.85 * pn

# TRACAO
def tracao_dobrado(Section):
    area = Section.get_area()
    fy = Section.fy

    return area * fy / 1.11


