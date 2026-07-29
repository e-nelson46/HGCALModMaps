# Builds the map train by train to achieve correct labeling
# To use run: python3 Trainbased_ModMapBuilder.py "Layer number" "Cassette number/letter"
# To change output folder, go to the "saving objects to file" section at the very end and change the variable "output_folder"

import ezdxf
import pandas as pd
import os
import numpy as np
import sys
import json
import train_func


############Inputs for Cassette and Layer Number###############

layer = int(sys.argv[1])
cassnum = (sys.argv[2])

#Changing the cassette labels based on the layer
if layer <= 33 and layer % 2 == 1: #Odd numbered layer before 33
    cass_dict = {'A':1, 'B':2, 'C':3, 'D':4}
    cass_label = {1:'A', 2:'B', 3:'C', 4:'D'}
elif layer <= 33 and layer % 2 == 0: #Even numbered layer before 33
    cass_dict = {'A':1, 'B':2, 'C':3, 'D':4}
    cass_label = {1:'A', 2:'B', 3:'C', 4:'D'} 
elif layer > 33 and layer % 2 == 1:  #Odd numbered layer after 33
    cass_dict = {'C':1, 'D':2, 'A':3, 'B':4}
    cass_label = {1:'C', 2:'D', 3:'A', 4:'B'}
else: #Even numbered layer after 33
    cass_dict = {'A':1, 'B':2, 'C':3, 'D':4}
    cass_label = {1:'A', 2:'B', 3:'C', 4:'D'}    

if cassnum in cass_dict:
    cassnum = cass_dict[cassnum]
else:
    cassnum = int(cassnum)

if layer <= 26:
    layer += 26

############Initial setup to open files and create ezdxf objects#############

doc = ezdxf.new("R2010", True)
msp = doc.modelspace()
doc.layers.add(name="SHAPES")
doc.layers.add(name="ENGINES")
doc.layers.add(name="TEXT")
style = doc.styles.add("BoldStyle", font="arial.ttf")
style.dxf.width = 1.5 


# Changed delim_whitespace=True to sep=r'\s+' to resolve the FutureWarning
df = pd.read_csv("Active Geometry SIPM Tile Data 2026.csv")
json_df = pd.read_csv('geometry_simotherboards.hgcal.txt', sep=r'\s+')

# Wrapped both conditions in parentheses inside the main brackets
df = df[(df.plane == layer)& (df.icassette == cassnum)]
json_df = json_df[(json_df.plane == layer)& (json_df.icassette == cassnum)]

if df.empty == True:
    print(f"Error: Not a valid layer or cassette number")
    sys.exit()


#Define important columns and building cassette dataframe
col = [
    'plane','u','v','itype','typecode',
    'x0','y0','irot','nvertices', 'vx_0','vy_0','vx_1','vy_1','vx_2','vy_2',
    'vx_3','vy_3','vx_4','vy_4','vx_5','vy_5','vx_6','vy_6','isEngine','icassette',
    'MB', 'wagon', "trigLinks", 'HDorLD', 'dataLinks_ld', 'dataLinks_hd'
]
cass_df = df[col]
cass_json_df = json_df[col]
print("Creating cassette dataframe...")

#Creating dictionary for a json file
json_info = {f"{layer}{cass_label[cassnum]}":{}}

isHD = []  #List of MB values for HD trains
isScint = []  #List of MB values for Scintillators
train_labels_LD = []
train_labels_HD = []
train_id = cass_df['MB'].unique().tolist() #List of unique MB values


############Train Labeling###############

#Determining order of the train labeling
for train in train_id:
    train_df = cass_df[(cass_df.MB == train)] 
    
    if train_df.wagon.nunique() == 1:   #If all wagon values are the same, classify as HD or Scint
        if train < 40:
            isHD.append(train)
        else:
            isScint.append(train)

    engine_df = train_df[train_df.isEngine == True] #Making dataframe for the engine and the engine center
    engine_center = train_func.find_module_vertices(engine_df.squeeze())[1]

#Getting data for additional colmuns containing the module center and distance from engine
    Mod_Dist_Data = []
    Mod_Center_data = []
    for index, row in train_df.iterrows():
        mod_center = train_func.find_module_vertices(row)[1]
        Mod_Center_data.append(mod_center)
        distance = np.linalg.norm(np.array(engine_center) - np.array(mod_center))
        Mod_Dist_Data.append(distance)
    
    #Adding new columns for module center "Mod_center"
    train_df = train_df.copy()
    train_df["Mod_center"] = Mod_Center_data

    if train in isHD:
        max_coords = max(train_df['Mod_center'], key=lambda item: item[1])
        train_labels_HD.append((train, max_coords[1]))
    elif train not in isScint:
        max_coords = max(train_df['Mod_center'], key=lambda item: item[1])
        train_labels_LD.append((train, max_coords[1]))

