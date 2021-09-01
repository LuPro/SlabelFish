import base64
import gzip
import io
import uuid
import argparse
import re
import sys
import json
from struct import *

def print_info(level, msg, verbose, quiet):
    if (level == "info_quiet" and verbose == True and quiet == False):
        print(msg)
    elif ((level == "info" or level == "warning") and verbose == True and quiet == False):
        print(level + ": " + msg)
    elif (level == "error" and quiet == False):
        print(level + ": " + msg, file=sys.stderr)

def format_binary(data):
    return ":".join("{:02X}".format(b) for b in data)


# ------- decode part start

#replace with .from_bytes?
def assemble_bytes(bytes):
    total = 0
    for byte in bytes:
        total = (total << 8) + byte #take old total, shift it to the left by 8 (make space for another byte), add next byte in list
    return total

def decode_asset(asset_data, verbose=False, quiet=False):
    print_info("info_quiet", "      asset: " + format_binary(asset_data), verbose, quiet)
    dec_data = unpack('IHH8BI', asset_data)
    uuid = (dec_data[0], dec_data[1], dec_data[2], assemble_bytes(dec_data[3:5]), assemble_bytes(dec_data[5:11]))
    instance_count = dec_data[11]
    #print("\ndecoded tile data:", '-'.join(format(x, 'X') for x in decData))
    #print("ordered decoded tile data:", '-'.join(format(x, 'X') for x in uuid))
    uuid_string = '-'.join(format(x, 'X') for x in uuid)
    print_info("info_quiet", "      UUID: " + uuid_string + ", # instances: " + str(instance_count), verbose, quiet)
    
    return {
        "uuid": uuid_string,
        "instance_count": instance_count,
        "instances": [] #rename to instance_position? or just positions?
    }
    

#decodes an asset position, returns a tuple of which asset this position belongs to (index from asset list) as well as the position
def decode_asset_position(asset_position_data, assets, dec_asset_count, verbose=False, quiet=False):
    #decode position from blob passed on
    print_info("info_quiet", "\n      Decoding asset position from list: " + format_binary(asset_position_data), verbose, quiet)
    position_blob = unpack("<Q", asset_position_data)[0]  #unpack as little endian. data is stored as 2 bit pad, 8 bit rot, 2 bit pad, 16 bit y, 2 bit pad, 16 bit z, 2 bit pad, 16 bit x
    print_info("info_quiet", "      Read position blob as little endian (64 bit binary):\n        " + format(position_blob, '064b'), verbose, quiet)
    #x, y and z are 16bit, rot is 8 bit. all have 2 bit padding between each other.
    x = position_blob & 0xFFFF # isolate lowest 16 bits (x position)
    y = (position_blob >> 36) & 0xFFFF # shift away the x and z coord + 2*2 bit padding
    z = (position_blob >> 18) & 0xFFFF # shift away the x coord + 2 bit padding
    rot = position_blob >> 54 #shift away x, y and z coord + 3*2 padding (54 places) to get rotation to LSB
    print_info("info_quiet", "      Extracted coordinates and rotation from blob:\n        x: " + str(x) + ", y: " + str(y) + ", z: " + str(z) + " | rot: " + str(rot) + "(=" + str(rot*15) + "°)", verbose, quiet)
    
    #figure out which asset this position actually belongs to and store it
    print_info("info_quiet", "      Keeping track of which assets' position is being read (count asset list)", verbose, quiet)
    #print_info("info_quiet", "      Keep track of which asset position is being read. Done by iterating through asset list and summing up instance counts until the current number of parsed asset positions is lower or equal to the number of asset instances from the list. This is the asset this position belongs to.", verbose, quiet)
    sub_total = 0
    for i, asset in enumerate(assets['asset_data']):
        sub_total += asset['instance_count']
        if (dec_asset_count < sub_total): #check if the currently iterated through asset in the asset list is the one we are currently decoding the pos of
            return (i, {
                "x": x,
                "y": y,
                "z": z,
                "degree": rot*15
            })
            

