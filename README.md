# HGCALModMaps
A place to make code to create module maps for HGCAL cassettes
More info to come...

## Syntax and Naming Conventions
After copying the repository, you can make individual .dxf files using the synax:  
python3 DataManipulation.py 26 1  
Where the first argument is the layer number (26-47) 
and the second is the cassette number (1-4).
This will save a .dxf file in the folder TestDXFfiles with the naming convention  
Cassette_'layer number'_'cassette number'

To run through mulitple layers and their cassettes, use the bash script shown below:  

```
for i in {26..47}; do
	for j in {1..4}; do
		python3 DataManipulation.py "$i" "$j"
	done
done
```
