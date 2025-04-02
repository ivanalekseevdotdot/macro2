import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# 1. calibration
# 1a. parameters
alpha = 0.9      
gamma = 2.0      
y_bar = 10.0      
pi_star = 4.0    
T = 20
T_fig = 2  
pi_e_t_vals = [(2.0), (4.0) ,(6.0)]
s_vals = [-2.0, 0.0, 2.0]
z_vals = [-2.0, 0.0, 2.0]

# 2. define as 
def AS_t(pi_e_t,s,y):
        return pi_e_t + gamma*(y - y_bar) + s     
    
# 3. draw
# 3a. different inf exp
y_grid = np.linspace(5, 15, 200)
fig, ax = plt.subplots(figsize=(7,5.5))
colors_pi_e = ['tab:blue', 'tab:orange', 'tab:green']
for color, pi_e in zip(colors_pi_e, pi_e_t_vals):
    as_vals = [AS_t(pi_e, 0, y) for y in y_grid] 
    plt.plot(y_grid, as_vals, color=color, label=f'$\pi^e$ = {pi_e}')
ax.grid(True, which='major', linestyle=':', color='gray', alpha=0.7)
plt.axhline(y=pi_star, color='gray', linestyle='--', label=f'$\pi^\star$= {pi_star}')
plt.axvline(x=y_bar, color='black', linestyle='-', label='LRAS')
plt.xlim(6, 14)
plt.ylim(0, 10)
plt.xlabel("y")
plt.ylabel("$\pi$")
plt.legend()
plt.savefig("class8_asad/a_inf_exp.pdf", bbox_inches='tight')

# 3b. different s
y_grid = np.linspace(5, 15, 200)
fig, ax = plt.subplots(figsize=(7,5.5))
colors_s = ['tab:red', 'tab:purple', 'tab:brown']
for color, s in zip(colors_s, s_vals):
    as_vals = [AS_t(pi_star, s, y) for y in y_grid] 
    plt.plot(y_grid, as_vals, color=color, label=f'$s$ = {s}')
ax.grid(True, which='major', linestyle=':', color='gray', alpha=0.7)
plt.axhline(y=pi_star, color='gray', linestyle='--', label=f'$\pi^\star$= {pi_star}')
plt.axvline(x=y_bar, color='black', linestyle='-', label='LRAS')
plt.xlim(6, 14)
plt.ylim(0, 10)
plt.xlabel("y")
plt.ylabel("$\pi$")
plt.legend()
plt.savefig("class8_asad/b_sup_shock.pdf", bbox_inches='tight')

# 4. define ad
def AD_t(y,z):
        return pi_star - (1/alpha)*(y - y_bar) + z/alpha
    
# 5. draw
# 5a. different z
y_grid = np.linspace(5, 15, 200)
fig, ax = plt.subplots(figsize=(7,5.5))
colors_z = ['tab:cyan', 'tab:olive', 'tab:pink']
for color, z in zip(colors_z, z_vals):
    ad_vals = [AD_t(y,z) for y in y_grid] 
    plt.plot(y_grid, ad_vals, color=color, label=f'$z$ = {z}')
ax.grid(True, which='major', linestyle=':', color='gray', alpha=0.7)
plt.axhline(y=pi_star, color='gray', linestyle='--', label=f'$\pi^\star$= {pi_star}')
plt.axvline(x=y_bar, color='black', linestyle='-', label='LRAS')
plt.xlim(6, 14)
plt.ylim(0, 10)
plt.xlabel("y")
plt.ylabel("$\pi$")
plt.legend()
plt.savefig("class8_asad/c_dem_shock.pdf", bbox_inches='tight')

# 6. perm demand shock
z_vals = [0, -1]
y_grid = np.linspace(5, 15, 200)
fig, ax = plt.subplots(figsize=(7,5.5))
colors_z = ['tab:cyan', 'tab:olive', 'tab:pink']
for color, z in zip(colors_z, z_vals):
    ad_vals = [AD_t(y,z) for y in y_grid] 
    plt.plot(y_grid, ad_vals, color=color, label=f'$AD_{-1*z}$')
plt.axhline(y=pi_star, color='gray', linestyle='--', label=f'$\pi^\star$= {pi_star}')
plt.axvline(x=y_bar, color='black', linestyle='-', label='LRAS')
for color, z in zip(colors_z, z_vals):   
    plt.plot(y_bar, AD_t(y_bar, z), 'ko')
ax.grid(True, which='major', linestyle=':', color='gray', alpha=0.7)

plt.xlim(6, 14)
plt.ylim(0, 10)
plt.xlabel("y")
plt.ylabel("$\pi$")
plt.legend()
plt.savefig("class8_asad/d_perm_dem.pdf", bbox_inches='tight')


