import numpy as np
import matplotlib.pyplot as plt

alpha = 0.9
gamma = 2.0

# regime 1 for t = 0,1
y_bar1 = 5.0      
pi_star = 4.0  # the inflation target remains unchanged

# regime 2 for t = 2
y_bar2 = 4.0      

# a permanent supply shock hits at t = 1
s0 = 0.0      
s1 = 2.0      
s2 = s1       

# ad function
def AD_func(y, y_bar, pi_star, z=0.0):
    return pi_star - (1/alpha)*(y - y_bar) + z/alpha

# equilibrium solver
def solve_equilibrium(pi_e_current, s, y_bar, pi_star):
    denom = gamma + 1/alpha
    num = pi_star - pi_e_current - s
    y = y_bar + num/denom
    pi = pi_star - (1/alpha)*(y - y_bar)
    return y, pi

# short-run as function
def AS_func(y, y_bar, pi_e_prev, s):
    return pi_e_prev + gamma*(y - y_bar) + s

# solve equilibrium for t = 0, 1, 2
y0, pi0 = solve_equilibrium(pi_e_current=pi_star, s=s0, y_bar=y_bar1, pi_star=pi_star)
y1, pi1 = solve_equilibrium(pi_e_current=pi0, s=s1, y_bar=y_bar1, pi_star=pi_star)
y2, pi2 = solve_equilibrium(pi_e_current=pi1, s=s2, y_bar=y_bar2, pi_star=pi_star)

# define grid for plotting curves
y_grid = np.linspace(0, 10, 200)

# set up a colormap
cmap = plt.get_cmap("tab10")

plt.figure(figsize=(10,7))

# plot ad curves
AD_regime1 = [AD_func(y, y_bar1, pi_star) for y in y_grid]
plt.plot(y_grid, AD_regime1, '-', color=cmap(0), linewidth=2, label=r'$AD_{0}=AD_{1}$')
AD_regime2 = [AD_func(y, y_bar2, pi_star) for y in y_grid]
plt.plot(y_grid, AD_regime2, '-', color=cmap(1), linewidth=2, label=r'$AD_{2}$')
AS0 = [AS_func(y, y_bar1, pi_star, s0) for y in y_grid]
AS1 = [AS_func(y, y_bar1, pi0, s1) for y in y_grid]
AS2 = [AS_func(y, y_bar1, pi_star, s2) + (pi1 - pi_star) for y in y_grid]

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

# plot each unique as curve with unique color
plt.axhline(y=pi_star, color='gray', linestyle='--', label=r'$\pi^\star$')
for idx, (grp, curve) in enumerate(groups):
    if len(grp) > 1:
        label = r'$AS_{' + '='.join(str(t) for t in grp) + '}$'
    else:
        label = r'$AS_{' + str(grp[0]) + '}$'
    plt.plot(y_grid, curve, '-', color=cmap(2+idx), linewidth=2, label=label)

# plot lras lines
plt.axvline(x=y_bar1, color='black', linestyle='-', linewidth=1.5, label=r'$LRAS$')
plt.axvline(x=y_bar2, color='gray', linestyle='-', linewidth=1.5, label=r'$LRAS^\prime$')

# mark equilibrium points (without legend)
plt.plot(y0, pi0, 'ko', markersize=8, label='_nolegend_')
plt.plot(y1, pi1, 'ko', markersize=8, label='_nolegend_')

# compute the intersection of ad2 and as2 for period 2 and plot it
denom = gamma + 1/alpha
y_intersect = (pi_star - pi1 - s2 + gamma*y_bar1 + (1/alpha)*y_bar2) / denom
pi_intersect = pi_star - (1/alpha) * (y_intersect - y_bar2)
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