def decode(data, asset_list_entry_length, asset_position_entry_length, verbose=False, quiet=False):
    out_json = {
        "unique_asset_count": 0,
        "asset_data": []
    }
    
    print_info("info", "Decoding slab:\n" + data + "\n", verbose, quiet)
    
    #decode base64
    base64_bytes = data.encode('ascii')
    slab_compressed_data = base64.b64decode(base64_bytes)

    #decompress gzip
    slab_data = gzip.decompress(slab_compressed_data)
    
    print_info("info_quiet", "Binary slab data after first base64 decoding, then gzip unpacking:\n" + format_binary(slab_data) + "\n", verbose, quiet)

    print_info("info_quiet", "--- Starting to parse slab", verbose, quiet)
    print_info("info_quiet", "  - Decoding slab header and splitting data into parts", verbose, quiet)
    header = slab_data[:10]
    out_json["unique_asset_count"] = unpack("I", header[6:])[0]
    asset_list = slab_data[len(header):len(header) + out_json["unique_asset_count"] * asset_list_entry_length]
    asset_position_list = slab_data[len(header) + len(asset_list):]

    print_info("info_quiet", "    Extracted header from binary slab data from indexes 0 to " + str(len(header)) + ", header is:\n      " + format_binary(header), verbose, quiet)
    print_info("info_quiet", "    Read unique asset count of " + str(out_json["unique_asset_count"]) + " from header. List length = unique_asset_count * 20 bytes per asset in list", verbose, quiet)
    print_info("info_quiet", "    Extracted asset list from binary slab data from indexes " + str(len(header)) + " to " + str((len(header) + len(asset_list))) + ", asset list is:\n" + format_binary(asset_list) + "\n", verbose, quiet)
    print_info("info_quiet", "    Extracted position list from binary data from index " + str((len(header) + len(asset_list))) + " to the end:\n" + format_binary(asset_position_list) + "\n", verbose, quiet)

    #decode asset list
    print_info("info_quiet", "  - Decoding asset list", verbose, quiet)
    for i in range(out_json["unique_asset_count"]):
        asset_data = decode_asset(asset_list[i * asset_list_entry_length : (i+1) * asset_list_entry_length], verbose, quiet)
        out_json["asset_data"].append(asset_data)
        
    #decode asset positions
    print_info("info_quiet", "  - Decoding asset position list", verbose, quiet)
    dec_asset_count = 0
    while(len(asset_position_list[dec_asset_count*asset_position_entry_length:]) > asset_position_entry_length):
        position = decode_asset_position(asset_position_list[dec_asset_count * asset_position_entry_length:(dec_asset_count+1) * asset_position_entry_length], out_json, dec_asset_count, verbose, quiet)
        out_json["asset_data"][position[0]]["instances"].append(position[1])
        dec_asset_count += 1
    
    return out_json

# ------- decode part end





# ------- encode part start

def create_header(unique_asset_count, verbose=False, quiet=False):
    header = b'\xCE\xFA\xCE\xD1\x02\x00'
    header += unique_asset_count.to_bytes(4, byteorder='little')
    return header


def encode_asset(asset_json, verbose=False, quiet=False):
    print_info("info_quiet", "    - Encoding asset: " + json.dumps(asset_json), verbose, quiet)
    asset_blob = b''
    uuid_parts = asset_json['uuid'].split("-")
    uuid_bytes = b''
    uuid_bytes += int(uuid_parts[0], 16).to_bytes(4, byteorder='little')
    uuid_bytes += int(uuid_parts[1], 16).to_bytes(2, byteorder='little')
    uuid_bytes += int(uuid_parts[2], 16).to_bytes(2, byteorder='little')
    uuid_bytes += int(uuid_parts[3], 16).to_bytes(2, byteorder='big')
    uuid_bytes += int(uuid_parts[4], 16).to_bytes(6, byteorder='big')
    asset_blob = uuid_bytes + asset_json['instance_count'].to_bytes(4, byteorder='little')
    print_info("info_quiet", "      Created asset list entry blob:\n        " + format_binary(asset_blob) + "\n", verbose, quiet)
    return asset_blob
    

