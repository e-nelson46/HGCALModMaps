import ezdxf
import pandas as pd
import os

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

############Initial setup to open files and create ezdxf objects#############

df=pd.read_csv('geometry_sipmontile_v16.6.hgcal.txt',delim_whitespace=True)
doc = ezdxf.new("R2010")
msp = doc.modelspace()

############Cutting panda dataframe############


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

cass = df[col]
print("Cassestte dataframe:")
print(cass)
############Drawing the objects############
print("Drawing modules...")
for module in cass:
    origin_x, origin_y = module.loc('x0'), module.loc('y0')
    print(f"Finished module {module}")


############Saving objects to file#############
filename = "Test_0_1"
output_folder = "TestDXFfiles"
hexagon_path = os.path.join(output_folder, filename)

#doc.saveas(hexagon_path)
print("DXF file successfully created!")

Full dataframe: 
      plane  u   v  isSiPM  itype typecode      x0       y0  irot  nvertices   vx_0    vy_0   vx_1    vy_1   vx_2    vy_2   vx_3    vy_3  vx_4    vy_4   vx_5    vy_5   vx_6    vy_6  icassette  trigRate  trigLinks  dataRate_ld  dataLinks_ld  dataRate_hd  dataLinks_hd  MB  wagon  isEngine  nROCs  power  mrot     phi  HDorLD     hash  hash_hdld  engine_trig_fibres  engine_data_fibres  engine_ctrl_fibres               dataPp0               trigPp0 dataPp0_type trigPp0_type            dataPp1             trigPp1 dataPp1_type trigPp1_type         dataPp2    DAQ
3421     33  5  10       0     FO   ML-F3T   -2.16  1458.46     5          6   -2.2  1361.7   81.6  1410.0   81.6  1506.8   -2.2  1555.3  -86.0  1506.8  -86.0  1410.0   -2.2  1361.7          4     0.658          2        0.227             1        0.225             1  23      1     False      3    3.6     0  90.085       0  3305100    3305100                   2                   1                   1  PP0(CE-)L33/C04_FO_1  PP0(CE-)L33/C04_FO_3            A            A  PP1(CE-)11_FO_2_8  PP1(CE-)11_FO_2_20           Ap           Ap  PPFO(CE-)X5_17  DAQ_2_5
3422     33  5  11       0     FO   ML-F3T  -85.98  1603.65     5          6  -86.0  1506.8   -2.2  1555.3   -2.2  1652.0  -86.0  1700.5 -169.8  1652.0 -169.8  1555.3  -86.0  1506.8          4     0.658          2        0.224             1        0.223             1  23      1     False      3    3.6     0  93.069       0  3305110    3305110                   2                   1                   1  PP0(CE-)L33/C04_FO_1  PP0(CE-)L33/C04_FO_3            A            A  PP1(CE-)11_FO_2_8  PP1(CE-)11_FO_2_20           Ap           Ap  PPFO(CE-)X5_17  DAQ_2_5
3423     33  5  12       0    FOe   ML-F3T -169.80  1748.83     5          6 -169.8  1652.0  -86.0  1700.5  -86.0  1797.2 -169.8  1845.6 -253.7  1797.2 -253.7  1700.5 -169.8  1652.0          4     0.648          2        0.223             1        0.222             1  23      0      True      3    3.6     0  95.546       0  3305120    3305120                   2                   1                   1  PP0(CE-)L33/C04_FO_1  PP0(CE-)L33/C04_FO_3            A            A  PP1(CE-)11_FO_2_8  PP1(CE-)11_FO_2_20           Ap           Ap  PPFO(CE-)X5_17  DAQ_2_5
3424     33  5  13       0   dOeR   ML-R3T -253.62  1894.00     0          5 -169.8  1845.6 -169.8  1894.0 -337.5  1894.0 -337.5  1845.6 -253.7  1797.2 -169.8  1845.6    0.0     0.0          4     0.646          2        0.150             1        0.150             1  23      0     False      2    2.4     0  97.627       0  3305130    3305130                   2                   1                   1  PP0(CE-)L33/C04_FO_1  PP0(CE-)L33/C04_FO_3            A            A  PP1(CE-)11_FO_2_8  PP1(CE-)11_FO_2_20           Ap           Ap  PPFO(CE-)X5_17  DAQ_2_5
3425     33  6  12       0  bOeRL   ML-53T   -2.16  1748.83     3          5   81.6  1797.2  -86.0  1797.2  -86.0  1700.5   -2.2  1652.0   81.6  1700.5   81.6  1797.2    0.0     0.0          4     0.644          2        0.198             1        0.198             1  23      1     False      3    3.6     0  90.071       0  3306120    3306120                   2                   1                   1  PP0(CE-)L33/C04_FO_1  PP0(CE-)L33/C04_FO_3            A            A  PP1(CE-)11_FO_2_8  PP1(CE-)11_FO_2_20           Ap           Ap  PPFO(CE-)X5_17  DAQ_2_5


