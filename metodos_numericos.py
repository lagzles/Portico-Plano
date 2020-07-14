import numpy as np


def newton2(f,Df,x0,epsilon,max_iter):
    '''Approximate solution of f(x)=0 by Newton's method.

    Parameters
    ----------
    f : function
        Function for which we are searching for a solution f(x)=0.
    Df : function
        Derivative of f(x).
    x0 : number
        Initial guess for a solution f(x)=0.
    epsilon : number
        Stopping criteria is abs(f(x)) < epsilon.
    max_iter : integer
        Maximum number of iterations of Newton's method.

    Returns
    -------
    xn : number
        Implement Newton's method: compute the linear approximation
        of f(x) at xn and find x intercept by the formula
            x = xn - f(xn)/Df(xn)
        Continue until abs(f(xn)) < epsilon and return xn.
        If Df(xn) == 0, return None. If the number of iterations
        exceeds max_iter, then return None.

    '''
    xn = x0
    for n in range(0,max_iter):
        fxn = f(xn)
        if abs(fxn) < epsilon:
##            print('Found solution after',n,'iterations.')
            return xn
        Dfxn = Df(xn)
        if Dfxn == 0:
            print('Zero derivative. No solution found.')
            return None
        xn = xn - fxn/Dfxn
    print('Exceeded maximum iterations. No solution found.')
    return None



x = np.arange(3)
y = np.array([ 14234.301, 20337.367, 30300.0], float)

# def achar_momento_maximo(y, dx):

# for n in range(1,14):
n = 2
x = np.array([0, 8.33, 16.66], float)
m = len(x)
# Grau do polinomio
#n = 7
carregamento = - 772.5
A = np.zeros((n+1, n+1))
B = np.zeros(n+1)
a = np.zeros(n+1)

for row in range(n+1):
    for col in range(n+1):
        if row == 0 and col == 0:
            A[row, col] = m
            continue
        A[row,col] = np.sum(x**(row+col))
    B[row] = np.sum(x**row * y)


a = np.linalg.solve(A, B)

# Função usando os coeficientes encontrados
# usando o metodo 'Curve Fitting'
def f(x):
    y = a[0]
    for i in range(1, n+1):
        y += a[i] * x ** i
    return y

def df(x):
    y = a[0] * 0
    for i in range(1, n+1):
        y += a[i] *i* x ** (i-1)
    return y

def ddf(x):
    y = carregamento
    # for i in range(2, n+1):
    #     y += a[i] * x ** (i-1) / i
    return y




momento = 0

for dx in range(0,int(833.0), 10):
    # dx = ((dx / 100.0)/8.33)
    dx = ((dx / 100.0))
    momento = max(momento, abs(f(dx)))
    print(f(dx), dx)
    # print('raiz', newton2(df, ddf, dx,0.01,200))

print('momento maximo = ',momento)
print('raiz', newton2(df, ddf, 0,0.01,200))

print()
teste = 0
print('Grau do polinomio %d' % n)
for i in range(len(x)):
    print('f(%d)'%i,round(f(i),0), y[i], i)
    print('f\'(%d)'%i,round(df(i),0), i)

            