#encodes an asset position
def encode_asset_position(instance_json, verbose=False, quiet=False):
    print_info("info_quiet", "          Encoding asset position: " + json.dumps(instance_json), verbose, quiet)
    position_blob = 0
    position_blob |= int(instance_json['x'])
    position_blob |= (int(instance_json['y']) << 36)
    position_blob |= (int(instance_json['z']) << 18)
    position_blob |= (int(instance_json['degree'] / 15) << 54)
    print_info("info_quiet", "          Created position blob:\n            " + format(position_blob, '064b') + "\n            " + format_binary(position_blob.to_bytes(8, byteorder='little')) + "\n", verbose, quiet)
    
    return position_blob.to_bytes(8, byteorder='little')
    
    
# creates asset list and asset position list     
def create_assets_data(assets_json, verbose=False, quiet=False):
    asset_list = b''
    position_list = b''
    
    for asset in assets_json: # create an entry in the asset list for each asset
        asset_list_entry = encode_asset(asset, verbose, quiet)
        asset_list += asset_list_entry
        for instance in asset['instances']: # create an entry in the position list for each instance of each asset
            print_info("info_quiet", "      - Creating position list for asset", verbose, quiet)
            position_list_entry = encode_asset_position(instance, verbose, quiet)
            position_list += position_list_entry
            
    return (asset_list, position_list)
            
def encode(data, verbose=False, quiet=False):
    slab_data = b'' # byte string slab blob
    encode_asset_position(json.loads('{"x": 5, "y": 13, "z": 611, "degree": 345}'), verbose, quiet)

    slab_json = json.loads(data)
    
    print_info("info_quiet", "--- Starting to create binary slab blob", verbose, quiet)
    # Updating internal json fields
    print_info("info_quiet", "    Updating unique asset count field", verbose, quiet)
    slab_json['unique_asset_count'] = len(slab_json['asset_data']) # no input validation! possibly keep track of duplicate entries (are they actually unique?) and either resolve or give warning in case of duplicates. Also no validation if # unique assets are too many for the format
    # also doesn't add in the proper order for a nice output if field was missing entirely. not important for function, but would be nice for usability
    for asset in slab_json['asset_data']:
        asset['instance_count'] = len(asset['instances'])
        #should do more validation on instances, but probably needs knowledge if a uuid stands for a tile or prop to differentiate between allowed positions and rotations of each of those
    # need to find the asset with the 0,0,0 tile and put it first in the lists (is this actually needed?)
    print_info("info_quiet", "  - Creating header", verbose, quiet)
    slab_data += create_header(len(slab_json['asset_data']), verbose, quiet)
    print_info("info_quiet", "      Header: " + format_binary(slab_data), verbose, quiet)
    print_info("info_quiet", "  - Creating asset list and position list", verbose, quiet)
    asset_data = create_assets_data(slab_json['asset_data'], verbose, quiet)
    slab_data += asset_data[0] + asset_data[1] + b'\x00\x00'
    
    print_info("info_quiet", "    Binary slab data:\n" + format_binary(slab_data), verbose, quiet)
    
    #gzip compress
    print_info("info_quiet", "  - Compressing binary slab data with gzip:", verbose, quiet)
    slab_compressed_data = gzip.compress(slab_data)
    
    #base64 encode
    print_info("info_quiet", "  - Base64 encoding gzip compressed data", verbose, quiet)
    base64_bytes = base64.b64encode(slab_compressed_data)
    
    return b'```' + base64_bytes + b'```'
    
    
# ------- encode part end

