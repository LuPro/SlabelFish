from utils import *

#feels like not pythonic to have a global variable here
#todo find out file/folder structure and add that to the index.json name
#todo find out if that cryptic folder name is the same for everyone / what it means (UUID for that asset pack?)
indexes = {}

ts_base_dir = ""

#verifies whether the given directory really is a TS directory (folder structure, files within)
#todo: evaluate whether this should even be done or if I shouldn't care and just throw errors when files that are needed are missing
def verify_TS_dir(path):
    global ts_base_dir
    ts_base_dir = path
    return True

#where to search for them?
def find_indexes():
    global ts_base_dir
    if (ts_base_dir == None):
        return

    if (not ts_base_dir.endswith("/")): #todo: properly work on windows/os specific paths
        ts_base_dir += "/"
    #default TS asset pack
    indexes["d71427a1-5535-4fa7-82d7-4ca1e75edbfd"] = load_index_json(ts_base_dir + "Taleweaver/d71427a1-5535-4fa7-82d7-4ca1e75edbfd/index.json")

    #todo find the rest of the asset packs (search through folders - may be a shitty experience if cross platform is wanted, not sure how python handles this

#called by find indexes to load the index data into ram for faster use (to not always need file reads/syscalls for each asset that is checked)
def load_index_json(index_path):
    file = open(index_path, 'r')
    data = file.read()
    return json.loads(data)

def get_asset(uuid):
    global indexes
    global ts_base_dir
    if (ts_base_dir == None):
        return None

    for key in indexes: #iterate through all index files
        for type in indexes[key]: #iterate through all types (tile, prop, creature, music, icon_atlas - consider stopping at "music", doesn't make sense for a slab (at least for now)
            for i in range(len(indexes[key][type])): #iterate through all assets in this type
                if (type == "IconsAtlases" or type == "Music"):
                    break
                if (uuid.lower() == indexes[key][type][i]["Id"]):
                    #inject the asset type into the json for easier use later on
                    asset = indexes[key][type][i]
                    asset["type"] = type
                    return asset
    #print_info("data_warning_quiet", "Tried finding an asset with UUID " + uuid + ", but couldn't find one.")
    return {"Id": uuid, "type": "unknown"}

#deprecated, use get asset and asset["type"] from its return
def get_asset_type(uuid):
    global indexes
    global ts_base_dir
    if (ts_base_dir == None):
        return None

    for key in indexes: #iterate through all index files
        for type in indexes[key]: #iterate through all types (tile, prop, creature, music, icon_atlas - consider stopping at "music", doesn't make sense for a slab (at least for now)
            for i in range(len(indexes[key][type])): #iterate through all assets in this type
                if (uuid.lower() == indexes[key][type][i]):
                    return type
