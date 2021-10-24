from utils import *
import assets_reader

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
def encode_asset_position(instance_json, uuid, offset=[0,0,0], validate=False, verbose=False, quiet=False):
    print_info("info_quiet", "          Encoding asset position: " + json.dumps(instance_json), verbose, quiet)
    if (validate):
        asset = assets_reader.get_asset(uuid)
        if (asset == None):
            print_info("error", "Tried finding asset metadata for UUID " + uuid + ", but failed terribly. Maybe no TS base dir was specified?", verbose, quiet) #TODO would be interesting to have a CLI flag toggle that allows to break here. For now try to continue
            type = "unknown"
        else:
            type = asset["type"]

        if (type == "unknown"):
            print_info("data_warning_quiet", "Tried finding an asset with UUID " + uuid + ", but couldn't find one. Interpreting as prop for least restrictions.", verbose, quiet)

        if (instance_json['degree'] % 15 != 0 or instance_json['degree'] > 360 or instance_json['degree'] < 0):
            if (type == "Tiles"):
                print_info("data_warning_quiet", "            Rotation invalid, valid values for tiles are 0, 90, 180 and 270 (raw values 0,6,12,18)\n            " + asset_str(asset) + "\n", verbose, quiet)
                #todo make a strict vs non-strict mode. in non-strict it would accept an invalid rotation and round to the nearest valid one and continue
                sys.exit(1)
            elif (type == "Props" or type == "unknown"):
                print_info("data_warning_quiet", "            Rotation invalid, valid values are 0-360 (raw values 0-23)\n            " + asset_str(asset) + "\n", verbose, quiet)
                sys.exit(1)

        if (type == "Tiles"):
            #most tiles are limited to steps of 100 but some (like corner fillers) can be placed more finely. not sure how to figure out which is which from the metadata
            if ((instance_json['x'] + offset[0]) % 50 != 0 or (instance_json['y'] + offset[1]) % 50 != 0):
                print_info("data_warning_quiet", "            x-y coordinates invalid, must be a multiple of 100 for tiles (relative to all other tiles)\n            " + asset_str(asset) + "\n", verbose, quiet)
                sys.exit(1)
            if ((instance_json['z'] + offset[2]) % 25 != 0):
                print_info("data_warning_quiet", "            z coordinate invalid, must be a multiple of 25 for tiles (relative to all other tiles)\n            " + asset_str(asset) + "\n", verbose, quiet)
                sys.exit(1)

    position_blob = 0
    position_blob |= int(instance_json['x'])
    position_blob |= (int(instance_json['y']) << 36)
    position_blob |= (int(instance_json['z']) << 18)
    position_blob |= (int(instance_json['degree'] / 15) << 54)
    print_info("info_quiet", "          Created position blob:\n            " + format(position_blob, '064b') + "\n            " + format_binary(position_blob.to_bytes(8, byteorder='little')) + "\n", verbose, quiet)

    return position_blob.to_bytes(8, byteorder='little')


# creates asset list and asset position list
def create_assets_data(assets_json, offset=[0,0,0], validate=False, verbose=False, quiet=False):
    asset_list = b''
    position_list = b''

    for asset in assets_json: # create an entry in the asset list for each asset
        asset_list_entry = encode_asset(asset, verbose, quiet)
        asset_list += asset_list_entry
        for instance in asset['instances']: # create an entry in the position list for each instance of each asset
            print_info("info_quiet", "      - Creating position list for asset", verbose, quiet)
            position_list_entry = encode_asset_position(instance, asset['uuid'], offset, validate, verbose, quiet)
            position_list += position_list_entry

    return (asset_list, position_list)

#this function name sucks ass
def iterate_tiles_for_offset(json, validate=False):
    if (validate == False):
        return [0,0,0]
    assets = json["asset_data"]
    minPos = [20000, 20000, 20000]
    for asset_json in assets:
        asset = assets_reader.get_asset(asset_json["uuid"])
        if (asset == None):
            return [0,0,0] # If asset metadata finding fails, skip. This should *never* happen unless no TS base dir is specified, in which case this part of the code should never be reached anyways.
        elif (asset["type"] == "Tiles"):
            for instance in asset_json["instances"]:
                if (instance["x"] < minPos[0]):
                    minPos[0] = instance["x"]
                if (instance["y"] < minPos[1]):
                    minPos[1] = instance["y"]
                if (instance["z"] < minPos[2]):
                    minPos[2] = instance["z"]

    return [(100 - (minPos[0] % 100)) % 100, (100 - (minPos[1] % 100)) % 100, (25 - (minPos[2] % 25)) % 25]


def encode(data, validate=False, verbose=False, quiet=False):
    slab_data = b'' # byte string slab blob
    #encode_asset_position(json.loads('{"x": 5, "y": 13, "z": 611, "degree": 345}'), verbose, quiet)

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

    print_info("info_quiet", "  - Checking offset from grid", verbose, quiet)
    grid_offset = iterate_tiles_for_offset(slab_json, validate)
    print_info("info_quiet", "  - Creating asset list and position list", verbose, quiet)
    asset_data = create_assets_data(slab_json['asset_data'], grid_offset, validate, verbose, quiet)
    slab_data += asset_data[0] + asset_data[1] + b'\x00\x00'

    print_info("info_quiet", "    Binary slab data:\n" + format_binary(slab_data), verbose, quiet)

    #gzip compress
    print_info("info_quiet", "  - Compressing binary slab data with gzip:", verbose, quiet)
    slab_compressed_data = gzip.compress(slab_data, compresslevel=9, mtime=0)

    #base64 encode
    print_info("info_quiet", "  - Base64 encoding gzip compressed data", verbose, quiet)
    base64_bytes = base64.b64encode(slab_compressed_data)

    return b'```' + base64_bytes + b'```'

