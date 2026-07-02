# HGCALModMaps
This repository serves as a tool to create images (in the form of .dxf files) of various cassettes that will be used in the 2026 High Luminosity upgrades for the CMS experiment. Using data from the geometry_sipmontile_v16.6.hgcal.txt file located in this repository, ModMapBuilder.py scripts locate and draw each individual module, rotating when necessary to keep a consistant display format. It also displays important information specific to each module such as the index, what train it belongs to, as well as if it is a high density, low density, or scintillator module. Trains are denoted by different colors, and other information is printed inside the individual modules.

## The different files

There are two different ModMapBuilder.py files, Trainbased and Modbased.  Currently Trainbased is the most up to date and gives the best output.  These two files take different approaches to drawing the Mod Map hinted at in their titles.  The Modbased file is simpler and draws out the map module by module for the whole cassette requiring module by module logic.  The Trainbased script is more complex, but is better suited for many of the problems.  Trainbased_ModMapBuilder.py seperates the cassette into trains and is able to individually classify the trains before printing out module by module, train by train, allowing for greater freedom in how the script can gain data about each module.  Our recommendation is to use Trainbased_ModMapBuilder.py.

The file geometry_sipmontile_v16.6.hgcal.txt is the raw mod map data from which our scripts pull from.  The modulemapper pdf contains photos of the layout of each layer.

## Syntax and Naming Conventions
After copying the repository, you can make individual .dxf files using the synax:  
```
python3 Trainbased_ModMapBuilder.py 26 1  #args: file, layer number, cassette number
```
This will save a .dxf file in the folder TestDXFfiles with the naming convention  
Cassette_'layer number'_'cassette number'  
The layers go from 1 to 47 and each layer has 4 cassettes.

To run through mulitple layers and their cassettes, use the bash script shown below:  

```
for i in {26..47}; do
	for j in {1..4}; do
		python3 Trainbased_ModMapBuilder.py "$i" "$j"
	done
done
```
