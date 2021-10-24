# Disclaimer
There is now an [official documentation](https://github.com/Bouncyrock/DumbSlabStats/blob/master/format.md). This is kept here to have a "different wording" for the format to help with development/understanding, but as this is from reverse engineering the format myself it's not 100% correct everywhere, so refer to the official documentation where they differ.

# Slab data packing
Slab data is first archived with gzip and the resulting binary data encoded with base64. To decode slabs you have to do these steps in reverse, so first decode with base64 and then unzip using gzip (in my test I just used the Python gzip library, Baggers has said for the last format the default C# gzip implementation works, ... It should be fairly straightforward)
Once this is decoded you should be left with a string of binary data.

# Binary Data Format
*Disclaimer: Some variables seem to be little endian, some big endian, not 100% sure on that stuff*

## Header [10 bytes]
bytes 0-4 are always identical: `0x CE FA CE D1 02` (version identifier?)

byte 5: Padding (= 0) (?)

bytes 6-9: Number of unique assets in slab (Investigate, could also be bytes 5-6)

## Asset list [n * 20 bytes]
*Contains a list of all assets (tiles and props) in use in this slab*

### Asset [20 bytes]
bytes 0-15: UUID. Some "groups" seem to be reversed: `08:d2:cf:32:63:c3:34:44:b8:17:8b:a5:9f:ae:ed:17` -> `08:d2:cf:32` = reversed; `63:c3` = reversed; `34:44` = reversed; `b8:17` = not reversed; `8b:a5:9f:ae:ed:17` = not reversed. Actual resulting UUID is `32CFD208-C363-4434-B817-8BA59FAEED17`

bytes 16-19: Number of instances of this tile

next asset ... (is a list, no padding in between elements)

## Asset positioning list [n * 8 bytes]
*Contains a list of all asset positions (and rotations)*

The asset positioning list contains each position of each asset, where one position consists of a "2 byte" (due to copy size limitations of 100x100x100, only 14 bits are ever used) x, y and z position and a "1 byte" (5 bits used) rotation. The asset positions contain no reference to the asset list, but they are ordered the same way. So if the asset list has on the first index 3 instances of the "Tavern Floor 2x2", the first 3 entries in the asset positioning list will be the 3 tavern floors and so on.

### Asset position [8 bytes]
When read as *little endian* the data is structured as follows *written in bits, not bytes*, where spaces are byte boundaries, "x", "y" and "z" mean bits that belong to the variable for their respective axis, "R" mean bits belonging to the rotation that are actually used, "r" are the "leftover" bits in the byte and "P" means padding: 
`PPrrrRRR RRPPyyyy yyyyyyyy yyyyPPzz zzzzzzzz zzzzzzPP xxxxxxxx xxxxxxxx`

The x, y and z coordinates are stored as integers where 100 means "1 tile" distance (1 grid unit). This means the slab format has 1/100 of a tile precision for prop placement.
The rotation is stored as an integer from 0-23, where each value is a rotation "ID". The actual angle is calculated like this: `rot * 15`. Each rotation step is 15°, full 360° rotation are 24 steps (0-23)

## End
The end is 4 bytes padding.
