# HGCALModMaps
A place to make code to create module maps for HGCAL cassettes
More info to come...

## What to Run
After copying the repository, you can make individual .dxf files using the synax
python3 DataManipulation.py 26 1, where the first argument is the layer number 
and the second is the cassette number.
This will save a .dxf file in the folder TestDXFfiles with the naming convention  
Cassette_'layer'_'cassette'

To run through all Fermilab layers (26-47) and cassettes, copy and paste the bash  
script shown below:  

```
for i in {26..47}; do
	for j in {1..4}; do
		python3 DataManipulation.py "$i" "$j"
	done
done
```
