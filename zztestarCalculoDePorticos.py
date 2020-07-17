from Portico import Portico
import time

print('\n hhh'*4)
print('começando rotina teste')

# valores em cm
# bracel armazem de celulose
vaos = [30.0,22.6,30.0]
pd = 11
cumeeira = 41.3
inc = 3
influencia = 21.000
duas_aguas = True
altura_minima = 0

cp = 30 # kgf/m²
sc = 25 # kgf/m²
su = 15 # kgf/m²
cv = 97 # kgf/m²

# # CD Zimba Castelo branco
# vaos = [22.0, 22.00 ,19.0]
# pd = 12.0
# cumeeira = 63.0
# inc = 3
# influencia = 21.500
# duas_aguas = False
# altura_minima = 900.0

# cp = 20 # kgf/m²
# sc = 25 # kgf/m²
# su = 40 # kgf/m²
# cv = 86 # kgf/m²


portico = Portico(vaos, pd, cumeeira, inc, influencia, altura_minima)

influencia_fech = influencia
if influencia > 14.0:
    influencia_fech = influencia / 2.0

cpL = cp * influencia 
scL = sc * influencia
suL = su * influencia
cvL = cv * influencia_fech


carregamentos = []
# carregamento = [tipo, [vertical agua esquerda, vertical agua direita, horizontal esquerda, horizontal direita]]
carr0 = ['pp',   [  0,  0,  0,  0]] # valores serão setados na analise
carr1 = ['cp',   [- cpL, -cpL,   0,  0]]
carr2 = ['sc',   [-scL, -scL,   0,  0]]
carr3 = ['su',   [-suL, -suL,   0,  0]]

if duas_aguas:
    # carregamento de vento para cobertura 2 aguas
    carr4 = ['cv 0', [ cvL,  cvL, cvL, -cvL]]
    # carr4 = ['cv 0', [ 10,  10, 10, -10]]
    carr5 = ['cv 90 i',   [ 0.53*cvL,  0.10*cvL, -1.00*cvL, -0.20*cvL]] # >
    carr6 = ['cv 90 ii',  [ 1.03*cvL,  0.60*cvL, -0.50*cvL, -0.70*cvL]] # >>
    carr7 = ['cv 270 i',  [ 0.10*cvL,  0.53*cvL, +0.20*cvL, +1.00*cvL]] # <
    carr8 = ['cv 270 ii', [ 0.60*cvL,  1.03*cvL, +0.70*cvL, +0.50*cvL]] # <<

else:
    # carregamento de vento para cobertura 1 agua
    carr4 = ['cv 0', [ 1.20*cvL,  1.20*cvL, cvL, -cvL]]
    carr5 = ['cv 90 i',   [ 0.70*cvL,  0.70*cvL, -1.00*cvL, -0.20*cvL]] # >
    carr6 = ['cv 90 ii',  [ 1.20*cvL,  1.20*cvL, -0.50*cvL, -0.70*cvL]] # >>
    carr7 = ['cv 270 i',  [ 0.70*cvL,  0.70*cvL, +0.20*cvL, +1.00*cvL]] # <
    carr8 = ['cv 270 ii', [ 1.20*cvL,  1.20*cvL, +0.70*cvL, +0.50*cvL]] # <<

carregamentos.append(carr0)
carregamentos.append(carr1)
carregamentos.append(carr2)
carregamentos.append(carr3)
carregamentos.append(carr4)
carregamentos.append(carr5)
carregamentos.append(carr6)
carregamentos.append(carr7)
carregamentos.append(carr8)

portico.SetarCarregamentos(carregamentos)
agora0 = time.time()
agora1 = time.time()
iterr = 0

portico.AnaliseMatricial()
print(round(time.time()-agora1, 2), ' segundos da analise matricial ')

agora1 = time.time()
portico.OtimizarColunas()
portico.InerciaVigasELS()
portico.OtimizarVigasComInerciaELS()
print(round(time.time()-agora1, 2), ' segundos da iteração  0 ','pesof = ', portico.SetarPeso())

# agora1 = time.time()
# portico.PegarColunasELU_ELS()
# portico.PegarVigasELU_ELS()
# print(round(time.time()-agora1, 2), ' segundos da iteração  0 ','pesof = ', portico.SetarPeso())

peso_f = portico.SetarPeso()
peso_i = 1
iterr = 0
iterr +=1
while ((peso_f != peso_i) and iterr < 20): ##iterr < 9:# (peso_f != peso_i): ##
    peso_i = peso_f

    portico.AnaliseMatricial()
    agora1 = time.time()

    portico.OtimizarColunas()
    portico.OtimizarVigasSemELS1()


    # portico.OtimizarColunasSemELS()
    # portico.OtimizarVigasSemELS()

    # portico.AnaliseMatricial()
    # portico.PegarColunasELU_ELS()
    # portico.PegarVigasELU_ELS()

    # portico.AnaliseMatricial()
    # portico.OtimizarColunasSemELS()
    # portico.OtimizarVigasSemELS()


    print(round(time.time()-agora1, 2), ' segundos da iteracao ', iterr,'pesof = ', round(portico.SetarPeso(),2),' kg')
    iterr += 1
    peso_f = portico.SetarPeso()


final = time.time()
portico.AnaliseMatricial()
for viga in portico.lista_barras:
    print(viga.id, viga.tipo, viga.section_inicio, viga.section_final)
    els = viga.verificar_els()
    if els > 1:
        flecha_maxima = max(viga.deformacao_els_inicio_y, viga.deformacao_els_final_y)
        # print(viga.id, viga.section_inicio, viga.section_final)

minutos = round((final-agora0)/60,0)

segundos = final - agora0 - minutos*60

# print(round(time.time()-agora0, 2), ' segundos total de verificação')
print( minutos, ' minutos ',segundos, ' segundos total de verificação')
print('peso do portico sem acessorios ', round(portico.SetarPeso(), 2))
