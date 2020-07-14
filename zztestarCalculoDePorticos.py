from Portico import Portico

print('\n hhh'*4)
print('começando rotina teste')

# valores em cm
vaos = [25, 25]
pd = 10
cumeeira = 25
inc = 3
influencia = 10.000
duas_aguas = True

portico = Portico(vaos, pd, cumeeira, inc, influencia)

cp = 15 # kgf/m²
sc = 25 # kgf/m²
su = 15 # kgf/m²
cv = 80 # kgf/m²

cpL = cp * influencia 
scL = sc * influencia
suL = su * influencia
cvL = cv * influencia * 0


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
portico.AnaliseMatricial()

portico.GerarDesenhoDXF()

# for barra in portico.lista_barras:
#     if barra.tipo == 'viga':
#         barra.set_combinacoes_esforcos()
#         barra.verificar()
#         print('barra id, momento inicio, ratio Mi, ratio Vi')
#         print(barra.id,barra.elu_msdi, barra.ratio_mi, barra.ratio_vi)
#         print()


barra = portico.lista_barras[0]
barra.set_combinacoes_esforcos()
barra.verificar()
print()
print(barra.sectionInicio)
print('barra id, momento inicio, MRd, ratio Mi')
print(barra.id,barra.elu_msdi, barra.ratio_mi)
print('barra id, momento Final, ratio Mf, ratio Vf')
print(barra.id,barra.elu_msdf, barra.ratio_mf, barra.ratio_vf)

barra = portico.lista_barras[2]
barra.set_combinacoes_esforcos()
barra.verificar()
print()
print(barra.sectionInicio)
print('barra id, momento inicio, MRd, ratio Mi')
print(barra.id,barra.elu_msdi, barra.ratio_mi)
print('barra id, momento Final, ratio Mf, ratio Vf')
print(barra.id,barra.elu_msdf, barra.ratio_mf, barra.ratio_vf)

