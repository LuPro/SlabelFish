import gzip
import base64

def print_info(level, msg, verbose, quiet):
    if (level == "info_quiet" and verbose == True and quiet == False):
        print(msg)
    elif ((level == "info" or level == "warning") and verbose == True and quiet == False):
        print(level + ": " + msg)
    elif (level == "error" and quiet == False):
        print(level + ": " + msg, file=sys.stderr)


def format_binary(data):
    return ":".join("{:02X}".format(b) for b in data)
