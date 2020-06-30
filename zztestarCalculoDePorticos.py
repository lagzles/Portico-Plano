from Portico import Portico

print('\n hhh'*4)
print('começando rotina teste')

vaos = [25,25,25,30]
pd = 10
cumeeira = 50
inc = 3
influencia = 10.000

portico = Portico(vaos, pd, cumeeira, inc, influencia)

carregamentos = []
carr1 = ['cp', 10, 0]
carr2 = ['cv 0', -10, +10]

carregamentos.append(carr1)
carregamentos.append(carr2)
carregamentos.append(carr3)

portico.SetarCarregamentos(carregamentos)
portico.AnaliseMatricial()

portico.GerarDesenhoDXF()























# testando exercicio da internet



# import numpy as np
# print('#'*200)
# fo = np.zeros((3))

# fo[0] = 90
# fo[1] = -30
# fo[2] = 2667

# k = np.matrix(([
#     [30,0,-6000,-30,0,-6000,0,0,0],
#     [0,3000,0,0,-3000,0,0,0,0],
#     [-6000,0,1600000,6000,0,800000,0,0,0],
#     [-30,0,6000,2697,0,6000,-2667,0,0],
#     [0,-3000,0,0,3018,5333,0,-18,5333],
#     [-6000,0,800000,6000,5333,3733333,0,-5333,1066667],
#     [0,0,0,-2667,0,0,2667,0,0],
#     [0,0,0,0,-18,-5333,0,18,-5333],
#     [0,0,0,0,5333,1066667,0,-5333,2133333],
#     ]))

# ap = [0,1,2,6,7,8]
# ap1 = [0,1,2]
# liv = [3,4,5]

# ka = np.delete(np.delete(k, ap, axis=0 ), ap, axis=1)
# kb = np.delete(np.delete(k, liv, axis=0), ap, axis=1)

# kb1 = np.delete(np.delete(k, ap1, axis=0), ap1, axis=1)

# k_inv = np.linalg.inv(ka)

# detk = np.linalg.det(k)
# detka = np.linalg.det(ka)

# print(detk, detka)


# ua = np.dot(k_inv, fo)
# print(ua.shape)
# print(kb.shape)
# print(ka.shape)
# print(k.shape)
# ua1 = np.zeros((6))
# # print(ua)
# # print(ua[0][0])

# for uuu in ua:
#     print(uuu)


# for l in liv:
#     ua1[l] = ua[0][liv.index(l)]

# fb1 = np.dot(kb1, ua1)
# # fb = np.dot(kb, ua)
# # print(ua)
# print(fb1)
