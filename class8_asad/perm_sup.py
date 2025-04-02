# ATTENTION: CODE IS WRONG, I WILL FIX IT LATER

import numpy as np
import matplotlib.pyplot as plt

alpha = 0.9
gamma = 2.0

# Regime 1: t = 0,1
y_bar1 = 5.0      
pi_star = 4.0  # The inflation target remains unchanged

# Regime 2: t = 2
y_bar2 = 4.0      

# --- Shock: A permanent supply shock hits at t = 1 ---
s0 = 0.0      # t = 0: No shock
s1 = 2.0      # t = 1: Shock occurs (and is permanent)
s2 = s1       # t = 2: Shock persists

# --- AD Function ---
# (AD is independent of the supply shock.)
def AD_func(y, y_bar, pi_star, z=0.0):
    return pi_star - (1/alpha)*(y - y_bar) + z/alpha

# --- Equilibrium Solver ---
#   y = y_bar + (π★ - π_e - s) / (γ + 1/α)
#   π = π★ - (1/α)(y - y_bar)
def solve_equilibrium(pi_e_current, s, y_bar, pi_star):
    denom = gamma + 1/alpha
    num = pi_star - pi_e_current - s
    y = y_bar + num/denom
    pi = pi_star - (1/alpha)*(y - y_bar)
    return y, pi

# --- Short-run AS Function ---
# AS is given by:
#    AS(y) = πₑ^(prev) + γ*(y - y_bar) + s
# For t=0 we take πₑ^(prev) = π★.
def AS_func(y, y_bar, pi_e_prev, s):
    return pi_e_prev + gamma*(y - y_bar) + s

# --- Simulate Equilibrium for t = 0, 1, 2 ---
# t = 0: initial steady state (using regime 1)
y0, pi0 = solve_equilibrium(pi_e_current=pi_star, s=s0, y_bar=y_bar1, pi_star=pi_star)
# t = 1: Shock hits; AD remains unchanged (regime 1)
y1, pi1 = solve_equilibrium(pi_e_current=pi0, s=s1, y_bar=y_bar1, pi_star=pi_star)
# t = 2: Central Bank adjusts AD so that the new regime uses y_bar2
y2, pi2 = solve_equilibrium(pi_e_current=pi1, s=s2, y_bar=y_bar2, pi_star=pi_star)

# --- Define Grid for Plotting Curves ---
y_grid = np.linspace(0, 10, 200)

# --- Set up a colormap ---
cmap = plt.get_cmap("tab10")

plt.figure(figsize=(10,7))

# --- Plot AD Curves ---
# Regime 1 AD (t = 0,1)
AD_regime1 = [AD_func(y, y_bar1, pi_star) for y in y_grid]
plt.plot(y_grid, AD_regime1, '-', color=cmap(0), linewidth=2, label=r'$AD_{0}=AD_{1}$')
# Regime 2 AD (t = 2)
AD_regime2 = [AD_func(y, y_bar2, pi_star) for y in y_grid]
plt.plot(y_grid, AD_regime2, '-', color=cmap(1), linewidth=2, label=r'$AD_{2}$')

# --- Compute Short-run AS Curves for each period ---
AS0 = [AS_func(y, y_bar1, pi_star, s0) for y in y_grid]
AS1 = [AS_func(y, y_bar1, pi0, s1) for y in y_grid]
# For period 2 use π★ as the base and then shift by (pi1 - pi_star)
AS2 = [AS_func(y, y_bar1, pi_star, s2) + (pi1 - pi_star) for y in y_grid]

# --- Group AS Curves if they are identical (within tolerance) ---
AS_curves = [AS0, AS1, AS2]
periods = [0, 1, 2]
tol_val = 1e-3
groups = []
visited = set()
for i in range(len(AS_curves)):
    if i in visited:
        continue
    group = [periods[i]]
    for j in range(i+1, len(AS_curves)):
        if np.allclose(AS_curves[i], AS_curves[j], atol=tol_val):
            group.append(periods[j])
            visited.add(j)
    visited.add(i)
    groups.append((group, AS_curves[i]))

# --- Plot each unique AS curve with unique color ---
plt.axhline(y=pi_star, color='gray', linestyle='--', label=r'$\pi^\star$')
for idx, (grp, curve) in enumerate(groups):
    if len(grp) > 1:
        label = r'$AS_{' + '='.join(str(t) for t in grp) + '}$'
    else:
        label = r'$AS_{' + str(grp[0]) + '}$'
    plt.plot(y_grid, curve, '-', color=cmap(2+idx), linewidth=2, label=label)

# --- Plot LRAS Lines ---
plt.axvline(x=y_bar1, color='black', linestyle='-', linewidth=1.5, label=r'$LRAS$')
plt.axvline(x=y_bar2, color='gray', linestyle='-', linewidth=1.5, label=r'$LRAS^\prime$')

# --- Mark Equilibrium Points (without legend) ---
plt.plot(y0, pi0, 'ko', markersize=8, label='_nolegend_')
plt.plot(y1, pi1, 'ko', markersize=8, label='_nolegend_')

# Compute the intersection of AD₂ and AS₂ for period 2 and plot it
# Compute the intersection of AD₂ and AS₂ for period 2
denom = gamma + 1/alpha
y_intersect = (pi_star - pi1 - s2 + gamma*y_bar1 + (1/alpha)*y_bar2) / denom
pi_intersect = pi_star - (1/alpha) * (y_intersect - y_bar2)

# Plot the intersection point for period 2 (black dot, no legend)
plt.plot(y_intersect, pi_intersect, 'ko', markersize=8, label='_nolegend_')

plt.xlabel('$y$')
plt.ylabel(r'$\pi$')
plt.xlim([3, 6])
plt.ylim([3, 6])
plt.grid(True, linestyle=':', alpha=0.7)
plt.legend(loc='upper right')
plt.tight_layout()
plt.savefig("class8_asad/e_perm_sup.pdf", bbox_inches="tight")
plt.show()