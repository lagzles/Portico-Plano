##import numpy as np
from numpy import array, zeros
from numpy.linalg import inv

# [a][x] = [b]

##a = array([[2, 7,-1, 3, 1],
##           [2, 3, 4, 1, 7],
##           [6, 2,-3, 2,-1],
##           [2, 1, 2,-1, 2],
##           [3, 4, 1,-2, 1]], float)

a = array([[0, 7,-1, 3, 1],
           [2, 3, 4, 1, 7],
           [6, 2, 0, 2,-1],
           [2, 1, 2, 0, 2],
           [3, 4, 1,-2, 1]], float)



b = array([5, 7, 2, 3, 4], float)

# [x] = [a]**-1 . [b]
inv_a = inv(a)

##print(inv_a.dot(b))

n = len(b)
x = zeros(n,float)

#Elimination

for k in range(n-1):
    if a[k,k] == 0:
        for j in range(n):
            a[k,j],a[k+1,j] = a[k+1,j],a[k,j]
        b[k], b[k+1] = b[k+1], b[k]
    for i in range(k+1, n):
        if a[i,k] == 0: continue
            
        fctr = a[k, k] / a[i, k]
        b[i] = b[k] - fctr * b[i]   
        for j in range(k, n):
            a[i,j] = a[k,j] - fctr * a[i,j]

#back substitution
x[n-1] = b[n-1] / a[n-1, n-1]
for i in range(n-2, -1, -1):
    s = 0
    for j in range(i+1, n):
        s += a[i,j]*x[j] 
    x[i] = (b[i] - s) / a[i,i]
        

print(a)
print(b)
print(x)

