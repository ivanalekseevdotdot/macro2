import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import os
desktop = os.path.join(os.path.expanduser("~"), "Desktop")

# a. parameters
phi = 0.03       
H   = 8.0      
r1   = 0.05      

# b. budget
def budget_line(c1,r):
    return (1 + r) * (H - c1)

# c. utility
def utility(c1, c2):
    return np.log(c1) + (1.0 / (1.0 + phi)) * np.log(c2)

# d. indifference curves
def c2_indiff(c1, Ubar):
    return np.exp((1.0 + phi) * (Ubar - np.log(c1)))

# e. solve for optimal cons
def optimal_consumption():
    c1_star = H * ((1.0 + phi) / (2.0 + phi))
    c2_star = (1.0 + r1) * (H - c1_star)
    return c1_star, c2_star
c1_star, c2_star = optimal_consumption()
U_star = utility(c1_star, c2_star)

# f. prep curves
c1_grid = np.linspace(0.0001, H+4, 200)
c2_line = budget_line(c1_grid, r1)
c2_indiff_star = c2_indiff(c1_grid, U_star)
c2_indiff_alt = c2_indiff(c1_grid, U_star+0.3)

# 1. fig 1 optimal allocation
# 1a. plot
fig, ax = plt.subplots(figsize=(5.5,4))
ax.plot(c1_grid, c2_line, color='grey') # budget
ax.plot(c1_grid, c2_indiff_star, color='orange') # indiff opt
ax.plot(c1_grid, c2_indiff_alt, color='red', linestyle='dotted') # indiff alt
ax.plot(c1_star, c2_star, 'o', color='orange', markersize=6, label='Opt')
ax.grid(True, which='major', linestyle=':', color='gray', alpha=0.7) #grid

# 1b. labels and layout
plt.xlabel(r'$C_1$', fontsize=12)
plt.ylabel(r'$C_2$', fontsize=12)
plt.xlim(0, (1+r1)*H + 0.5)
plt.ylim(0, (1 +r1)*H + 0.5)
ax.xaxis.set_major_locator(ticker.MultipleLocator(base=2))  # x-axis ticks at multiples of 2
ax.yaxis.set_major_locator(ticker.MultipleLocator(base=2))

# 1c. generate & save fig
plt.legend()
plt.tight_layout()
filepath = os.path.join(desktop, "fig1_opt.pdf")
plt.savefig(filepath)
plt.close()

# 2. fig 2 alt y1
# 2a. plot
fig, ax = plt.subplots(figsize=(5.5,4))
c2_indiff_alt = c2_indiff(c1_grid, U_star)
ax.plot(c1_grid, c2_line, color='grey') # budget
ax.plot(c1_grid, c2_indiff_star, color='orange') # indiff opt
ax.plot(c1_star, c2_star, 'o', color='orange', markersize=6, label='Opt')
ax.grid(True, which='major', linestyle=':', color='gray', alpha=0.7) # grid
ax.plot([c1_star, c1_star], [c2_star, 0], linestyle='--', color='orange')
ax.plot([3, 3], [0, budget_line(3, r1)], linestyle='--', color='dimgray', label=r'Borrow ($Y_1^B$)')
ax.plot([5, 5], [0, budget_line(5, r1)], linestyle='--', color='royalblue', label=r'Save ($Y_1^S$)')

# 2b. labels and layout
plt.xlim(0, (1+r1)*H + 0.5)
plt.ylim(0, (1 +r1)*H + 0.5)

# 2c. generate & save fig
plt.legend()
plt.tight_layout()
filepath = os.path.join(desktop, "fig2_alt_y1.pdf")
plt.savefig(filepath)
plt.close()

# 3. fig 3 change in interest rate
# 3a. make second line
r2 = 0.3
c2_line_alt = budget_line(c1_grid, r2)

# 3b. plot
fig, ax = plt.subplots(figsize=(5.5,4))
ax.plot(c1_grid, c2_line_alt, color='navy', label=r'$r=0.3$') # budget alt
ax.plot(c1_grid, c2_line, color='blue', label=r'$r=0.05$') # budget
ax.grid(True, which='major', linestyle=':', color='gray', alpha=0.7) #grid

# 3c. labels and layout
plt.xlim(0, (1+r2)*H + 0.5)
plt.ylim(0, (1 + r2)*H + 0.5)

# 3d. generate & save fig
plt.legend()
plt.tight_layout()
filepath = os.path.join(desktop, "fig3_alt_r.pdf")
plt.savefig(filepath)
plt.close()

# 4. fig 4 budget constrained
# 4a. new grids etc
pre_cons_grid = np.linspace(0.0001, 2, 200)
post_cons_grid = np.linspace(2, H+0.5, 200)
c2_pre = budget_line(pre_cons_grid, r1)
c2_post = budget_line(post_cons_grid, r1)
c2_cons_indiff = c2_indiff(c1_grid, utility(2,(H-2)*(1+r1)))

# 4b. plot
fig, ax = plt.subplots(figsize=(5.5,4))
ax.plot(pre_cons_grid, c2_pre, color='grey') # pre cons
ax.plot(post_cons_grid, c2_post, color='grey', linestyle='--') # post cons
ax.plot(c1_grid, c2_indiff_star, color='orange') # indiff opt
ax.plot(c1_grid, c2_cons_indiff, color='maroon') # cons indiff
ax.plot(2,(H-2)*(1+r1), 'o', color='maroon', markersize=6, label=r'Cons. opt $(C_1=Y_1)$')
ax.plot([2,2], [(H-2)*(1+r1), 0], linestyle='--', color='maroon')
ax.plot(c1_star, c2_star, 'o', color='orange', markersize=6, label=r'Uncons. opt $(C_1=C_1^\star)$')
ax.plot([c1_star, c1_star], [c2_star, 0], linestyle='--', color='orange')
ax.grid(True, which='major', linestyle=':', color='gray', alpha=0.7) #grid

# 4c. labels and layout
plt.xlim(0, (1+r1)*H + 0.5)
plt.ylim(0, (1 +r1)*H + 0.5)

# 4d. generate & save fig
plt.legend()
plt.tight_layout()
filepath = os.path.join(desktop, "fig4_credit_cons.pdf")
plt.savefig(filepath)
plt.close()











