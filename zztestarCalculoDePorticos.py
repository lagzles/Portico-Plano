from Portico import Portico

print('\n hhh'*4)
print('começando rotina teste')

# valores em cm
vaos = [25, 25]
pd = 10
cumeeira = 25
inc = 3
influencia = 10.000

portico = Portico(vaos, pd, cumeeira, inc, influencia)

carregamentos = []
# carregamento = [tipo, [vertical agua esquerda, vertical agua direita, horizontal esquerda, horizontal direita]]
carr1 = ['cp',   [-10, -10,   0,  0]]
carr2 = ['cv 0', [ 10,  10, 10, -10]]
carr22 = ['cv 90', [ 10,  10, -10, -10]]

carregamentos.append(carr1)
carregamentos.append(carr2)
carregamentos.append(carr22)

portico.SetarCarregamentos(carregamentos)
portico.AnaliseMatricial()

portico.GerarDesenhoDXF()