def read_arguments(args):
    exec_data = {
        'quiet': False,
        'verbose': False,
        'mode': None,
        'in_file': None,
        'in_data': None,
        'out': None
    }
    
    exec_data['verbose'] = args.verbose
    if (args.quiet == True):
        exec_data['quiet'] = True
        exec_data['verbose'] = False
    
    if (args.encode == True and args.decode == True): # I dislike the entire mode switch thing. It's long and feels like a lot of duplicated code. Would like to change/shorten, though not sure if possible with all the things I want it to do.
        print_info("warning", "Both encode and decode was specified. Trying to figure out which one was meant based on input (automatic mode)", exec_data['verbose'], exec_data['quiet'])
        exec_data['mode'] = 'automatic'
    elif (args.encode == True):
        settexec_dataings['mode'] = 'encode'
    elif (args.decode == True):
        exec_data['mode'] = 'decode'
    else:
        if (args.encode == False and args.decode == False and args.automatic == False):
            while (1):
                mode = input("Do you want to encode JSON data into a TaleSpire slab or decode a TaleSpire slab into JSON?\nEnter 'e' for encode, 'd' for decode or 'a' for automatic mode:\n")
                if (mode == 'e'):
                    exec_data['mode'] = 'encode'
                    break
                elif (mode == 'd'):
                    exec_data['mode'] = 'decode'
                    break
                elif (mode == 'a'):
                    exec_data['mode'] = 'automatic'
                    break
                else:
                    print("\nThis is an invalid option, please enter a valid one.\n")
        else:
            if (args.encode == True):
                exec_data['mode'] = 'encode'
            elif (args.decode == True):
                exec_data['mode'] = 'decode'
            elif (args.automatic == True):
                exec_data['mode'] = 'automatic'
            else:
                print_info("error", "This error should be unreachable. There are no mode flags set but it was not caught earlier to ask for input. Aborting.", exec_data['verbose'], exec_data['quiet'])
                sys.exit(1)
                
    exec_data['out'] = args.out
    if (args.in_file != None and args.data != None):
        exec_data['in_data'] = args.data
    elif (args.in_file == None and args.data == None):
        in_data = input("Please enter the data you want converted. You can either directly paste the data (a TaleSpire slab or a JSON string) here, or specify a file name that contains this (and only this) data.\n")
        #match = re.search('^```.*```$|.+\.json$', in_data)
        if (re.fullmatch('^```.*```$|^{.*}$', in_data, flags=re.DOTALL) != None):
            exec_data['in_data'] = in_data
        else:
            exec_data['in_file'] = in_data
            
        if (args.out == None):
            exec_data['out'] = input("Do you also want to store the result in a specific file? If not it will just be displayed at the end of the program execution. Enter the file name you want or leave empty and press enter.\n")
    else:
        exec_data['in_data'] = args.data
        exec_data['in_file'] = args.in_file
            
    return exec_data

