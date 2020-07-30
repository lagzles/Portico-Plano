from Portico import Portico
import time

# print(round(time.time()-agora0, 2), ' segundos total de verificação')


# def VerificarPorColunasEvigas2(portico):
#     agora0 = time.time()
#     iterr = 0

#     coisa = time.time()
#     portico.AnaliseMatricial()
#     # portico.PegarVigasELU_ELS()
#     portico.OtimizarBarras()
#     portico.OtimizarColunas()
#     # portico.OtimizarVigasPorSecaoELUELS()
#     peso_f = portico.SetarPeso()
#     print(time.time() - coisa, peso_f )
# # 
#     peso_i = 1
#     iterr = 0
#     iterr +=1
#     while ((peso_f != peso_i) and iterr < 10): ##iterr < 9:# (peso_f != peso_i): ##
#         peso_i = peso_f
#         coisa = time.time()

#         portico.AnaliseMatricial()

#         portico.PegarVigasELU_ELS()
#         portico.OtimizarColunas()
#         # portico.OtimizarVigasPorSecaoELUELS()

#         iterr += 1
#         peso_f = portico.SetarPeso()
#         print(time.time() - coisa, peso_f)
    
#     print(iterr, "fim do processo de Pegando Secoess, Peso=", portico.SetarPeso(), round((time.time()-agora0)/ 60.0, 2), ' minutos')
#     # print("fim do processo de Vigas e Colunas, Peso=", portico.SetarPeso())
#     # print(round(time.time()-agora0, 2) / 60.0, ' minutos')





def VerificarPorColunasEvigas(portico):
    agora0 = time.time()
    iterr = 0

    # coisa = time.time()
    portico.AnaliseMatricial()
    portico.OtimizarColunas()
    portico.OtimizarVigas()
    # print(time.time() - coisa)

    peso_f = portico.SetarPeso()
    peso_i = 1
    iterr = 0
    iterr +=1
    while ((peso_f != peso_i) and iterr < 10): ##iterr < 9:# (peso_f != peso_i): ##
        peso_i = peso_f
        # coisa = time.time()

        portico.AnaliseMatricial()

        portico.OtimizarColunas()
        portico.OtimizarVigas()

        iterr += 1
        peso_f = portico.SetarPeso()
        # print(time.time() - coisa, peso_f)
    
    # print(iterr, "fim do processo de Vigas e Colunas, Peso=", portico.SetarPeso(), round((time.time()-agora0)/ 60.0, 2), ' minutos')
    # print("fim do processo de Vigas e Colunas, Peso=", portico.SetarPeso())
    # print(round(time.time()-agora0, 2) / 60.0, ' minutos')









def VerificarGeral(portico):
    agora0 = time.time()
    iterr = 0

    portico.AnaliseMatricial()
    portico.OtimizarBarras()

    peso_f = portico.SetarPeso()
    peso_i = 1
    iterr = 0
    iterr +=1
    while ((peso_f != peso_i) and iterr < 10): ##iterr < 9:# (peso_f != peso_i): ##
        peso_i = peso_f
        coisa = time.time()
        portico.AnaliseMatricial()
        portico.OtimizarBarras()
        iterr += 1
        peso_f = portico.SetarPeso()
        # print(time.time() - coisa, peso_f)
    
    # print(iterr, "fim do processo Geral, Peso=", portico.SetarPeso(), round((time.time()-agora0)/ 60.0, 2), ' minutos')
    # print(round((time.time()-agora0)/ 60.0, 2) / 60.0, ' minutos')



