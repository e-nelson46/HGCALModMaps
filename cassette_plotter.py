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




