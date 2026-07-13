import ezdxf
import pandas as pd
import os
import numpy as np

###########Functions used in the Trainbased_ModMapBuilder.py script###########

def find_traintext_loc(layer, cassnum, row, train_df, isHD, isScint):
    """
    Determines the location of the label for each train based on various properties
    Inputs:
        layer: layer on which the cassette is found
        cassnum: identifies the cassette in the layer
        row: the row corresponding to one module in the train
        train_df: the dataframe for the train
        isHD: a list of which trains are High density
        isScint: a list of which trains are Scintillators
    Returns:
        t_label_coords: a tuple with the coordinates where the label should go
    """
    if layer <= 33: #if silicon  
        if row.MB in isHD: #if HD
            temp_coords = min(train_df['Mod_center'], key=lambda item: item[0])
            if cassnum % 2 == 1: #if A or C cassette
                t_label_coords = (temp_coords[0] - 125, temp_coords[1] + 125)
            else: # if B or D cassette
                t_label_coords = (temp_coords[0] - 150, temp_coords[1] - 50)
        else: #if LD
            temp_coords = max(train_df['Mod_center'], key=lambda item: item[0])
            t_label_coords = (temp_coords[0] + 150, temp_coords[1] + 30)
    else: #if mixed
        if row.MB in isScint: #if scint
            temp_coords = max(train_df['Mod_center'], key=lambda item: item[0])
            t_label_coords = (temp_coords[0] + 250, temp_coords[1])
        else: #if LD
            temp_coords = min(train_df['Mod_center'], key=lambda item: item[0])
            if cassnum % 2 == 1: #if A or C cassette
                t_label_coords = (temp_coords[0] - 150, temp_coords[1])
            else: # if B or D cassette
                t_label_coords = (temp_coords[0] - 150, temp_coords[1] - 40)
    return t_label_coords

#######################################################################################

def find_engine(row, cassnum, module_coords, engine_locations, isScint, isHD):
    """Finds where to draw an engine, placing it on the line between 
    HD and LD or between East and West
    INPUTS:
        row: row number you are currently on
        cassnum: casset number (1-4)
        module_cords: a list of tuples, where the module vertices are
        engine_locations: a list of tuples, a way to save these locations
        isScint: a boolean list defining if the module is a scintillator
        isHD: a boolean list defining if the module is HD
    """
    if (row.MB in isScint):
        x = (module_coords[0][0]+module_coords[1][0])/2
        y = (module_coords[0][1]+module_coords[1][1])/2
        point = (x,y)
        engine_locations.append(tuple(point))
    ############################################################################
    elif(cassnum % 2 == 1):
        far_right_vertices = sorted(module_coords, key=lambda p: p[0], reverse=True)[:2]
        bottom_right = far_right_vertices[0]                     
        top_right = far_right_vertices[1]                         
        x = ((bottom_right[0])+(top_right[0]))/2.0
        y = ((bottom_right[1])+(top_right[1]))/2.0
        point = (x,y)
        engine_locations.append(tuple(point))
    ############################################################################
    elif(cassnum == 2):
        if (row.MB in isHD):
            x = (module_coords[3][0]+module_coords[2][0])/2
            y = (module_coords[3][1]+module_coords[2][1])/2
            point = (x,y)
            engine_locations.append(tuple(point))
        else:
            bottom_two_vertices = sorted(module_coords, key=lambda p: p[1])[:2]
            bottom_left = min(bottom_two_vertices, key=lambda p: p[0])
            far_left = min(module_coords, key=lambda p: (p[0]))
            x = ((bottom_left[0])+(far_left[0]))/2.0
            y = ((bottom_left[1])+(far_left[1]))/2.0
            point = (x,y)
            engine_locations.append(tuple(point))
    ############################################################################        
    elif(cassnum == 4):
        if (row.MB in isHD):                 #or (row.MB in isScint):
            x = (module_coords[4][0]+module_coords[3][0])/2
            y = (module_coords[4][1]+module_coords[3][1])/2
            point = (x,y)
            engine_locations.append(tuple(point))
        else:
            bottom_two_vertices = sorted(module_coords, key=lambda p: p[1])[:2]
            bottom_left = min(bottom_two_vertices, key=lambda p: p[0])
            far_left = min(module_coords, key=lambda p: (p[0]))
            x = ((bottom_left[0])+(far_left[0]))/2.0
            y = ((bottom_left[1])+(far_left[1]))/2.0
            point = (x,y)
            engine_locations.append(tuple(point))
    return(engine_locations)

#############################################################################################

def draw_solid_dot(msp, location, radius=1.0, color=244):
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
    msp.add_circle(center=location, radius=radius, dxfattribs={"color": color, "layer": "ENGINES"})

#############################################################################################################

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
