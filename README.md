# SlabelFish
A de- and encoder for TaleSpire Slabs.

Currently knows the "Chimera" Slab Format.

Decodes to JSON for human readable editing, can reencode back to the slab binary format (encoder part not yet done)

## Dependencies
Tested and developed with Python 3.9.6, but just Python >=3 should suffice (not validated)

Depends on whatever Python screams at you when you try to run it. *ToDo: Proper dependency list*

## Usage
run
`python slab_decoder.py`

In the input prompt enter the file name that contains the slab data (and *only* the slab data)

It will read the file, decode the slab and print the decoded JSON to console (you may need to replace ' with " for the JSON to work in the tool of your choice)
