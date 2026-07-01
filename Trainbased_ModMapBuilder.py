# Most current builder
# Builds the map train by train to achieve correct labeling
# To use run: python ./Trainbased_ModMapBuilder "Layer number" "Cassette number"

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

def find_module_vertices(row):
    """
    Calculates the rotated coordinates and center of a module

    :param row: The corresponding module's dataframe row

    :return module_coords: A list of tuples which are the coordinates for each vertex
    "return center_coords: A tuple which conatins the coordinates of the center of the shape
    """
    # Check how many vertices this specific module has
    num_vertices = int(row["nvertices"]) 
    
    # This list will hold the (x, y) tuples for the current module
    module_coords = []
    
    #Angle of rotation
    theta = -(np.radians(30 * (row["icassette"] - 1)))

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


    center_x = sum(v[0] for v in module_coords) / num_vertices #Calculate center in x
    center_y = sum(v[1] for v in module_coords) / num_vertices #Calculate center in y

    center_coords = (center_x, center_y)

    return module_coords, center_coords

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

#Define important columns and building cassette dataframe
col = [
    'plane','u','v','itype','typecode',
    'x0','y0','irot','nvertices', 'vx_0','vy_0','vx_1','vy_1','vx_2','vy_2',
    'vx_3','vy_3','vx_4','vy_4','vx_5','vy_5','vx_6','vy_6','isEngine','icassette',
    'MB', 'wagon'
]
cass_df = df[col]


isHD = []  #List of MB values for HD trains
isScint = []  #List of MB values for Scintillators
train_labels_LD = []
train_labels_HD = []
train_id = cass_df['MB'].unique().tolist() #List of unique MB values

#Determining order of the train labeling
for train in train_id:
    train_df = cass_df[(cass_df.MB == train)] 
    
    if train_df.wagon.nunique() == 1:   #If all wagon values are the same, classify as HD or Scint
        if train < 40:
            isHD.append(train)
        else:
            isScint.append(train)

    if train in isHD:
        y0_max = train_df['vy_3'].max()
        train_labels_HD.append((train, y0_max))
    elif train not in isScint:
        y0_max = train_df['vy_3'].max()
        train_labels_LD.append((train, y0_max))

train_labels_LD.sort(key=lambda x: x[1], reverse=True)
train_labels_HD.sort(key=lambda x: x[1], reverse=True)

train_labels = {}
for i in range(len(train_labels_LD)):
    train_labels[str(train_labels_LD[i][0])] = "LD" + str(i+1)
for i in range(len(train_labels_HD)):
    train_labels[str(train_labels_HD[i][0])] = "HD" + str(i+1)


#Defining variables used for coloring and labeling
train_num = 0



for train in train_id:
    #Reseting variables
    West_num = 1
    East_num = 1
    HD_num = 1

    train_df = cass_df[(cass_df.MB == train)] #making df for the train
    #print(f"Train {train} dataframe:")
    #print(train_df)
        

    if train in isHD: #If train is high density, only loop through wagon = 0 when drawing dataframe
        wagon_loop = 1
    else:
        wagon_loop = 2

    engine_df = train_df[train_df.isEngine == True] #Making dataframe for the engine and the engine center
    engine_center = find_module_vertices(engine_df.squeeze())[1]

    #Getting data for additional colmuns containing the module center and distance from engine
    Mod_Dist_Data = []
    Mod_Center_data = []
    for index, row in train_df.iterrows():
        mod_center = find_module_vertices(row)[1]
        Mod_Center_data.append(mod_center)
        distance = np.linalg.norm(np.array(engine_center) - np.array(mod_center))
        Mod_Dist_Data.append(distance)
    
    #Adding new columns for distance from engine "Eng_dist" and module center "Mod_center"
    train_df["Eng_Dist"] = Mod_Dist_Data
    train_df["Mod_center"] = Mod_Center_data

    #Changing number to determine color (should be named color_num, but too lazy to change)
    train_num += 1

    #Narrowing down train dataframe further
    for wagon in range(wagon_loop):
        sub_train_df = train_df[train_df.wagon == wagon]  #Making East/West specific dataframe
        sub_train_df = sub_train_df.sort_values("Eng_Dist")
        #print(f"East/West Frame:\n {sub_train_df}")

        #Drawing the module and inputing text
        for index, row in sub_train_df.iterrows():
            #Setting color
            if train_num == 1:
                color = 32
            elif train_num == 2:
                color = 42
            elif train_num == 3:
                color = 82
            elif train_num == 4:
                color = 122
            elif train_num == 5:
                color = 152
            elif train_num == 6:
                color = 202
            elif train_num == 7:
                color = 232
            elif train_num == 8:
                color = 242
            else:
                color = 62
            
            #Getting vertex coordinates and drawing shape
            module_coords = find_module_vertices(row)[0]

    # 1. Initialize the hatch
            hatch = msp.add_hatch()

    # 2. Set the ACI color directly on the hatch entity 
            hatch.dxf.color = color
            hatch.set_solid_fill(color=color)

    # 3. Add the closed polyline path to the hatch
            hatch.paths.add_polyline_path(module_coords, is_closed=True)

    # 4. Draw the boundary line explicitly, and match its color so it looks seamless
            boundary = msp.add_lwpolyline(module_coords, close=True)
            boundary.dxf.color = 250

    #Determining the text for each module
            if row.MB in isHD:
                wagon_text = train_labels[str(row.MB)] + "_M" + str(HD_num)
                HD_num += 1
            elif row.MB in isScint:
                wagon_text = "Scintillator"
            elif row.wagon == 1:
                wagon_text = train_labels[str(row.MB)] + "_E" + str(East_num)
                East_num += 1
            else:
                wagon_text = train_labels[str(row.MB)] + "_W" + str(West_num)
                West_num += 1

            module_text = f"IsEngine: {row.isEngine}\n {wagon_text}\n (u, v): ({row.u}, {row.v})" #Text to be printed

            #Printing of the text
            msp.add_mtext(  #mtext allows for multi-line text to be printed
            module_text, 
            dxfattribs={
                "color": 0,
                "style": "BoldStyle",
                "char_height": 10,  # Use char_height for MTEXT instead of height
            }
        ).set_location(
            insert=row.Mod_center,                         # The coordinate point
            attachment_point=5  # The MTEXT equivalent of CENTER
        )

############Adding Cassette Label#############
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
