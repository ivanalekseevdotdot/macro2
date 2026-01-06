import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from scipy.optimize import fsolve

# 1. calibration
# 1a. parameters
s= 0.0
z= 0.0
gamma = 1.0
y_bar = 5.0-s/gamma
beta1 = 0.5

# 2. curves & grid
# 2a. grid

y_grid = np.linspace(3.0, 7.0, 50)

def er(y):
    return (y-y_bar-z)/beta1

# 3. plot
plt.figure(figsize=(8,6))
demand =  er(y_grid)

plt.axvline(x=y_bar, color='black', linestyle='-', label=r'$LRAS$')
plt.axhline(y=0, color='gray', linestyle='--', label=r'$e^r=0$')
plt.plot(y_grid, demand, color='orange', label=r'$LRAD$')
plt.plot(y_bar, 0, 'ko')

plt.xlabel("$y$")
plt.ylabel(r"$e^r$")
plt.xlim([4,7])
plt.ylim([-4.0,4.0])
plt.grid(True, linestyle=':', alpha=0.7)
plt.legend(loc="lower right")
plt.tight_layout()
plt.savefig("class11_open_economy/a_longrun1.pdf")

z = 0.0
s= -1.0
demand = er(y_grid)
#plt.plot(y_grid, demand, color='red', label=r'$LRAD\prime$')
y_bar_new = 5.0-s/gamma
to_solve = lambda er_new: er(y_bar_new) - er_new
er_new = fsolve(to_solve, x0=0.0)[0]
plt.axhline(y=er_new, color='darkgray', linestyle='--', label=r'New eq. $e^r$')

plt.axvline(x=y_bar_new, color='grey', linestyle='-', label=r'$New LRAS$')
plt.plot(y_bar_new, er_new, 'ko')
plt.legend(loc="lower right")
plt.savefig("class11_open_economy/a_longrun2.pdf")






