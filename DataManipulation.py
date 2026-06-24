import ezdxf
import pandas as pd
import os

# Changed delim_whitespace=True to sep='\s+' to resolve the FutureWarning
df = pd.read_csv('geometry_sipmontile_v16.6.hgcal.txt', sep='\s+')

# Wrapped both conditions in parentheses inside the main brackets
df = df[(df.plane == 33) & (df.icassette == 2)]

col = [
    'plane',
    'u',
    'v',
    'itype',
    #'typecode',
    'x0',
    'y0',
    'irot',
    'nvertices',
    'vx_0','vy_0','vx_1','vy_1','vx_2','vy_2','vx_3','vy_3','vx_4','vy_4','vx_5','vy_5','vx_6','vy_6',
    'isEngine'
]



#points = df[['x0','x1','x2','x3','x4','x5','x6']]
points = df[col]
print(points)