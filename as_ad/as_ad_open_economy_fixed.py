import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# 1. calibration
# 1a. parameters
alpha = 0.9      
gamma = 2.0      
y_bar = 5.0      

T_sim = 20
T_fig = 2
beta1 = 0.5 # new parameter for open economy

# pi^f level + optional time shock
pi_f0 = 4.0
pi_f_shock = np.zeros(T_sim+1)       
pi_f_shock[1] = 1.5
pi_f_path = pi_f0 + pi_f_shock        # time path for pi^f

# 1b. shocks
z = np.zeros(T_sim+1)
s = np.zeros(T_sim+1)
z[1] = -0.5

# 1c. store paths
pi_vals  = np.zeros(T_sim+1)
y_vals   = np.zeros(T_sim+1)
e_r_vals = np.zeros(T_sim+1)

# 1d. start at steady state
e_r_vals[0] = 0.0
pi_vals[0]  = pi_f_path[0]
y_vals[0]   = y_bar

# 2. impulse responses
# 2a. simulate
for t in range(1, T_sim+1):
    common      = e_r_vals[t-1] + z[t] - s[t]
    denominator = (1 + beta1*gamma)
    y_vals[t]   = y_bar + (beta1 * common) / denominator
    pi_vals[t]  = pi_f_path[t] + s[t] + (gamma * beta1 * common) / denominator
    e_r_vals[t] = e_r_vals[t-1] + pi_f_path[t] - pi_vals[t]

time = np.arange(T_sim+1)

plt.figure(figsize=(10,5))

# 2b. plot impulse responses with x-axis ticks spaced by 5
plt.subplot(1,2,1)
plt.plot(time, pi_vals, color='navy')
plt.title(r"$\pi$")
plt.grid(True, linestyle=':', alpha=0.7)
plt.xlabel("$t$")
ax1 = plt.gca()
ax1.xaxis.set_major_locator(ticker.MultipleLocator(5))

plt.subplot(1,2,2)
plt.plot(time, y_vals, color='darkorange')
plt.title("$y$")
plt.grid(True, linestyle=':', alpha=0.7)
plt.xlabel("$t$")
ax2 = plt.gca()
ax2.xaxis.set_major_locator(ticker.MultipleLocator(5))

plt.tight_layout()
plt.savefig("as_ad/baseline_impulse_open_economy_fixed.pdf")


# 3. AS-AD diagram
# 3a. number of periods to illustrate
T_plot = T_fig
z_vals = z[:T_plot+1]
s_vals = s[:T_plot+1]

# pi^f time path for the plotted scenario
pi_f_vals = pi_f_path[:T_plot+1]

# 3b. solve model for equilibrium each period
y_eqs, pi_eqs, e_r_eqs = [], [], []

e_r_last = 0.0

def solve_equilibrium(z_t, s_t, pi_f_t):
    common      = e_r_last + z_t - s_t
    denominator = (1 + beta1*gamma)
    y           = y_bar + (beta1 * common) / denominator
    pi          = pi_f_t + s_t + (gamma * beta1 * common) / denominator
    e_r         = e_r_last + pi_f_t - pi
    return y, pi, e_r

for t in range(T_plot+1):
    y_t, pi_t, e_r_t = solve_equilibrium(z_vals[t], s_vals[t], pi_f_vals[t])
    e_r_last = e_r_t
    y_eqs.append(y_t)
    pi_eqs.append(pi_t)
    e_r_eqs.append(e_r_t)

# 3c. define grid for curves
y_grid = np.linspace(0, 30, 200)

# 3d. plot AS/AD diagram
plt.figure(figsize=(8,6))

tol = 1e-6

# group AD curves by identical intercepts
ad_groups = {}
for t in range(T_plot+1):
    e_r_lag = 0.0 if t == 0 else e_r_eqs[t-1]
    intercept = e_r_lag + pi_f_vals[t] + z_vals[t]
    key = np.round(intercept / tol) * tol
    ad_groups.setdefault(key, []).append(t)
ad_keys = sorted(ad_groups.keys())
num_ad = len(ad_keys)

# group AS curves by identical intercepts
as_groups = {}
for t in range(T_plot+1):
    # AS uses pi_f_t in this model
    base = pi_f_vals[t] - gamma*y_bar + s_vals[t]
    key  = np.round(base / tol) * tol
    as_groups.setdefault(key, []).append(t)
as_keys = sorted(as_groups.keys())
num_as = len(as_keys)

total_curves = num_ad + num_as
cmap = plt.get_cmap('tab10', total_curves)

# plot long‐run supply and target inflation
plt.axvline(x=y_bar, color='black', linestyle='-', label=r'$LRAS$')
plt.axhline(y=pi_f_vals[0], color='dimgray', linestyle='--', linewidth=2, label=r'$\pi^f_0$')
if T_plot >= 1:
    plt.axhline(y=pi_f_vals[1], color='dimgray', linestyle='--', linewidth=2, label=r'$\pi^f_1$')

# plot AD schedules
for i, key in enumerate(ad_keys):
    group = ad_groups[key]
    rep   = group[0]
    label = f"$AD_{rep}$" if len(group)==1 else " = ".join(f"$AD_{t}$" for t in group)
    e_r_lag = 0.0 if rep == 0 else e_r_eqs[rep-1]
    ad_vals = e_r_lag + pi_f_vals[rep] - (1/beta1)*(y_grid - y_bar) + z_vals[rep]
    plt.plot(y_grid, ad_vals, color=cmap(i), linestyle='-', label=label)

# plot AS schedules and equilibrium points + dashed lines to LRAS
for j, key in enumerate(as_keys):
    group = as_groups[key]
    rep   = group[0]
    label = f"$AS_{rep}$" if len(group)==1 else " = ".join(f"$AS_{t}$" for t in group)
    
    # AS function (pi_f can move over time)
    pi_e_rep = pi_f_vals[rep]
    def AS_t(y, pi_e_rep=pi_e_rep, s_t=s_vals[rep]):
        return pi_e_rep + gamma*(y - y_bar) + s_t
    as_vals = [AS_t(y) for y in y_grid]
    plt.plot(y_grid, as_vals, color=cmap(num_ad+j), linestyle='-', label=label)

    # equilibrium and dashed connector to LRAS
    for t in group:
        y_star   = y_eqs[t]
        pi_star_t= pi_eqs[t]
        plt.plot(y_star, pi_star_t, 'ko')
        if t < T_plot:
            plt.plot([y_star, y_star], [pi_star_t, pi_f_vals[t]],
                 linestyle='--', color='dimgray', zorder=0)

plt.xlabel("$y$")
plt.ylabel(r"$\pi$")
plt.xlim([4.5,5.5])
plt.ylim([3,6])
plt.grid(True, linestyle=':', alpha=0.7)
plt.legend(loc="lower right")
plt.tight_layout()
plt.savefig("as_ad/baseline_diag_open_economy_fixed.pdf")