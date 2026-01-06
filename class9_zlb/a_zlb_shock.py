import numpy as np
import matplotlib.pyplot as plt

# 1. calibration
gamma = 2.0
y_bar = 5.0
pi_star = 4.0
s = np.zeros(4)
s[1] = 0.5  # positive supply shock in period 1

# 2. define ad and as curves
def AD_curve(y, alpha):
    return pi_star - (1/alpha)*(y - y_bar)

def AS_curve(y, pi_e, s_val):
    return pi_e + gamma*(y - y_bar) + s_val

# 3. parameter values for alpha
alphas = [0.5, 0.9, 1.5]  # Three different values for alpha

# 4. create the plot
plt.figure(figsize=(10, 6))

# define y grid
y_grid = np.linspace(0, 10, 200)

# add vertical and horizontal lines
plt.axvline(x=y_bar, color='gray', linestyle='--', label="$y_{bar}$")
plt.axhline(y=pi_star, color='gray', linestyle=':', label="$\pi^*$")

# plot ad curves (same for all periods)
colors = ['red', 'green', 'blue']
for i, alpha in enumerate(alphas):
    ad_curve = [AD_curve(y, alpha) for y in y_grid]
    plt.plot(y_grid, ad_curve, label=f"AD ($\\alpha$={alpha})", color=colors[i])

# plot as curves for each period
pi_e = pi_star  # Expected inflation
# as curve before the shock (period 0)
as_curve_0 = [AS_curve(y, pi_e, s[0]) for y in y_grid]
plt.plot(y_grid, as_curve_0, label=f"AS0", color='purple', linestyle='--')

# as curve after the shock (period 1)
as_curve_1 = [AS_curve(y, pi_e, s[1]) for y in y_grid]
plt.plot(y_grid, as_curve_1, label=f"AS1", color='orange', linestyle='-')

# find and plot intersections
for i, alpha in enumerate(alphas):
    ad_curve = [AD_curve(y, alpha) for y in y_grid]

    # intersection with as0
    y_intersect_index_0 = np.argmin(abs(np.array(ad_curve) - np.array(as_curve_0)))
    y_intersect_0 = y_grid[y_intersect_index_0]
    pi_intersect_0 = ad_curve[y_intersect_index_0]
    plt.plot(y_intersect_0, pi_intersect_0, marker='o', color='black', markersize=5)

    # intersection with as1
    y_intersect_index_1 = np.argmin(abs(np.array(ad_curve) - np.array(as_curve_1)))
    y_intersect_1 = y_grid[y_intersect_index_1]
    pi_intersect_1 = ad_curve[y_intersect_index_1]
    plt.plot(y_intersect_1, pi_intersect_1, marker='o', color='black', markersize=5)

# 5. customize the plot
plt.xlabel("y")
plt.ylabel("$\\pi$")
plt.title("AS-AD Diagram with Different Alphas and Positive Supply Shock")
plt.xlim(4, 7)
plt.ylim(2, 6)
plt.grid(True)
plt.legend()
plt.tight_layout()

# 6. save the plot
plt.savefig("as_ad/as_ad_alphas_supply_shock.pdf")