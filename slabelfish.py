import io
import uuid
import argparse
import re
import os

from utils import *
import encoder
import decoder
import assets_reader

def get_data(in_file, in_data, verbose=False, quiet=False):
    # Get data to convert
    data = None
    print_info("info", "Reading input data...", verbose, quiet)
    if (in_file != None):
        if (in_file == "stdin"):
            data = input()
        else:
            in_file = open(in_file, "r")
            data = in_file.read()
            in_file.close()
    elif (in_data != None):
        data = in_data
    else:
        print_info("error", "No in file or data was specified while trying to gather data for conversion! Aborting.", exec_data['verbose'], exec_data['quiet'])
        sys.exit(1)

    print_info("info", "Done.", verbose, quiet)
    return data

def read_arguments(args):
    exec_data = {
        'quiet': False,
        'verbose': False,
        'pipeline': False,
        'mode': None,
        'in_data': None,
        'out': None,
        'compact': None,
        'ts_dir': None
    }

    exec_data['pipeline'] = args.pipeline
    
    exec_data['verbose'] = args.verbose
    if (args.quiet == True):
        exec_data['quiet'] = True
        exec_data['verbose'] = False

    exec_data['compact'] = args.compact
    
    if (args.encode == True and args.decode == True): # I dislike the entire mode switch thing. It's long and feels like a lot of duplicated code. Would like to change/shorten, though not sure if possible with all the things I want it to do.
        print_info("warning", "Both encode and decode was specified. Trying to figure out which one was meant based on input (automatic mode)", exec_data['verbose'], exec_data['quiet'])
        exec_data['mode'] = 'automatic'
    elif (args.encode == True):
        exec_data['mode'] = 'encode'
    elif (args.decode == True):
        exec_data['mode'] = 'decode'
    elif (args.automatic == True):
        exec_data['mode'] = 'automatic'
    else: #no valid mode was specified, ask for one if interactive mode is wanted
        if (exec_data['pipeline']):
            print_info("error", "Missing argument, no encode, decode or automatic mode specified", exec_data['verbose'], exec_data['quiet'])
            sys.exit(1)

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
                
    exec_data['out'] = args.out
    if (args.in_file != None and args.data != None):
        exec_data['in_data'] = args.data
    elif (args.in_file == None and args.data == None):
        if (exec_data['pipeline']):
            print_info("error", "Missing argument, no input data specified.", exec_data['verbose'], exec_data['quiet'])
            sys.exit(1)

        in_data = input("Please enter the data you want converted. You can either directly paste the data (a TaleSpire slab or a JSON string) here, or specify a file name that contains this (and only this) data.\n")
        path_parts = in_data.split("/")
        if (os.path.exists(os.path.join(*path_parts))):
            in_file = open(os.path.join(*path_parts), 'r')
            exec_data['in_data'] = in_file.read()
            in_file.close()
        else:
            exec_data['in_data'] = in_data

        #if (re.fullmatch('^```.*```$|^{.*}$', in_data, flags=re.DOTALL) != None):
        #    exec_data['in_data'] = in_data
        #else:
        #    exec_data['in_file'] = in_data
        if (args.out == None):
            exec_data['out'] = input("Do you also want to store the result in a specific file? If not it will just be displayed at the end of the program execution. Enter the file name you want or leave empty and press enter.\n")
            if (exec_data['out'] == ''):
                exec_data['out'] = None
    else:
        exec_data['in_data'] = get_data(args.in_file, exec_data['in_data'], exec_data['verbose'], exec_data['quiet'])


    #decide whether encode or decode should be chosen if automatic mode was selected
    if (exec_data['mode'] == 'automatic'):
        data = exec_data['in_data'].strip()
        if (re.fullmatch('^```.*```$|H4sI.*', data) != None): # Decode (H4sI seems to always be at the beginning of a slab. Not sure why, probably gzip header or the like) TODO consider only checking for JSON and assume that if it's not JSON it's a slab
            exec_data['mode'] = 'decode'
            print_info("info", "Interpreted input as slab data, setting to decode.", exec_data['verbose'], exec_data['quiet'])
        elif (re.fullmatch('^{.*}$', data, flags=re.DOTALL) != None): #Encode
            exec_data['mode'] = 'encode'
            print_info("info", "Interpreted input as JSON data, setting to encode.", exec_data['verbose'], exec_data['quiet'])
        else:
            print_info("error", "Can't recognize input data as either TaleSpire slab data or JSON! Aborting.", exec_data['verbose'], exec_data['quiet'])
            sys.exit(1)

    if (args.ts_dir == None and exec_data['mode'] == 'encode'):
        if (exec_data['pipeline']):
            exec_data['ts_dir'] = None
        else:
            ts_dir = input("Specify the TaleSpire base directory (absolute path or relative to SlabelFish). Leave empty if no input validation should be done.\n")
            if (assets_reader.verify_TS_dir(ts_dir) and ts_dir != ""):
                exec_data['ts_dir'] = ts_dir
            else:
                exec_data['ts_dir'] = None # Is None the best choice here? If so, is it the best choice for exec_data['out'] a bit later?
    else:
            if (args.ts_dir == ""):
                exec_data['ts_dir'] = None
            else:
                exec_data['ts_dir'] = args.ts_dir
            
    return exec_data

