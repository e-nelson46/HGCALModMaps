# HGCALModMaps
This repository serves as a tool to create images (in the form of .dxf files) of various cassettes that will be used in the 2026 High Luminosity upgrades for the CMS experiment. Using data from the geometry_sipmontile_v16.6.hgcal.txt file located in this repository, the Trainbased_ModMapBuilder.py script locate and draw each individual module, rotating when necessary to keep a consistant display format. It also displays important information specific to each module such as the index, what train it belongs to, as well as if it is a high density, low density, or scintillator module. Trains are denoted by different colors, and other information is printed inside the individual modules. The script also makes an additional .json file containing information about each train and module in the specified cassette.

## Required Packages
To run this you will need the following python libraries installed:
- ezdxf
- pandas
- numpy

These can be installed with the typical pip install or using the requirements.txt file.

## Syntax and Naming Conventions
After copying the repository, you can make individual .dxf and .json files using the command:  
```
python3 Trainbased_ModMapBuilder.py 33 2  #args: layer number, cassette number
```
This will save a .dxf file to the specified output folder at the end of the script.  The script defaults to an output folder called TestDXFfiles.  Then it will create a .json file, saving it to the current working directory. These files have the naming convention:


Cassette_'layer number'_'cassette number'.'file type'  


The layers go from 27 to 47 and each layer has 4 cassettes.
You can use either the 1-20 naming scheme or the 27-47 naming scheme when calling the script and you can either specify the cassette by the number (1-4) or letter (A-D).

To run through mulitple layers and their cassettes, use the bash script shown below:  

```
for i in {27..47}; do
	for j in {1..4}; do
		python3 Trainbased_ModMapBuilder.py "$i" "$j"
	done
done
```