def main():
    asset_list_entry_length = 20
    asset_position_entry_length = 8

    arg_parser = argparse.ArgumentParser(description="Decode or Encode TaleSpire slabs to/from JSON", epilog="If no arguments are specified (or some important ones are omitted), SlabelFish will instead launch into interactive mode where the (missing) options are asked via input prompts.")
    
    arg_parser.add_argument('-v', '--verbose', action='store_true', help="Show internal messages while de- or encoding slabs. Useful for debugging or learning the format. Errors will be shown nontheless.")
    arg_parser.add_argument('-q', '--quiet', action='store_true', help="Turn off all internal messages apart from the final conversion result and necessary input prompts. Overrides -v.")
    arg_parser.add_argument('-e', '--encode', action='store_true', help="Specifies that JSON data is provided which is to be encoded into a TaleSpire slab. If this is specified together with -d, SlabelFish will interpret it as -a being set")
    arg_parser.add_argument('-d', '--decode', action='store_true', help="Specifies that TaleSpire slab data is provided which is to be decoded into JSON. If this is specified together with -e, SlabelFish will interpret it as -a being set")
    arg_parser.add_argument('-a', '--automatic', action='store_true', help="Tries to guess based on input data entered --in whether to decode or encode and whether to read the data directly from the argument or if it's stored in a file and the file name was specified.")
    arg_parser.add_argument('--in_file', metavar='IN_FILE', help="Enter a file name for SlabelFish to read the data (TaleSpire slab or JSON string) from. Don't specify this and positional argument 'data' at the same time, in case of conflict, this will be discarded.")
    arg_parser.add_argument('--out', metavar='OUT_DATA', help="Enter a file name that serves as output for the final result. Progress output like info messages with -v are still printed on the command line.")
    arg_parser.add_argument('data', metavar='IN_DATA', nargs='?', help="Enter raw input data (TaleSpire slab or JSON string) for conversion. Don't specify this and '--in_file' at the same time, in case of conflict this takes precedence.")
    exec_data = read_arguments(arg_parser.parse_args())
    
    # Get data to convert
    data = None
    print_info("info", "Reading input data...", exec_data['verbose'], exec_data['quiet'])
    if (exec_data['in_file'] != None):
        in_file = open(exec_data['in_file'], "r")
        data = in_file.read()
        in_file.close()
    elif (exec_data['in_data'] != None):
        data = exec_data['in_data']
    else:
        print_info("error", "No in file or data was specified while trying to gather data for conversion! Aborting.", exec_data['verbose'], exec_data['quiet'])
        sys.exit(1)
        
    print_info("info", "Done.", exec_data['verbose'], exec_data['quiet'])

    # Check if decode, encode or automatic switch
    out_data = None
    if (exec_data['mode'] == 'encode'):
        out_data = encode(data, exec_data['verbose'], exec_data['quiet'])
    elif (exec_data['mode'] == 'decode'):
        out_data = decode(data, asset_list_entry_length, asset_position_entry_length, exec_data['verbose'], exec_data['quiet'])
    elif (exec_data['mode'] == 'automatic'):
        #if (re.fullmatch('^```.*```$|^{.*}$', data) != None):
        if (re.fullmatch('^```.*```$', data) != None): # Decode
            exec_data['mode'] = 'decode'
            print_info("info", "Interpreted input as slab data, setting to decode.", exec_data['verbose'], exec_data['quiet'])
            out_data = decode(data, asset_list_entry_length, asset_position_entry_length, exec_data['verbose'], exec_data['quiet'])
        elif (re.fullmatch('^{.*}$', data, flags=re.DOTALL) != None): #Encode
            exec_data['mode'] = 'encode'
            print_info("info", "Interpreted input as JSON data, setting to encode.", exec_data['verbose'], exec_data['quiet'])
            out_data = encode(data, exec_data['verbose'], exec_data['quiet'])
        else:
            print_info("error", "Can't recognize input data as either TaleSpire slab data or JSON! Aborting.", exec_data['verbose'], exec_data['quiet'])
            sys.exit(1)
    else:
        print_info("error", "Encountered an invalid mode (" + exec_data['mode'] + ")!", exec_data['verbose'], exec_data['quiet'])
        sys.exit(1)
        
    if (exec_data['out'] == None):
        print_info("info_quiet", "\n---\n\nResult:", True, exec_data['quiet'])
        if (exec_data['mode'] == 'decode'): # can I do that nicer?
            #print(json.dumps(out_data, indent=2)) #make cmd argument for pretty print? default pretty with flag for short?
            print_info("info_quiet", json.dumps(out_data), True, exec_data['quiet'])
        elif (exec_data['mode'] == 'encode'):
            print_info("info_quiet", out_data, True, exec_data['quiet'])
    else:
        out_file = open(exec_data['out'], "w")
        if (exec_data['mode'] == 'decode'): # can I do that nicer?
            out_file.write(json.dumps(out_data, indent=2))
        elif (exec_data['mode'] == 'encode'):
            out_file.write(out_data)
        out_file.close()
        
    sys.exit(0)
        
    
if __name__ == '__main__':
    main()
    