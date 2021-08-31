import base64
import gzip
import io
import uuid
import argparse
from struct import *

assets = {
    "unique_asset_count": 0,
    "asset_data": []
}

assetListEntryLength = 20
assetPositionEntryLength = 8

def main():
    arg_parser = argparse.ArgumentParser(description="Decode or Encode TaleSpire slabs to/from JSON", epilog="If no arguments are specified (or some important ones are omitted), SlabelFish will instead launch into interactive mode where the (missing) options are asked via input prompts.")
    
    arg_parser.add_argument('-v', '--verbose', action='store_true', help="Show internal messages while de- or encoding slabs. Useful for debugging or learning the format.")
    arg_parser.add_argument('-e', '--encode', action='store_true', help="Specifies that JSON data is provided which is to be encoded into a TaleSpire slab. If this is specified together with -d, SlabelFish will interpret it as -a being set")
    arg_parser.add_argument('-d', '--decode', action='store_true', help="Specifies that TaleSpire slab data is provided which is to be decoded into JSON. If this is specified together with -e, SlabelFish will interpret it as -a being set")
    arg_parser.add_argument('-a', '--automatic', action='store_true', help="Tries to guess based on input data entered --in whether to decode or encode and whether to read the data directly from the argument or if it's stored in a file and the file name was specified.")
    arg_parser.add_argument('--in', type=ascii, metavar='IN_DATA', help="Enter input data, either the actual raw data (be it a TaleSpire slab or a JSON object) or a filename to read said data from.")
    arg_parser.add_argument('--out', type=ascii, metavar='OUT_DATA', help="Enter a file name that serves as output for the final result. Progress output like info messages with -v are still printed on the command line.")
    
    #arg_parser.add_argument()
    
    
    args = arg_parser.parse_args()
    print(args)
    
if __name__ == '__main__':
    main()
    

def assembleBytes(byteList):
    total = 0
    for i in range(len(byteList)):
        total = (total << 8) + byteList[i] #take old total shift it to the left by 8 (make space for another byte), add next byte in list
    return total

def decodeAsset(assetData):
    #print("\ndecoding raw asset", ':'.join(format(x, '02X') for x in tileData))
    decData = unpack('IHH8BI', assetData)
    uuid = (decData[0], decData[1], decData[2], assembleBytes(decData[3:5]), assembleBytes(decData[5:11]))
    instanceCount = decData[11]
    #print("\ndecoded tile data:", '-'.join(format(x, 'X') for x in decData))
    #print("ordered decoded tile data:", '-'.join(format(x, 'X') for x in uuid))
    uuidString = '-'.join(format(x, 'X') for x in uuid)
    print("parsed UUID:", uuidString, "--- nr instances:", instanceCount)
    assets["asset_data"].append({
        "uuid": uuidString,
        "instance_count": instanceCount,
        "instances": [] #rename to instance_position? or just positions?
    })

def decodeAssetPosition(assetPositionData, decAssetCount):
    #decode position from blob passed on
    print("decoding raw asset position", ':'.join(format(x, '02X') for x in assetPositionData))
    positionBlob = unpack("<Q", assetPositionData)[0]  #unpack as little endian. data is stored as 2 bit pad, 8 bit rot, 2 bit pad, 16 bit y, 2 bit pad, 16 bit z, 2 bit pad, 16 bit x
    print("blob:", format(positionBlob, '064b'))
    #x, y and z are 16bit, rot is 8 bit. all have 2 bit padding between each other.
    x = positionBlob & 0xFFFF # isolate lowest 16 bits (x position)
    y = (positionBlob >> 36) & 0xFFFF # shift away the x and z coord + 2*2 bit padding
    z = (positionBlob >> 18) & 0xFFFF # shift away the x coord + 2 bit padding
    rot = positionBlob >> 54 #shift away x, y and z coord + 3*2 padding (54 places) to get rotation to LSB
    #print("x: %d, y: %d, z: %d | rot: %d\n" % (x,y,z,rot))
    
    #figure out which asset this position actually belongs to and store it 
    subTotal = 0
    currentAsset = 0
    for i in range(len(assets["asset_data"])):
        subTotal += assets["asset_data"][i]["instance_count"]
        if (decAssetCount < subTotal): #check if the currently iterated through asset in the asset list is the one we are currently decoding the pos of
            assets["asset_data"][i]["instances"].append({
                "x": x,
                "y": y,
                "z": z,
                "degree": rot*15
            })
            break
    
slabFileName = input("Enter file containing slab code: ")
#slabFileName = "test_slabs/rot_prop"

#read slab
slabFile = open(slabFileName, "r")
slabRawData = slabFile.read()

#decode base64
base64Bytes = slabRawData.encode('ascii')
slabCompressedData = base64.b64decode(base64Bytes)

#enter data into virtual gzip file, then decompress it
gzipFile = io.BytesIO()
gzipFile.write(slabCompressedData)
gzipFile.seek(0)

slabData = gzip.GzipFile(fileobj = gzipFile, mode = "rb").read()

print("\nraw:\n", slabRawData)
#print("\ncompressed:", slabCompressedData)
#print("data:", slabData)
print("\ndata:\n", ":".join("{:02x}".format(c) for c in slabData))

print("\n--- parsing ---")
header = slabData[:10]
assets["unique_asset_count"] = unpack("I", header[6:])[0]
uniqueAssetCount = unpack("I", header[6:])[0]
assetList = slabData[len(header):len(header) + assets["unique_asset_count"] * assetListEntryLength]
assetPositionList = slabData[len(header) + len(assetList):]

print("- header -\n")
print(":".join("{:02x}".format(c) for c in header))
print("\n- asset list -\n")
print(":".join("{:02x}".format(c) for c in assetList))
print("\n- asset positions -\n")
print(":".join("{:02x}".format(c) for c in assetPositionList))

#decode asset list
print("\n- decoding asset list -\n")
print("# unique:", assets["unique_asset_count"])
for i in range(assets["unique_asset_count"]):
    decodeAsset(assetList[i * assetListEntryLength : (i+1) * assetListEntryLength])
    
#decode asset positions
print("\n- decoding asset position list -\n")
decAssetCount = 0
while(len(assetPositionList[decAssetCount*assetPositionEntryLength:]) > assetPositionEntryLength):
    decodeAssetPosition(assetPositionList[decAssetCount * assetPositionEntryLength:(decAssetCount+1) * assetPositionEntryLength], decAssetCount)
    decAssetCount += 1
print(assets)