def FazerCarregamentosParaPortico(cp_linear, sc_linear, su_linear, cv_linear, cv_fechamento, duas_aguas):
    cpL = cp * influencia 
    scL = sc * influencia
    suL = su * influencia
    cvL = cv * influencia
    cvF = cv * influencia_fech


    carregamentos = []
    # carregamento = [tipo, [vertical agua esquerda, vertical agua direita, horizontal esquerda, horizontal direita]]
    carr0 = ['pp',   [  0,  0,  0,  0]] # valores serão setados na analise
    carr1 = ['cp',   [- cp_linear, -cp_linear,   0,  0]]
    carr2 = ['sc',   [-sc_linear, -sc_linear,   0,  0]]
    carr3 = ['su',   [-su_linear, -su_linear,   0,  0]]

    if duas_aguas:
        # carregamento de vento para cobertura 2 aguas
        carr4 = ['cv 0',      [ cv_linear,  cv_linear, cvL, -cvL]]
        carr5 = ['cv 90 i',   [ 0.53*cv_linear,  0.10*cv_linear, -1.00*cv_fechamento, -0.20*cv_fechamento]] # >
        carr6 = ['cv 90 ii',  [ 1.03*cv_linear,  0.60*cv_linear, -0.50*cv_fechamento, -0.70*cv_fechamento]] # >>
        carr7 = ['cv 270 i',  [ 0.10*cv_linear,  0.53*cv_linear, +0.20*cv_fechamento, +1.00*cv_fechamento]] # <
        carr8 = ['cv 270 ii', [ 0.60*cv_linear,  1.03*cv_linear, +0.70*cv_fechamento, +0.50*cv_fechamento]] # <<

    else:
        # carregamento de vento para cobertura 1 agua
        carr4 = ['cv 0',      [ 1.20*cv_linear,  1.20*cv_linear, cv_fechamento, -cv_fechamento]]
        carr5 = ['cv 90 i',   [ 0.70*cv_linear,  0.70*cv_linear, -1.00*cv_fechamento, -0.20*cv_fechamento]] # >
        carr6 = ['cv 90 ii',  [ 1.20*cv_linear,  1.20*cv_linear, -0.50*cv_fechamento, -0.70*cv_fechamento]] # >>
        carr7 = ['cv 270 i',  [ 0.70*cv_linear,  0.70*cv_linear, +0.20*cv_fechamento, +1.00*cv_fechamento]] # <
        carr8 = ['cv 270 ii', [ 1.20*cv_linear,  1.20*cv_linear, +0.70*cv_fechamento, +0.50*cv_fechamento]] # <<

    carregamentos.append(carr0)
    carregamentos.append(carr1)
    carregamentos.append(carr2)
    carregamentos.append(carr3)
    carregamentos.append(carr4)
    carregamentos.append(carr5)
    carregamentos.append(carr6)
    carregamentos.append(carr7)
    carregamentos.append(carr8)

    return carregamentos




































print('hhh'*4)
print('começando rotina teste')

# valores em cm
# bracel armazem de celulose
vaos = [30.0,22.6,30.0]
pd = 11
cumeeira = 41.3
inc = 3
influencia = 21.000
duas_aguas = True
altura_minima = 900.0
# pilar_metalico = False
pilar_metalico = True

cp = 30 # kgf/m²
sc = 25 # kgf/m²
su = 15 # kgf/m²
cv = 97 # kgf/m²

influencia_fech = influencia
if influencia > 14.0:
    influencia_fech = influencia / 2.0

cpL = cp * influencia 
scL = sc * influencia
suL = su * influencia
cvL = cv * influencia
cvF = cv * influencia_fech

carregamentos = FazerCarregamentosParaPortico(cpL, scL, suL, cvL, cvF, duas_aguas)
portico = Portico(vaos, pd, cumeeira, inc, influencia, altura_minima, pilar_metalico)
portico.SetarCarregamentos(carregamentos)

print("Obra Armazem de Celulose, Pilar Metalico ")
# # VerificarGeral(portico)
VerificarPorColunasEvigas(portico)
# VerificarPorColunasEvigas2(portico)

portico.AnaliseMatricial()
for barra in portico.lista_barras:
    barra.verificar_elu()
    ratio_elu = max(barra.ratio_inicio_elu, barra.ratio_final_elu)
    ratio_els = barra.verificar_els()
    if ratio_elu > 1.0 or ratio_els > 1.0:
        print(barra.tipo,barra.section_inicio, barra.section_final, ratio_elu, ratio_els)



print("Obra Armazem de Celulose, Pilar Concreto ")

