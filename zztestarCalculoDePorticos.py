from Portico import Portico


vaos = [7]
pd = 5
cumeeira = 3.5
inc = 3
influencia = 10.000

portico = Portico(vaos, pd, cumeeira, inc, influencia)

carregamentos = []
carr1 = ['ultimo', 10]
# carr2 = ['ultimo', -10]
carregamentos.append(carr1)
# carregamentos.append( carr2)

portico.SetarCarregamentos(carregamentos)
portico.MontarMatrizRigidez()
portico.AnaliseMatricial()