train_labels_LD.sort(key=lambda x: x[1], reverse=True)
train_labels_HD.sort(key=lambda x: x[1], reverse=True)

#Creating dictionary for the module labels
train_labels = {}
for i in range(len(train_labels_LD)):
    train_labels[str(train_labels_LD[i][0])] = "LD" + str(i+1)
for i in range(len(train_labels_HD)):
    train_labels[str(train_labels_HD[i][0])] = "HD" + str(i+1)


############Drawing the modules train by train###############

#Defining variables used for coloring and labeling
train_num = 0
Scint_train_num = 3
engine_locations = []

print("Drawing Modules...")
for train in train_id:
    #Reseting variables
    West_num = 1
    East_num = 1
    HD_num = 1
    Scint_num = 1

    train_df = cass_df[(cass_df.MB == train)] #making df for the train
    cass_json_df['MB'] = pd.to_numeric(cass_json_df['MB'], errors='coerce')
    train_json_df = cass_json_df[(cass_json_df.MB == float(train))]

    if train in isHD or train in isScint: #If train is high density or Scint, only loop through wagon = 0 when drawing dataframe
        wagon_loop = 1
    else:
        wagon_loop = 2

    #Defining Scintillator train label dictionaries
    if len(train_df) == 2:
        Scint = {1 : 'K', 2 :'J'}
        Scint_train_label = 'TH'
    else:
        Scint = {1: 'G', 2: 'E', 3: 'D', 4: 'B', 5: 'A'}
        Scint_train_label = 'TL'

    #Adding train labels to json dictionaries
    if train in isScint:
        json_info[f"{layer}{cass_label[cassnum]}"].update({f"{Scint_train_label}{Scint_train_num}":{}})
    else:
        json_info[f"{layer}{cass_label[cassnum]}"].update({f"{train_labels[str(train)]}":{}})

    #Making dataframe for the engine and the engine center
    engine_df = train_df[train_df.isEngine == True]
    engine_json_df = train_json_df[train_json_df.isEngine == "1"]
    engine_json_df = engine_json_df.squeeze()
    #print(engine_json_df)
    engine_center = train_func.find_module_vertices(engine_df.squeeze())[1]
    if train not in isScint:
        u = float(engine_json_df["u"])
        v = float(engine_json_df["v"])
        type = engine_json_df["typecode"]

    wagon_json_df = train_json_df[train_json_df.isEngine == "0"]
    wagon_json_df = wagon_json_df.squeeze()

    #Adding engine and wagon info to json dictionaries
    if train in isHD:
        wagon_type = wagon_json_df["typecode"]
        json_info[f"{layer}{cass_label[cassnum]}"][f"{train_labels[str(train)]}"].update({"engine":{"u":u, 'v':v, 'type':type}, "wagon_type":wagon_type})
    elif train in isScint:
        if train > 37:
            wingboard = 'WM-MBH'
        else:
            wingboard = 'WM-MFH'
        json_info[f"{layer}{cass_label[cassnum]}"][f"{Scint_train_label}{Scint_train_num}"].update({"wingboard":wingboard, "motherboard":'WM-MB0'})
    else:
        if wagon_json_df["typecode"].iloc[0][1] == "W":
            wagon_west = wagon_json_df["typecode"].iloc[0]
            wagon_east = wagon_json_df["typecode"].iloc[1]
        else:
            wagon_east = wagon_json_df["typecode"].iloc[0]
            wagon_west = wagon_json_df["typecode"].iloc[1]                                                        
        json_info[f"{layer}{cass_label[cassnum]}"][f"{train_labels[str(train)]}"].update({"engine":{"u":u, 'v':v, 'type':type}, "wagon_west":wagon_west, "wagon_east":wagon_east})

    #print(json_info)


    #Finding the values for each module's center and distance from the engine
    Mod_Dist_Data = []
    Mod_Center_data = []
    for index, row in train_df.iterrows():
        mod_center = train_func.find_module_vertices(row)[1]
        Mod_Center_data.append(mod_center)
        distance = np.linalg.norm(np.array(engine_center) - np.array(mod_center))
        Mod_Dist_Data.append(distance)
    
    #Adding new columns for distance from engine "Eng_dist" and module center "Mod_center"
    train_df = train_df.copy()
    train_df["Eng_Dist"] = Mod_Dist_Data
    train_df["Mod_center"] = Mod_Center_data

    #Changing number to determine color (should be named color_num, but too lazy to change)
    train_num += 1

    #Narrowing down train dataframe further into wagons
    for wagon in range(wagon_loop):

        sub_train_df = train_df[train_df.wagon == wagon]  #Making East/West specific dataframe
        sub_train_df = sub_train_df.copy()
        #print("East/West Frame: \n" + sub_train_df.to_string())

        ############Sorting the modules in each wagon df###############

        #Sorting the sections of the trains to order out from the engine
        if cassnum % 2 == 1 and row.MB not in isScint:            #odd casset num
            #Get the target y-value from the first row
            y_row = sub_train_df['Mod_center'].iloc[0][1]

            #Calculate the distance for every row and save it as a new column
            sub_train_df['Distance'] = sub_train_df['Mod_center'].apply(
                lambda x: np.linalg.norm(np.array(engine_center) - np.array(x))
            )

            #Create a boolean column: True if the y-coordinate matches y_row, False otherwise
            sub_train_df['Is_Y_Match'] = sub_train_df['Mod_center'].apply(
            lambda x: abs(x[1]-y_row) <= 20 
            )

            #Sort the entire DataFrame
            #'Is_Y_Match' ascending=False means True comes before False (your simple_sort group first)
            #'Distance' ascending=True means smallest distances come first
            sub_train_df = sub_train_df.sort_values(
            by=['Is_Y_Match', 'Distance'], 
            ascending=[False, True]
            )

            #Clean up by dropping the temporary columns
            sub_train_df = sub_train_df.drop(columns=['Is_Y_Match', 'Distance'])
  
        elif cassnum % 2 == 0 and row.MB not in isScint:
            # Get the target x and y values from the first row
            # We need both coordinates to anchor our 60-degree line
            x0, y0 = engine_center[0], engine_center[1]

            # Calculate the distance for every row and save it as a new column
            sub_train_df['Distance'] = sub_train_df['Mod_center'].apply(
                lambda p: np.linalg.norm(np.array(engine_center) - np.array(p))
            )

            # Create a boolean column: True if the point is within a tolerance of 2 from the 30-degree line
            # Tangent of 30 degrees is the slope (m)
            m = np.tan(np.radians(30)) # This equals sqrt(3)
            
            # Using the perpendicular distance formula from a point to a line:
            # d = |m*x - y + y0 - m*x0| / sqrt(m^2 + 1)
            sub_train_df['Is_Angle_Match'] = sub_train_df['Mod_center'].apply(
                lambda p: (abs(m * p[0] - p[1] + y0 - m * x0) / np.sqrt(m**2 + 1)) <= 20
            )

            # Sort the entire DataFrame
            # - 'Is_Angle_Match' ascending=False means True comes before False
            # - 'Distance' ascending=True means smallest distances come first
            sub_train_df = sub_train_df.sort_values(
                by=['Is_Angle_Match', 'Distance'], 
                ascending=[False, True]
            )

            # Clean up by dropping the temporary columns
            sub_train_df = sub_train_df.drop(columns=['Is_Angle_Match', 'Distance'])
        else:
            sub_train_df = sub_train_df.sort_values('Eng_Dist')

        ############Drawing each module###############

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
                color = 222
            elif train_num == 8:
                color = 242
            else:
                color = 62
            
            #Getting vertex coordinates and drawing shape
            module_coords = train_func.find_module_vertices(row)[0]

            #Initialize the hatch to add fill color
            hatch = msp.add_hatch()

            #Set the ACI color directly on the hatch entity 
            hatch.dxf.color = color
            hatch.set_solid_fill(color=color)

            #Add the closed polyline path to the hatch
            hatch.paths.add_polyline_path(module_coords, is_closed=True)
            
            #Draw the boundary line explicitly, and match its color so it looks seamless
            boundary = msp.add_lwpolyline(module_coords, close=True, dxfattribs={"layer": "SHAPES"})
            boundary.dxf.color = 250

            #Adding circle locations for Engines
            if row.isEngine == True:
                engine_location = train_func.find_engine(row, cassnum, module_coords, isScint,isHD)
                if row.MB in isHD:
                    engine_color = 214
                else:
                    engine_color = 246
                engine_info = (engine_location, engine_color)
                engine_locations.append(engine_info)
            
            ############Determining and writing text inside each module###############
            HD_txt_fix = {1:1, 2:2, 3:4, 4:3}

            if row.MB in isHD: #Labeling for HD modules
                module_text ="M" + str(HD_num)
                #Hardcoded name change for a certain type of train
                if layer <= 33 and cassnum % 2 == 1 and train_labels[str(row.MB)] == 'HD2':
                    module_text ="M" + str(HD_txt_fix[HD_num])
                HD_num += 1
            elif row.MB in isScint: #Labeling for Scintillator modules
                module_text = row.typecode[3:5]
                #Fixing typecode identifier
                if module_text[1] == '2':
                    module_text = module_text[0] + '12'
                elif module_text[1] == '1':
                    module_text = module_text[0] + '11'
                elif module_text[1] == '0':
                    module_text = module_text[0] + '10'
            elif row.wagon == 0:  #Labeling for west LD modules
                module_text = "W" + str(West_num)
                West_num += 1
            else: #Labeling for east LD modules
                module_text = "E" + str(East_num)
                East_num += 1

            #Adding module info to dictionary for json file
            if row.HDorLD == 0:
                daqLinks = row.dataLinks_ld
            else:
                daqLinks = row.dataLinks_hd

            module_dict = {'u':row.u, 'v':row.v, 'type':row.typecode, 'i_rot':row.irot, 'trigLinks':row.trigLinks, 'daqLinks':daqLinks}
            if row.MB in isScint:
                json_info[f"{layer}{cass_label[cassnum]}"][f"{Scint_train_label}{Scint_train_num}"].update({module_text:module_dict})
            else:    
                json_info[f"{layer}{cass_label[cassnum]}"][f"{train_labels[str(train)]}"].update({module_text:module_dict})

            module_text += f"\n{{\\H23;({row.u},{row.v})}}" # <--- Change "H23" to change u,v text size

            #Adapts text size based on module types
            num_vertices = int(row["nvertices"])
            if row.MB in isScint:
                text_size = 40
            elif num_vertices == 4:
                text_size = 28
            elif num_vertices == 5:
                text_size = 32
            else:
                text_size = 35


            #Printing the Module text
            msp.add_mtext(  #mtext allows for multi-line text to be printed
            module_text, 
            dxfattribs={
                "color": 250,
                "style": "BoldStyle",
                "char_height": text_size,  # <--- Go to if else above to change text size of module labels
                "layer": "TEXT"
            }
        ).set_location(
            insert=row.Mod_center,                         # The coordinate point
            attachment_point=5  # The MTEXT equivalent of CENTER
        )

        ############Adding labeling to the edges of each train###############

        t_label_coords = train_func.find_traintext_loc(layer, cassnum, row, train_df, isHD, isScint)

        #Adding text for train labels
        if row.MB in isScint:
            train_text = Scint_train_label + str(Scint_train_num)
            Scint_train_num -= 1
        else:
            train_text = train_labels[str(row.MB)]

        msp.add_mtext(  #mtext allows for multi-line text to be printed
            train_text, 
            dxfattribs={
                "color": 0,
                "style": "BoldStyle",
                "char_height": 40,  # <--- Change this to change train label text size
                "layer": "TEXT"
            }
        ).set_location(
            insert=t_label_coords,                         # The coordinate point
            attachment_point=5  # The MTEXT equivalent of CENTER
        )

