from Portico import Portico


vaos = [20000, 20000, 20000]
pd = 12500
cumeeira = 35000
inc = 3
influencia = 11000

portico = Portico(vaos, pd, cumeeira, inc, influencia)

carregamentos = []
carr1 = ['ultimo', 100]
carr2 = ['ultimo', -100]

carregamentos.append(carr1, carr2)

portico.SetarCarregamentos(carregamentos)
