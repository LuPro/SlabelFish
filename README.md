# SlabelFish
A de- and encoder for TaleSpire Slabs.

Currently knows the "Chimera" Slab Format.

Decodes to JSON for human readable editing, can reencode back to the slab binary format (encoder part WIP)

With verbose output the decoding and encoding can be documented which is mostly to better document/explain the process for if developers are working on their own decoder or encoder and the text documentation isn't detailed enough (or to debug their implementation).

## Dependencies
Tested and developed with Python 3.9.6, but just Python >=3 should suffice (not validated)

Depends on whatever Python screams at you when you try to run it, but there aren't any fancy depencies so far, so a default Python install should do. *ToDo: Proper dependency list, see issue #4*

## Usage

### Precompiled

#### Linux

Open a terminal of your choice, navigate to the directory of the executable and run SlabelFish by entering `./slabelfish`. Then follow the instructions (or provide the information as flags beforehand yourself)

See [common usages](#common-usages) for more detailed usage information.

#### Windows

Open a CMD, navigate to the directory of the executable (using `cd`) and enter `slabelfish.exe`. Then follow the instructions (or provide the information as flags beforehand yourself)
File paths follow the Windows standard of using `\` as folder marker.

See [common usages](#common-usages) for more detailed usage information.

### Dev Environment

run
`python slabelfish.py`
for (fully) interactive mode.

See [common usages](#common-usages) and [help](help-text) for further info on command line arguments.

### Common usages
*(All commands can be run from the precompiled executable as well of course)*
*For ease of documentation all examples are provided with `-a` (automatic mode) to let SlabelFish decide whether it needs to decode or encode, if you want to specify, replace this with either `-e` (encode) or `-d` (decode)*

- Pipeline

```bash
python slabelfish.py -aq --in_file="stdin"
```

- Documentation / Tool development
If you want to create your own encoder/decoder, use verbose mode so SlabelFish documents the individual steps of the process in a human readable way to help with understanding the format / debugging your tool.

```bash
python slabelfish.py -av --in_file="your/file/name"
```
(Use backslashes on Windows)

- Storing output to a file.<br>
Sometimes it's more convenient to have the output in a file instead of in stdout

```bash
python slabelfish.py -aq --in_file="cool/in_file/location" --out="out_file_name"
```

- Input data via positional arguments.<br>
When using in your own tool you may want to run SlabelFish with the raw data without needing to hook into stdin or storing it as a file first (positional argument may be limited in length depending on your shell/cmd environment)

```bash
python slabelfish.py -aq --out="some_out_name" POSITIONAL_DATA
```

Where the positional data can be either a raw TS slab, or a JSON representation of one.

### Help text

```bash
python slabelfish.py --help
```

shows help text and usage info. For convenience and documentation purposes the help text is copied to here as well:

```
usage: slabelfish.py [-h] [-v] [-q] [-e] [-d] [-a] [-c] [--ts_dir TS_DIR] [--in_file IN_FILE]
                     [--out OUT_DATA]
                     [IN_DATA]

Decode or Encode TaleSpire slabs to/from JSON

positional arguments:
  IN_DATA            Enter raw input data (TaleSpire slab or JSON string) for conversion. Don't
                     specify this and '--in_file' at the same time, in case of conflict in_file
                     takes precedence.

optional arguments:
  -h, --help         show this help message and exit
  -v, --verbose      Show internal messages while de- or encoding slabs. Useful for debugging or
                     learning the format. Errors will be shown nontheless.
  -q, --quiet        Turn off all internal messages apart from the final conversion result and
                     necessary input prompts. Overrides -v.
  -e, --encode       Specifies that JSON data is provided which is to be encoded into a TaleSpire
                     slab. If this is specified together with -d, SlabelFish will interpret it as -a
                     being set
  -d, --decode       Specifies that TaleSpire slab data is provided which is to be decoded into
                     JSON. If this is specified together with -e, SlabelFish will interpret it as -a
                     being set
  -a, --automatic    Tries to guess based on input data entered --in whether to decode or encode and
                     whether to read the data directly from the argument or if it's stored in a file
                     and the file name was specified.
  -c, --compact      Switches to compact mode, printing JSON output in one line instead of
                     prettified with newlines and indentation. Only has an effect in decoding mode.
  --ts_dir TS_DIR    Specifies the location of the base directory of TaleSpire. Only needed for
                     encoding to ensure valid input data from the JSON. **WIP**
  --in_file IN_FILE  Enter a file name for SlabelFish to read the data (TaleSpire slab or JSON
                     string) from. File name can be 'stdin', in which case it reads from sys.stdin
                     later on (Input terminated by newline). Don't specify this and positional
                     argument 'data' at the same time, in case of conflict, positional data will be
                     discarded.
  --out OUT_DATA     Enter a file name that serves as output for the final result. Progress output
                     like info messages with -v are still printed on the command line.

If no arguments are specified (or some required ones are omitted), SlabelFish will instead launch
into interactive mode where the (missing) options are asked via input prompts.
```
