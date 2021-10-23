import gzip
import base64
import json
import sys

#todo: global kinda ugly. not sure what the "pythonic" way of doing this would be. class? struct? investigate
asset_list_entry_length = 20
asset_position_entry_length = 8

def print_info(level, msg, verbose, quiet):
    if ((level == "info_quiet" or level == "data_warning_quiet") and verbose == True and quiet == False):
        print(msg)
    elif ((level == "info" or level == "warning" or level == "data_warning") and verbose == True and quiet == False):
        print(level + ": " + msg)
    elif (level == "error" and quiet == False):
        print(level + ": " + msg, file=sys.stderr)

#needs the modified asset json with the injected type
def asset_str(asset):
    if (asset == None):
        return "Unknown Asset"
    else:
        return "Name: " + asset["Name"] + " (" + asset["type"] + "), UUID: " + asset["Id"]

def format_binary(data):
    return ":".join("{:02X}".format(b) for b in data)
