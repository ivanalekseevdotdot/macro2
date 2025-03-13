import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# 1. calibration
# 1a. parameters
alpha = 2.0      
gamma = 2.0      
y_bar = 15.0      
pi_star = 10.0    
T = 20
T_fig = 2           

# 1b. shocks
z = np.zeros(T+1)
s = np.zeros(T+1)
z[1] = 10.0  # change shock here

# 1c. store path
pi_vals = np.zeros(T+1)  
y_vals  = np.zeros(T+1)  

# 1d. start at steady state
pi_vals[0] = pi_star   
y_vals[0]  = y_bar     

# 2. impulse responses
# 2a. simulate
for t in range(1, T+1):
    
    numerator = ( pi_vals[t-1] 
                  + gamma*alpha*pi_star 
                  + gamma*z[t] 
                  + s[t] )
    denominator = (1 + gamma*alpha)
    pi_vals[t] = numerator / denominator

    pi_gap = pi_vals[t] - pi_star
    y_vals[t] = y_bar - alpha*pi_gap + z[t]

time = np.arange(T+1)

plt.figure(figsize=(10,5))

# 2b. plot
plt.subplot(1,2,1)
plt.plot(time, pi_vals, marker='o')
plt.title("$\pi$")
plt.grid(True, linestyle=':', alpha=0.7)


plt.subplot(1,2,2)
plt.plot(time, y_vals, marker='o', color='orange')
plt.title("$y$")
plt.grid(True, linestyle=':', alpha=0.7)
plt.tight_layout()

plt.savefig("as_ad/baseline_impulse.pdf")

# 3. as ad diagram
# 3a. number of periods to illustrate
T = T_fig 
z_vals = z  
s_vals = s  

# 3b. solve model
pi_e = pi_star # expectations anchored at target

y_eqs, pi_eqs = [], [] # array for solutions

def solve_equilibrium(pi_e_current, z_t, s_t): # equilibirium solver
    denom = gamma + 1/alpha
    num = pi_star + z_t/alpha - pi_e_current - s_t
    y = y_bar + num / denom
    pi = pi_star - (1/alpha)*(y - y_bar) + z_t/alpha
    return y, pi

for t in range(T+1): # find equilibirum
    y_t, pi_t = solve_equilibrium(pi_e, z_vals[t], s_vals[t])
    y_eqs.append(y_t)
    pi_eqs.append(pi_t)
    pi_e = pi_t

# 3c. curves
y_grid = np.linspace(0, 30, 200)

# 3d. plot
plt.figure(figsize=(8,6))

colors = ['orange','green','purple','brown']

for t in range(T+1):
    
    def AD_t(y):
        return pi_star - (1/alpha)*(y - y_bar) + z_vals[t]/alpha
    def AS_t(y):
        pi_e_t = pi_eqs[t-1] if t>0 else pi_star
        return pi_e_t + gamma*(y - y_bar) + s_vals[t]

    ad_vals = [AD_t(y) for y in y_grid]
    as_vals = [AS_t(y) for y in y_grid]

    plt.plot(y_grid, ad_vals, color=colors[t % len(colors)],
             label=f"AD$_{t}$", linestyle='-')
    plt.plot(y_grid, as_vals, color=colors[t % len(colors)],
             label=f"AS$_{t}$", linestyle='-')

    plt.plot(y_eqs[t], pi_eqs[t], 'ko')

plt.axvline(x=y_bar, color='black', linestyle='-', label='LRAS') # plot lras

plt.xlabel("$y$")
plt.ylabel("$\\pi$")
plt.xlim([0,30])
plt.ylim([0,30])
plt.grid(True,  linestyle=':', alpha=0.7)
plt.legend(loc="upper right")
plt.tight_layout()

plt.savefig("as_ad/baseline_diag.pdf")