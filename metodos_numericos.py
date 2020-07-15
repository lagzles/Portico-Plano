import numpy as np

def newton(f, fl, x):
    if fl(x) == 0.0:
        xnew = x
        return xnew
    
    for i in range(1,101):
        xnew = x - f(x) / fl(x)
        if abs(xnew - x) < 0.00000001:
            break
   
    return xnew    


def x_do_momento_maximo(Barra):
    # ELU = Estado Limite Ultimo
    # momento_elu = Momento de ELU no inicio da barra
    # cortante_elu = Cortante de ELU no inicio da barra
    # carregamento_elu = Carregamento de ELU da barra
    momento_elu = Barra.elu_msdi
    cortante_elu = Barra.elu_vsdi
    carregamento_elu = Barra.carregamento_elu
    comprimento = Barra.comprimento()

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

    momento = 0

    print('newto(0)', newton(df, ddf, 0))
    print('newto(comprimento)', newton(df, ddf, comprimento))

# print('momento maximo = ',momento)
# print('raiz', newton2(df, ddf, 0,0.01,20000))
# print('###########')
# print('f(0)', f(0))
# print('f(6.25)', f(6.25))

# print('###########')
# print('df(0)', df(0))
# print('df(6.25)', df(6.25))

# print('###########')
# print('ddf(0)', ddf(0))
# print('ddf(6.25)', ddf(6.25))
# print()
# teste = 0
# print('Grau do polinomio %d' % n)
# for i in range(len(x)):
#     print('f(%d)'%i,round(f(i),0), y[i], i)
#     print('f\'(%d)'%i,round(df(i),0), i)

            
