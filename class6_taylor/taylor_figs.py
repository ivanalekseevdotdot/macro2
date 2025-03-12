import pandas as pd
import matplotlib.pyplot as plt  
from matplotlib.lines import Line2D
import numpy as np
import os
desktop = os.path.join(os.path.expanduser("~"), "Desktop")

# a. import
df = pd.read_excel('/Users/ivanalekseev/Desktop/dk_taylor_data.xlsx', 
                   header=None, 
                   skiprows=lambda x: x<3 or x>126, 
                   names =['A', 'B', 'C', 'D', 'F'])

# b. vars
date = df['A']
gdp = df['B']
output_gap = df['C']
pi = df['D']
i_actual = df['F']

# c. taylor rule
def taylor(h, b, pi_star, r_bar):
    i_taylor = r_bar + pi + h*(pi-pi_star)+ b*output_gap
    return i_taylor

# d. first calib 
i_taylor_1 = taylor(h=0.5, b=0.5, pi_star = 2, r_bar = 2)

# e. plot 1
fig, ax = plt.subplots(figsize=(7,4.5))
actual_i = ax.plot(date, i_actual, color='royalblue', label=r'Actual $i$')
taylor_baseline_h1=ax.plot(date, i_taylor_1, color='darkred', label=r'Taylor rule $i$')
ax.set_xlabel('Date', fontsize=12)
ax.legend()
ax.grid(True, linestyle=':', alpha=0.7)
plt.savefig("class6_taylor/a_baseline.pdf")

# f. sensitivity to h new plot
for line in taylor_baseline_h1:
    line.remove()
grid = np.linspace(0, 1, 100)

h_fans = []
for h in grid:
    i_taylor_h = taylor(h=h, b=0.5, pi_star = 2, r_bar = 2)
    lines = ax.plot(date, i_taylor_h, color='lightcoral', alpha=0.5)
    h_fans.extend(lines)
taylor_baseline_h2 = ax.plot(date, i_taylor_1, color='darkred', label=r'Taylor rule $i$')
plt.savefig("class6_taylor/b_change_h.pdf")

# g. sensetivity to b new plot
for line in h_fans:
    line.remove()

b_fans = []
for b in grid:
    i_taylor_b = taylor(h=0.5, b=b, pi_star = 2, r_bar = 2)
    lines = ax.plot(date, i_taylor_b, color='salmon', alpha=0.5)
    b_fans.extend(lines)
ax.plot(date, i_taylor_1, color='darkred', label=r'Taylor rule $i$')
plt.savefig("class6_taylor/c_change_b.pdf")

# h. new rbar
for line in taylor_baseline_h2:
    line.remove()
    
for line in b_fans:
    line.remove()
    
start_date = pd.Timestamp('1994-01-01')
df['quarters_since_1994Q1'] = ((df['A'].dt.year - start_date.year) * 4 +
                               (df['A'].dt.quarter - 1))
                               
def r_bar_function(q):
    if q <= 100:
        return 4.0 - 0.0625 * q
    else:
        return -2.25

df['r_bar_new'] = df['quarters_since_1994Q1'].apply(r_bar_function)
new_r_bar = df['r_bar_new']
i_taylor_new_r = taylor(h=0.5, b=0.5, pi_star = 2, r_bar = new_r_bar)
ax.plot(date, i_taylor_new_r, color='orange', label=r'Taylor rule $i$ (new $\bar{r}$)')
ax.legend()
plt.savefig("class6_taylor/d_change_rbar.pdf")