pilar_metalico = False
portico = Portico(vaos, pd, cumeeira, inc, influencia, altura_minima, pilar_metalico)
portico.SetarCarregamentos(carregamentos)
# # VerificarGeral(portico)
VerificarPorColunasEvigas(portico)
# VerificarPorColunasEvigas2(portico)


portico.AnaliseMatricial()
for barra in portico.lista_barras:
    barra.verificar_elu()
    ratio_elu = max(barra.ratio_inicio_elu, barra.ratio_final_elu)
    ratio_els = barra.verificar_els()
    if ratio_elu > 1.0 or ratio_els > 1.0:
        print(barra.tipo,barra.section_inicio, barra.section_final, ratio_elu, ratio_els)


######################################################################################################
# CD Zimba Castelo branco
vaos = [22.0, 22.00 ,19.0]
pd = 12.0
cumeeira = 63.0
inc = 3
influencia = 21.500
duas_aguas = False
altura_minima = 900.0
pilar_metalico = True
# pilar_metalico = False

cp = 19.8 # kgf/m²
sc = 25 # kgf/m²
su = 40 # kgf/m²
cv = 86 # kgf/m²

influencia_fech = influencia
if influencia > 14.0:
    influencia_fech = influencia / 2.0

cpL = cp * influencia 
scL = sc * influencia
suL = su * influencia
cvL = cv * influencia
cvF = cv * influencia_fech

carregamentos = FazerCarregamentosParaPortico(cpL, scL, suL, cvL, cvF, duas_aguas)
portico = Portico(vaos, pd, cumeeira, inc, influencia, altura_minima, pilar_metalico)
portico.SetarCarregamentos(carregamentos)

print("Obra CD Zimba Castelo Branco, Pilar de Metalico")
# VerificarGeral(portico)
VerificarPorColunasEvigas(portico)
# VerificarPorColunasEvigas2(portico)

portico.AnaliseMatricial()
for barra in portico.lista_barras:
    barra.verificar_elu()
    ratio_elu = max(barra.ratio_inicio_elu, barra.ratio_final_elu)
    ratio_els = barra.verificar_els()
    if ratio_elu > 1.0 or ratio_els > 1.0:
        print(barra.tipo, barra.section_inicio, barra.section_final, ratio_elu, ratio_els)

print("Obra CD Zimba Castelo Branco, Pilar de Concreto")
pilar_metalico = False
portico = Portico(vaos, pd, cumeeira, inc, influencia, altura_minima, pilar_metalico)
portico.SetarCarregamentos(carregamentos)
# VerificarGeral(portico)
VerificarPorColunasEvigas(portico)
# VerificarPorColunasEvigas2(portico)


portico.AnaliseMatricial()
for barra in portico.lista_barras:
    barra.verificar_elu()
    ratio_elu = max(barra.ratio_inicio_elu, barra.ratio_final_elu)
    ratio_els = barra.verificar_els()
    if ratio_elu > 1.0 or ratio_els > 1.0:
        print(barra.tipo,barra.section_inicio, barra.section_final, ratio_elu, ratio_els)

######################################################################################################

#BTS Bonito
vaos = [17.0, 25.00, 25.00, 25.00, 25.00 ,17.0]
pd = 10.0
cumeeira = 67.0
inc = 3
influencia = 12.500
duas_aguas = True
altura_minima = 0.0
pilar_metalico = False

cp = 15.68 # kgf/m²
sc = 25 # kgf/m²
su = 15 # kgf/m²
cv = 39 # kgf/m²

influencia_fech = influencia
if influencia > 14.0:
    influencia_fech = influencia / 2.0

cpL = cp * influencia 
scL = sc * influencia
suL = su * influencia
cvL = cv * influencia
cvF = cv * influencia_fech

# carregamentos = FazerCarregamentosParaPortico(cpL, scL, suL, cvL, cvF, duas_aguas)
# coisa = time.time()
# portico = Portico(vaos, pd, cumeeira, inc, influencia, altura_minima, pilar_metalico)
# portico.SetarCarregamentos(carregamentos)
# print(time.time() - coisa)

# print("Obra BTS Bonito, Pilar de concreto")
# # # VerificarGeral(portico)
# VerificarPorColunasEvigas2(portico)


######################################################################################################


