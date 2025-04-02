import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# 1. calibration
# 1a. parameters
alpha = 0.9      
gamma = 2.0      
y_bar = 5.0      
pi_star = 4.0    
T = 20
T_fig = 3          

# 1b. shocks
z = np.zeros(T+1)
s = np.zeros(T+1)
z[1] = -1.0  # change shock here
z[2] = -1.0

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

# 2b. plot impulse responses with x-axis ticks spaced by 5
plt.subplot(1,2,1)
plt.plot(time, pi_vals, marker='', color='navy')
plt.title("$\\pi$")
plt.grid(True, linestyle=':', alpha=0.7)
plt.xlabel("$t$")
ax1 = plt.gca()
ax1.xaxis.set_major_locator(ticker.MultipleLocator(5))  # ticks every 5

plt.subplot(1,2,2)
plt.plot(time, y_vals, marker='', color='darkorange')
plt.title("$y$")
plt.grid(True, linestyle=':', alpha=0.7)
plt.xlabel("$t$")
ax2 = plt.gca()
ax2.xaxis.set_major_locator(ticker.MultipleLocator(5))  # ticks every 5

plt.tight_layout()

plt.savefig("as_ad/baseline_impulse.pdf")

# 3. as ad diagram
# 3a. number of periods to illustrate (set T to T_fig)
T = T_fig 
z_vals = z  
s_vals = s  

# 3b. solve model
pi_e = pi_star  # expectations anchored at target
y_eqs, pi_eqs = [], []  # arrays for equilibrium solutions

def solve_equilibrium(pi_e_current, z_t, s_t):
    # equilibrium solver:
    denom = gamma + 1/alpha
    num = pi_star + z_t/alpha - pi_e_current - s_t
    y = y_bar + num / denom
    pi = pi_star - (1/alpha)*(y - y_bar) + z_t/alpha
    return y, pi

for t in range(T+1):
    y_t, pi_t = solve_equilibrium(pi_e, z_vals[t], s_vals[t])
    y_eqs.append(y_t)
    pi_eqs.append(pi_t)
    pi_e = pi_t

# 3c. define grid for curves
y_grid = np.linspace(0, 30, 200)

# 3d. plot AD/AS diagram
plt.figure(figsize=(8,6))

tol = 1e-6

# ------ Group AD curves by identical z shocks ------
ad_groups = {}
for t in range(T+1):
    key = np.round(z_vals[t] / tol) * tol  
    ad_groups.setdefault(key, []).append(t)
ad_group_keys = sorted(ad_groups.keys())
num_ad = len(ad_group_keys)

# ------ Group AS curves by their intercept (since slope=gamma constant) ------
# AS_t(y) = (pi_eqs[t-1] if t>0 else pi_star) + gamma*(y - y_bar) + s_vals[t]
# Its intercept is: (pi_eqs[t-1] if t>0 else pi_star) - gamma*y_bar + s_vals[t]
as_groups = {}
for t in range(T+1):
    base = (pi_eqs[t-1] if t > 0 else pi_star) - gamma*y_bar + s_vals[t]
    key = np.round(base / tol)*tol  
    as_groups.setdefault(key, []).append(t)
as_group_keys = sorted(as_groups.keys())
num_as_groups = len(as_group_keys)

# Total unique curves
total_curves = num_ad + num_as_groups

# Create a colormap with unique color for each curve.
cmap = plt.get_cmap('tab10', total_curves)

plt.axvline(x=y_bar, color='black', linestyle='-', label=r'$LRAS$')
plt.axhline(y=pi_star, color='gray', linestyle='--', label='$\\pi^\\star$')

# Plot each unique AD curve (one line per group) with a unique color.
for i, key in enumerate(ad_group_keys):
    group = ad_groups[key]
    rep = group[0]  # representative period for this group
    if len(group) == 1:
         label = f"$AD_{rep}$"
    else:
         label = " = ".join([f"$AD_{t}$" for t in group])
    ad_vals = [pi_star - (1/alpha)*(y - y_bar) + z_vals[rep]/alpha for y in y_grid]
    plt.plot(y_grid, ad_vals, color=cmap(i), linestyle='-', label=label)

# Plot each unique AS curve (one line per group) with a unique color.
for j, key in enumerate(as_group_keys):
    group = as_groups[key]
    rep = group[0]  # representative period for this AS group
    if len(group) == 1:
         label = f"$AS_{rep}$"
    else:
         label = " = ".join([f"$AS_{t}$" for t in group])
    # Define the AS function using representative period rep.
    def AS_t(y, rep=rep):
        pi_e_rep = pi_eqs[rep-1] if rep > 0 else pi_star
        return pi_e_rep + gamma*(y - y_bar) + s_vals[rep]
    as_vals = [AS_t(y) for y in y_grid]
    color = cmap(num_ad + j)
    plt.plot(y_grid, as_vals, color=color, linestyle='-', label=label)
    # Plot equilibrium point(s) for each period in the group.
    for t in group:
        plt.plot(y_eqs[t], pi_eqs[t], 'ko')

plt.xlabel("$y$")
plt.ylabel("$\\pi$")
plt.xlim([4,6])
plt.ylim([2,5])
plt.grid(True, linestyle=':', alpha=0.7)
plt.legend(loc="lower right")
plt.tight_layout()

plt.savefig("as_ad/baseline_diag.pdf")