############Adding Cassette Label#############
casstxt = "Cassette "+str(layer-26)+str(cass_label[cassnum])+"("+str(layer)+str(cass_label[cassnum])+")"
msp.add_mtext(  #mtext allows for multi-line text to be printed
casstxt, 
dxfattribs={
    "color": 8,
    "style": "BoldStyle",
    "char_height": 65,  # <--- Change this to change cassette label text size
    "layer": "TEXT"
    }
).set_location(
    insert=(450, 700),                         # The coordinate point
    attachment_point=5  # The MTEXT equivalent of CENTER
)

############Adding engines from pre-determined locations###############
print("Adding Engines...")
for engine_info in engine_locations:
    train_func.draw_solid_dot(msp, engine_info[0], 15, engine_info[1])

############Saving objects to file#############
#Creating json file
filename = "Cassette_"+str(layer-26)+str(cass_label[cassnum])+"("+str(layer)+str(cass_label[cassnum])+").json"
with open(filename, 'w', encoding='utf-8') as file:
    json.dump(json_info, file, indent=4, ensure_ascii=False)

#Creating dxf file
filename = "Cassette_"+str(layer-26)+str(cass_label[cassnum])+"("+str(layer)+str(cass_label[cassnum])+").dxf"

output_folder = "TestDXFfiles" # <---- Change to what you want your output folder to be

file_path = os.path.join(output_folder, filename)
doc.saveas(file_path)
print("Saving to "+file_path) 