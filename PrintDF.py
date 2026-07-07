import pandas as pd
import sys


layer = int(sys.argv[1])
cassnum = int(sys.argv[2])
df = pd.read_csv('geometry_sipmontile_v16.6.hgcal.txt', sep=r'\s+')

# Wrapped both conditions in parentheses inside the main brackets
df = df[(df.plane == layer)& (df.icassette == cassnum)]

if df.empty == True:
    print(f"Error: Not a valid layer or cassette number")
    sys.exit()


#Define important columns and building cassette dataframe
col = [
    'plane','u','v','itype','typecode',
    'x0','y0','irot','nvertices', 
    #'vx_0','vy_0','vx_1','vy_1','vx_2','vy_2','vx_3','vy_3','vx_4','vy_4','vx_5','vy_5','vx_6','vy_6',
    'isEngine','icassette',
    'MB', 'wagon'
]
cass_df = df[col]

print(cass_df.to_string())