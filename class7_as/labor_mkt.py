import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

sigma = 2.0
alpha = 0.3
Y = 30.0
P = 1.0
n = 10.0
B = 1.0
eta = 0.7
b = 0.02

w_grid = np.linspace(0.0001, 100, 10000)

def labor_demand(w):
    inner_exponent = 1 / (1/sigma + 1/(1 - alpha) - 1)
    numerator = ((sigma - 1) / sigma) * (1 - alpha) * (Y/n)**(1/sigma) * B**(1/(1 - sigma))
    inner = (numerator / w)**(inner_exponent) * B**(-1)
    return inner**(1/(1 - alpha))

def wage(P_e):
    inner3 = sigma/(1+alpha*(sigma-1))
    w_prime = b*(eta*inner3/(eta*inner3-1))
    w_actual = w_prime*P_e/P
    return w_prime, w_actual

demand_curve = labor_demand(w_grid)
w_prime, w_actual = wage(1.25)

fig, ax = plt.subplots(figsize=(5.5,4))
ax.plot(demand_curve, w_grid, color='orange', label=r'$L_i$')
ax.plot([0, max(demand_curve)], [w_prime, w_prime], linestyle='-', color='blue', label=r'$w_i^\prime$')
ax.plot(labor_demand(w_prime), w_prime, 'o', color='grey', markersize=5, label='Eq.')
ax.grid(True, which='major', linestyle=':', color='gray', alpha=0.7) #grid
plt.xlim(0, 10)
plt.ylim(0, 1)
plt.xlabel(r'$L_i$', fontsize=12)
plt.ylabel(r'$w_i$', fontsize=12)
plt.legend()
plt.tight_layout()
plt.savefig("class7_as/a_correct_exp.pdf", bbox_inches='tight')
plt.close()

fig, ax = plt.subplots(figsize=(5.5,4))
ax.plot(demand_curve, w_grid, color='orange', label=r'$L_i$')
ax.plot([0, max(demand_curve)], [w_prime, w_prime], linestyle='-', color='blue', label=r'$w_i^\prime$')
ax.plot([0, max(demand_curve)], [w_actual, w_actual], linestyle='-', color='maroon', label=r'$w_i$')
ax.plot(labor_demand(w_actual), w_actual, 'o', color='grey', markersize=5, label='Eq.')
ax.grid(True, which='major', linestyle=':', color='gray', alpha=0.7) #grid
plt.xlim(0, 10)
plt.ylim(0, 1)
plt.xlabel(r'$L_i$', fontsize=12)
plt.ylabel(r'$w_i$', fontsize=12)
plt.legend()
plt.tight_layout()
plt.savefig("class7_as/b_wrong_exp.pdf", bbox_inches='tight')
plt.close()