def main():
    arg_parser = argparse.ArgumentParser(description="Decode or Encode TaleSpire slabs to/from JSON", epilog="If no arguments are specified (or some required ones are omitted), SlabelFish will instead launch into interactive mode where the (missing) options are asked via input prompts.")
    
    arg_parser.add_argument('-v', '--verbose', action='store_true', help="Show internal messages while de- or encoding slabs. Useful for debugging or learning the format. Errors will be shown nontheless.")
    arg_parser.add_argument('-q', '--quiet', action='store_true', help="Turn off all internal messages apart from the final conversion result and necessary input prompts. Overrides -v.")
    arg_parser.add_argument('-e', '--encode', action='store_true', help="Specifies that JSON data is provided which is to be encoded into a TaleSpire slab. If this is specified together with -d, SlabelFish will interpret it as -a being set")
    arg_parser.add_argument('-d', '--decode', action='store_true', help="Specifies that TaleSpire slab data is provided which is to be decoded into JSON. If this is specified together with -e, SlabelFish will interpret it as -a being set")
    arg_parser.add_argument('-a', '--automatic', action='store_true', help="Tries to guess based on input data entered --in whether to decode or encode and whether to read the data directly from the argument or if it's stored in a file and the file name was specified.")
    arg_parser.add_argument('-c', '--compact', action='store_true', help="Switches to compact mode, printing JSON output in one line instead of prettified with newlines and indentation. Only has an effect in decoding mode.")
    arg_parser.add_argument('-p', '--pipeline', action='store_true', help="Prevents interactive mode and instead exits with an error if something required is missing.")
    arg_parser.add_argument('--ts_dir', metavar='TS_DIR', help="Specifies the location of the base directory of TaleSpire. If no validity check is wanted, set this parameter to empty string. In pipeline (-p) mode it can also be omitted."); #this will probably need another var that defines how it should act on errors (ignore invalid data or stop and warn on invalid data). could be rolled into other settings like always stop and warn on invalid data in verbose mode and ignore them in quiet mode. Could also be done based on if the argument is specified or not
    arg_parser.add_argument('--in_file', '--if', metavar='IN_FILE', help="Enter a file name for SlabelFish to read the data (TaleSpire slab or JSON string) from. File name can be 'stdin', in which case it reads from sys.stdin later on (Input terminated by newline). Don't specify this and positional argument 'data' at the same time, in case of conflict, positional data will take precedence.")
    arg_parser.add_argument('--out', '--of', metavar='OUT_DATA', help="Enter a file name that serves as output for the final result. Progress output like info messages with -v are still printed on the command line.")
    arg_parser.add_argument('data', metavar='IN_DATA', nargs='?', help="Enter raw input data (TaleSpire slab or JSON string) for conversion. Don't specify this and '--in_file' at the same time, in case of conflict this takes precedence.")
    exec_data = read_arguments(arg_parser.parse_args())

    data = exec_data['in_data']

    # Create output
    out_data = None
    if (exec_data['mode'] == "encode"):
        assets_reader.verify_TS_dir(exec_data['ts_dir'])
        if (exec_data['ts_dir'] != None):
            assets_reader.find_indexes()
            out_data = encoder.encode(data, True, exec_data['verbose'], exec_data['quiet'])
        else:
            out_data = encoder.encode(data, False, exec_data['verbose'], exec_data['quiet'])
    elif (exec_data['mode'] == "decode"):
        out_data = decoder.decode(data, exec_data['verbose'], exec_data['quiet'])
    else:
        print_info("error", "Didn't get a valid mode (encode or decode). Technically this shouldn't be reachable and already be filtered out by previous checks. Aborting")
        sys.exit(1)

    # Write output
    if (exec_data['out'] == None):
        print_info("info_quiet", "\n---\n\nResult:", exec_data['verbose'], exec_data['quiet'])
        if (exec_data['mode'] == 'decode'): # can I do that nicer?
            if (exec_data['compact'] == True):
                print(json.dumps(out_data).strip())
            else:
                print(json.dumps(out_data, indent=2).strip())
        elif (exec_data['mode'] == 'encode'):
            print(out_data.decode().strip())
    else:
        if (exec_data['mode'] == 'decode'): # can I do that nicer?
            out_file = open(exec_data['out'], "w")
            if (exec_data['compact'] == True):
                out_file.write(json.dumps(out_data))
            else:
                out_file.write(json.dumps(out_data, indent=2))
        elif (exec_data['mode'] == 'encode'):
            out_file = open(exec_data['out'], "wb")
            out_file.write(out_data.strip())
        out_file.close()
        
    sys.exit(0)
        
    
if __name__ == '__main__':
    main()
    
