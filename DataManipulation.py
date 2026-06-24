import ezdxf
import pandas as pd
import os

#Declare some important stuff right away
doc = ezdxf.new("R2010", True)
msp = doc.modelspace()
shapes_layer = doc.layers.new("SHAPES")

# Changed delim_whitespace=True to sep='\s+' to resolve the FutureWarning
df = pd.read_csv('geometry_sipmontile_v16.6.hgcal.txt', sep='\s+')

# Wrapped both conditions in parentheses inside the main brackets
df = df[(df.plane == 33) & (df.icassette == 2)]

col = [
    'plane','u','v','itype',
    #'typecode',
    'x0','y0','irot','nvertices', 'vx_0','vy_0','vx_1','vy_1','vx_2','vy_2',
    'vx_3','vy_3','vx_4','vy_4','vx_5','vy_5','vx_6','vy_6','isEngine'
]
cass = df[col]

# We will store a list of coordinate lists for all modules here
all_modules_polygons = []

# .iterrows() lets you step through the DataFrame one row at a time
for index, row in cass.iterrows():
    
    # Check how many vertices this specific module has
    num_vertices = int(row['nvertices']) 
    
    # This list will hold the (x, y) tuples for the current module
    module_coords = []
    
    # Loop from 0 up to the number of vertices (e.g., 0 to 5 for a hexagon)
    for i in range(num_vertices):
        
        # Use an f-string to dynamically grab vx_0, vx_1, etc.
        # We wrap it in int() to ensure they are integers as requested
        x = int(row[f'vx_{i}'])
        y = int(row[f'vy_{i}'])
        
        # Add the (x, y) pair to the list
        module_coords.append((x, y))

    #could probably try printing right here, and then we will not have to save each
    #individual list in the all_modules_polygons master list...
    for i in range (0,len(module_coords)):
        msp.add_line(module_coords[i],module_coords[i-1],dxfattribs= {"layer":"SHAPES"})
    

    # Add this completed module's coordinates to our master list
    all_modules_polygons.append(module_coords)

#print(all_modules_polygons)
doc.saveas("Test_Cass.dxf")
print("Yep it worked")