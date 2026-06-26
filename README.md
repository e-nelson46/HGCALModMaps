# HGCALModMaps
This repository serves as a tool to create images (in the form of .dxf files) of various cassettes that will be used in the 2026 High Luminosity upgrades for the CMS experiment. Using data from the geometry_sipmontile_v16.6.hgcal.txt file located in this repository, the script ModMapBuilder.py locates and draws each individual module, rotating when necessary to keep a consistant display format. It is also displays important information specific to each module such as the index, what train it belongs to, as well as if it is a high density, low density, or scintillator module. Trains are denoted by different colors, and other information is printed inside the individual modules.

## Syntax and Naming Conventions
After copying the repository, you can make individual .dxf files using the synax:  
```
python3 ModMapBuilder.py 26 1  #args: file, layer number, cassette number
```
This will save a .dxf file in the folder TestDXFfiles with the naming convention  
Cassette_'layer number'_'cassette number'  
The layers go from 1 to 47 and each layer has 4 cassettes.

To run through mulitple layers and their cassettes, use the bash script shown below:  

```
for i in {26..47}; do
	for j in {1..4}; do
		python3 DataManipulation.py "$i" "$j"
	done
done
```
