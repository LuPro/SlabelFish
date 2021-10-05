# SlabelFish
A de- and encoder for TaleSpire Slabs.

Currently knows the "Chimera" Slab Format.

Decodes to JSON for human readable editing, can reencode back to the slab binary format (encoder part WIP)

With verbose output the decoding and encoding can be documented which is mostly to better document/explain the process for if developers are workin on their own decoder or encoder and the text documentation isn't detailed enough (or to debug their implementation).

## Dependencies
Tested and developed with Python 3.9.6, but just Python >=3 should suffice (not validated)

Depends on whatever Python screams at you when you try to run it, but there aren't any fancy depencies so far, so a default Python install should do. *ToDo: Proper dependency list, see issue #4*

## Usage
run
`python slabelfish.py`
for interactive mode.

`python slabelfish.py --help`
shows help text and usage info. For convenience and documentation purposes the help text is copied to here as well:

```
usage: slabelfish.py [-h] [-v] [-q] [-e] [-d] [-a] [-c] [--in_file IN_FILE]
                     [--out OUT_DATA]
                     [IN_DATA]

Decode or Encode TaleSpire slabs to/from JSON

positional arguments:
  IN_DATA            Enter raw input data (TaleSpire slab or JSON string) for
                     conversion. Don't specify this and '--in_file' at the
                     same time, in case of conflict this takes precedence.

optional arguments:
  -h, --help         show this help message and exit
  -v, --verbose      Show internal messages while de- or encoding slabs.
                     Useful for debugging or learning the format. Errors will
                     be shown nontheless.
  -q, --quiet        Turn off all internal messages apart from the final
                     conversion result and necessary input prompts. Overrides
                     -v.
  -e, --encode       Specifies that JSON data is provided which is to be
                     encoded into a TaleSpire slab. If this is specified
                     together with -d, SlabelFish will interpret it as -a
                     being set
  -d, --decode       Specifies that TaleSpire slab data is provided which is
                     to be decoded into JSON. If this is specified together
                     with -e, SlabelFish will interpret it as -a being set
  -a, --automatic    Tries to guess based on input data entered --in whether
                     to decode or encode and whether to read the data directly
                     from the argument or if it's stored in a file and the
                     file name was specified.
  -c, --compact      Switches to compact mode, printing JSON output in one
                     line instead of prettified with newlines and indentation.
                     Only has an effect in decoding mode.
  --in_file IN_FILE  Enter a file name for SlabelFish to read the data
                     (TaleSpire slab or JSON string) from. Don't specify this
                     and positional argument 'data' at the same time, in case
                     of conflict, this will be discarded.
  --out OUT_DATA     Enter a file name that serves as output for the final
                     result. Progress output like info messages with -v are
                     still printed on the command line.

If no arguments are specified (or some required ones are omitted), SlabelFish
will instead launch into interactive mode where the (missing) options are
asked via input prompts.
```
