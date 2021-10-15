import io
import uuid
import argparse
import re
import sys

from utils import *
import encoder
import decoder
import assets_reader

def read_arguments(args):
    exec_data = {
        'quiet': False,
        'verbose': False,
        'mode': None,
        'in_file': None,
        'in_data': None,
        'out': None,
        'compact': None,
        'ts_dir': None
    }
    
    exec_data['verbose'] = args.verbose
    if (args.quiet == True):
        exec_data['quiet'] = True
        exec_data['verbose'] = False

    exec_data['compact'] = args.compact
    
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

    if (args.ts_dir == None and exec_data['mode'] == 'encode'):
        ts_dir = input("Specify the TaleSpire base directory (absolute path or relative to SlabelFish). Leave empty if no input validation should be done. WIP, NOT IMPLEMENTED YET\n")
        if (assets_reader.verify_TS_dir(ts_dir) and ts_dir != ""):
            exec_data['ts_dir'] = ts_dir
        else:
            exec_data['ts_dir'] = None # Is None the best choice here? If so, is it the best choice for exec_data['out'] a bit later?
                
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
            if (exec_data['out'] == ''):
                exec_data['out'] = None
    else:
        exec_data['in_data'] = args.data
        exec_data['in_file'] = args.in_file
            
    return exec_data

def main():
    arg_parser = argparse.ArgumentParser(description="Decode or Encode TaleSpire slabs to/from JSON", epilog="If no arguments are specified (or some required ones are omitted), SlabelFish will instead launch into interactive mode where the (missing) options are asked via input prompts.")
    
    arg_parser.add_argument('-v', '--verbose', action='store_true', help="Show internal messages while de- or encoding slabs. Useful for debugging or learning the format. Errors will be shown nontheless.")
    arg_parser.add_argument('-q', '--quiet', action='store_true', help="Turn off all internal messages apart from the final conversion result and necessary input prompts. Overrides -v.")
    arg_parser.add_argument('-e', '--encode', action='store_true', help="Specifies that JSON data is provided which is to be encoded into a TaleSpire slab. If this is specified together with -d, SlabelFish will interpret it as -a being set")
    arg_parser.add_argument('-d', '--decode', action='store_true', help="Specifies that TaleSpire slab data is provided which is to be decoded into JSON. If this is specified together with -e, SlabelFish will interpret it as -a being set")
    arg_parser.add_argument('-a', '--automatic', action='store_true', help="Tries to guess based on input data entered --in whether to decode or encode and whether to read the data directly from the argument or if it's stored in a file and the file name was specified.")
    arg_parser.add_argument('-c', '--compact', action='store_true', help="Switches to compact mode, printing JSON output in one line instead of prettified with newlines and indentation. Only has an effect in decoding mode.")
    arg_parser.add_argument('--ts_dir', metavar='TS_DIR', help="Specifies the location of the base directory of TaleSpire. Only needed for encoding to ensure valid input data from the JSON."); #this will probably need another var that defines how it should act on errors (ignore invalid data or stop and warn on invalid data). could be rolled into other settings like always stop and warn on invalid data in verbose mode and ignore them in quiet mode. Could also be done based on if the argument is specified or not
    arg_parser.add_argument('--in_file', metavar='IN_FILE', help="Enter a file name for SlabelFish to read the data (TaleSpire slab or JSON string) from. File name can be 'stdin', in which case it reads from sys.stdin later on (Input terminated by newline). Don't specify this and positional argument 'data' at the same time, in case of conflict, positional data will be discarded.")
    arg_parser.add_argument('--out', metavar='OUT_DATA', help="Enter a file name that serves as output for the final result. Progress output like info messages with -v are still printed on the command line.")
    arg_parser.add_argument('data', metavar='IN_DATA', nargs='?', help="Enter raw input data (TaleSpire slab or JSON string) for conversion. Don't specify this and '--in_file' at the same time, in case of conflict in_file takes precedence.")
    exec_data = read_arguments(arg_parser.parse_args())
    
    # Get data to convert
    data = None
    print_info("info", "Reading input data...", exec_data['verbose'], exec_data['quiet'])
    if (exec_data['in_file'] != None):
        if (exec_data['in_file'] == "stdin"):
            data = input()
        else:
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
        out_data = encoder.encode(data, exec_data['verbose'], exec_data['quiet'])
    elif (exec_data['mode'] == 'decode'):
        out_data = decoder.decode(data, exec_data['verbose'], exec_data['quiet'])
    elif (exec_data['mode'] == 'automatic'):
        #if (re.fullmatch('^```.*```$|^{.*}$', data) != None):
        if (re.fullmatch('^```.*```$', data) != None): # Decode
            exec_data['mode'] = 'decode'
            print_info("info", "Interpreted input as slab data, setting to decode.", exec_data['verbose'], exec_data['quiet'])
            out_data = decoder.decode(data, exec_data['verbose'], exec_data['quiet'])
        elif (re.fullmatch('^{.*}$', data, flags=re.DOTALL) != None): #Encode
            exec_data['mode'] = 'encode'
            print_info("info", "Interpreted input as JSON data, setting to encode.", exec_data['verbose'], exec_data['quiet'])
            out_data = encoder.encode(data, exec_data['verbose'], exec_data['quiet'])
        else:
            print_info("error", "Can't recognize input data as either TaleSpire slab data or JSON! Aborting.", exec_data['verbose'], exec_data['quiet'])
            sys.exit(1)
    else:
        print_info("error", "Encountered an invalid mode (" + exec_data['mode'] + ")!", exec_data['verbose'], exec_data['quiet'])
        sys.exit(1)
        
    if (exec_data['out'] == None):
        print_info("info_quiet", "\n---\n\nResult:", exec_data['verbose'], exec_data['quiet'])
        if (exec_data['mode'] == 'decode'): # can I do that nicer?
            if (exec_data['compact'] == True):
                print_info("info_quiet", json.dumps(out_data), True, False)
            else:
                print_info("info_quiet", json.dumps(out_data, indent=2), True, False)
        elif (exec_data['mode'] == 'encode'):
            print_info("info_quiet", out_data.decode(), True, False)
    else:
        if (exec_data['mode'] == 'decode'): # can I do that nicer?
            out_file = open(exec_data['out'], "w")
            if (exec_data['compact'] == True):
                out_file.write(json.dumps(out_data))
            else:
                out_file.write(json.dumps(out_data, indent=2))
        elif (exec_data['mode'] == 'encode'):
            out_file = open(exec_data['out'], "wb")
            out_file.write(out_data)
        out_file.close()
        
    sys.exit(0)
        
    
if __name__ == '__main__':
    main()
    
