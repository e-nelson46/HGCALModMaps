import ezdxf
import pandas as pd
import os
import numpy as np

#############Defining functions to draw the shapes#############

def draw_solid_dot(msp, location, radius=1.0, color=1):
    """
    Draws a solid, filled circular dot at a specified location.

    :param msp: The ezdxf modelspace object.
    :param location: A tuple (x, y) for the center of the dot.
    :param radius: The size/radius of the dot.
    :param color: AutoCAD Color Index (default 1 = Red).
    """
    # 1. Create a blank hatch
    hatch = msp.add_hatch()

    # 2. Explicitly force the SOLID FILL to the desired color index
    hatch.set_solid_fill(color=color)

    # 3. Add the circular boundary path to the hatch
    path = hatch.paths.add_edge_path()
    path.add_arc(center=location, radius=radius)

    # 4. Add the outer circle line matching the color
    msp.add_circle(center=location, radius=radius, dxfattribs={"color": color})


############Inputs for Cassette and Layer Number###############
layer = int(input("Enter layer number: "))
cassnum = int(input("Enter cassette number: "))


############Initial setup to open files and create ezdxf objects#############
doc = ezdxf.new("R2010", True)
msp = doc.modelspace()
shapes_layer = doc.layers.new("SHAPES")

# Changed delim_whitespace=True to sep='\s+' to resolve the FutureWarning
df = pd.read_csv('geometry_sipmontile_v16.6.hgcal.txt', sep='\s+')

# Wrapped both conditions in parentheses inside the main brackets
df = df[(df.plane == layer)& (df.icassette == cassnum)]

col = [
    'plane','u','v','itype','typecode',
    'x0','y0','irot','nvertices', 'vx_0','vy_0','vx_1','vy_1','vx_2','vy_2',
    'vx_3','vy_3','vx_4','vy_4','vx_5','vy_5','vx_6','vy_6','isEngine','icassette'
]
cass = df[col]
print("Cassestte dataframe:")
print(cass)

############Drawing the objects############
print("Drawing modules...")

# .iterrows() lets you step through the DataFrame one row at a time
for index, row in cass.iterrows():
    
    # Check how many vertices this specific module has
    num_vertices = int(row['nvertices']) 
    
    # This list will hold the (x, y) tuples for the current module
    module_coords = []
    
    theta = -(np.radians(30 * (row['icassette'] - 1)))

    c, s = np.cos(theta), np.sin(theta)
    R = np.array([
        [c, -s],
        [s,  c]
    ])

    # Loop from 0 up to the number of vertices (e.g., 0 to 5 for a hexagon)
    for i in range(num_vertices):
        
        # Use an f-string to dynamically grab vx_0, vx_1, etc.
        # We wrap it in int() to ensure they are integers as requested
        x = int(row[f'vx_{i}'])
        y = int(row[f'vy_{i}'])

        vector = np.array([[x], [y]])        
        rotated_coordinates = R @ vector
        x_rot = float(rotated_coordinates[0][0])
        y_rot = float(rotated_coordinates[1][0])

        # Add the (x, y) pair to the list
        module_coords.append((x_rot,y_rot))

    #could probably try printing right here, and then we will not have to save each
    #individual list in the all_modules_polygons master list...
    for i in range (0,len(module_coords)):
        msp.add_line(module_coords[i],module_coords[i-1],dxfattribs= {"layer":"SHAPES"})    


############Saving objects to file#############
filename = "Cassette_"+str(layer)+"_"+str(cassnum)+".dxf"
output_folder = "TestDXFfiles"
file_path = os.path.join(output_folder, filename)
doc.saveas(file_path)
print("Saving to "+file_path) 
