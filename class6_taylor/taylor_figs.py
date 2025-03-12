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
print(df.head(10))
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
taylor_baseline_h=ax.plot(date, i_taylor_1, color='darkred', label=r'Taylor rule $i$')
ax.set_xlabel('Date', fontsize=12)
ax.legend()
ax.grid(True, linestyle=':', alpha=0.7)

# f. sensitivity to h new plot
grid = np.linspace(0, 1, 100)

for h in grid:
    i_taylor_h = taylor(h=h, b=0.5, pi_star = 2, r_bar = 2)
    h_fans = ax.plot(date, i_taylor_h, color='lightcoral', alpha=0.5)
taylor_baseline_h = ax.plot(date, i_taylor_1, color='darkred', label=r'Taylor rule $i$')

# g. sensetivity to b new plot
for line in h_fans:
    line.remove()

for b in grid:
    i_taylor_b = taylor(h=0.5, b=b, pi_star = 2, r_bar = 2)
    b_fans = ax.plot(date, i_taylor_b, color='salmon', alpha=0.5)
ax.plot(date, i_taylor_1, color='darkred', label=r'Taylor rule $i$')

# h. new rbar
taylor_baseline_h.remove()

for line in h_fans:
    line.remove()
    
for line in b_fans:
    line.remove()
    


plt.show()