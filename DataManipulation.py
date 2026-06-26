import ezdxf
import pandas as pd
import os
import numpy as np
import sys


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
#layer = int(input("Enter layer number: "))
#cassnum = int(input("Enter cassette number: "))
layer = int(sys.argv[1])
cassnum = int(sys.argv[2])
print(type(layer))

############Initial setup to open files and create ezdxf objects#############
doc = ezdxf.new("R2010", True)
msp = doc.modelspace()
shapes_layer = doc.layers.new("SHAPES")
style = doc.styles.add("BoldStyle", font="arial.ttf")
style.dxf.width = 1.5 


# Changed delim_whitespace=True to sep='\s+' to resolve the FutureWarning
df = pd.read_csv('geometry_sipmontile_v16.6.hgcal.txt', sep='\s+')

# Wrapped both conditions in parentheses inside the main brackets
df = df[(df.plane == layer)& (df.icassette == cassnum)]

#Define important columns
col = [
    'plane','u','v','itype','typecode',
    'x0','y0','irot','nvertices', 'vx_0','vy_0','vx_1','vy_1','vx_2','vy_2',
    'vx_3','vy_3','vx_4','vy_4','vx_5','vy_5','vx_6','vy_6','isEngine','icassette',
    'MB', 'wagon'
]
cass = df[col]
print("Cassestte dataframe:")
print(cass)

############Drawing the objects############
print("Drawing modules...")


###################################################
#           Draw modules one by one               #
###################################################

train_num = 0
MB_num  = 0
module_num = 0
# .iterrows() lets you step through the DataFrame one row at a time
for index, row in cass.iterrows():
    
    #Checking for train and location in train
    if row.MB > MB_num:
        train_num += 1
        MB_num = row.MB
        module_num = 0
    else:
        module_num += 1
    # Check how many vertices this specific module has
    num_vertices = int(row['nvertices']) 
    
    # This list will hold the (x, y) tuples for the current module
    module_coords = []
    
    #Angle of rotation
    theta = -(np.radians(30 * (row['icassette'] - 1)))

    #rotation matrix calculation
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
    
    #Draws a circle on the right edge of modules with engine
    #if row.isEngine == True:
    #    draw_solid_dot(msp, (module_coords[2][0],module_coords[2][1]+10), 10, 1)
    ########################
    #       Add color      #
    ########################

    #Setting color
    if train_num == 1:
        color = 30
    elif train_num == 2:
        color = 40
    elif train_num == 3:
        color = 86
    elif train_num == 4:
        color = 122
    elif train_num == 5:
        color = 152
    elif train_num == 6:
        color = 202
    else:
        color = 232

    # 1. Initialize the hatch
    hatch = msp.add_hatch()

    # 2. Set the ACI color directly on the hatch entity 
    hatch.dxf.color = color
    hatch.set_solid_fill(color=color)

    # 3. Ensure coordinates are clean, native Python floats (tuples of x, y)
    clean_coords = [(float(x), float(y)) for x, y in module_coords]

    # 4. Add the closed polyline path to the hatch
    hatch.paths.add_polyline_path(clean_coords, is_closed=True)

    # 5. Draw the boundary line explicitly, and match its color so it looks seamless
    boundary = msp.add_lwpolyline(clean_coords, close=True)
    boundary.dxf.color = 250

    #for i in range (0,len(module_coords)):
    #    msp.add_line(module_coords[i],module_coords[i-1],dxfattribs= {"layer":"SHAPES"})
     
    ########################
    #       Add text       #
    ########################
    
    center_x = sum(v[0] for v in module_coords) / num_vertices #Calculate center in x
    center_y = sum(v[1] for v in module_coords) / num_vertices #Calculate center in y

    module_text = f"IsEngine: {row.isEngine}\n MB: {row.MB}\n wagon: {row.wagon}" #Text to be printed

    #Printing of the text
    msp.add_mtext(  #mtext allows for multi-line text to be printed
    module_text, 
    dxfattribs={
        "color": 0,
        "char_height": 10,  # Use char_height for MTEXT instead of height
    }
).set_location(
    insert=(center_x, center_y),                         # The coordinate point
    attachment_point=5  # The MTEXT equivalent of CENTER
)


casstxt = "Cassette_"+str(layer)+"_"+str(cassnum)
msp.add_mtext(  #mtext allows for multi-line text to be printed
casstxt, 
dxfattribs={
    "color": 8,
    "style": "BoldStyle",
    "char_height": 65,  # Use char_height for MTEXT instead of height
    }
).set_location(
    insert=(450, 700),                         # The coordinate point
    attachment_point=5  # The MTEXT equivalent of CENTER
)
    

############Saving objects to file#############
filename = "Cassette_"+str(layer)+"_"+str(cassnum)+".dxf"
output_folder = "TestDXFfiles"
file_path = os.path.join(output_folder, filename)
doc.saveas(file_path)
print("Saving to "+file_path) 
