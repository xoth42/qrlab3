import json
import os
import sys

# keysightSD1.py lives one level up (instrument_plugins/); insert it so plain import works
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import keysightSD1 as key

"""
Reads compiled-in constants out of each HVI file listed in HVI_INFO.json and
merges them into that file under "modules". Requires real hardware/driver
access (keysightSD1), so run this on the lab PC, not in CI.
"""

HVI_DIR = os.path.dirname(os.path.abspath(__file__))
HVI_INFO_PATH = os.path.join(HVI_DIR, "HVI_INFO.json")

# Constant names to probe for on every module; HVI files don't expose a list
# of their own constants, so we just try known names and keep the ones that
# come back without an error.
KNOWN_CONSTANT_NAMES = ["trigger_period", "nCycles", "nSamples", "period", "delay"]


def read_hvi_modules(hvi_path):
    hvi = key.SD_HVI()
    hvi.open(hvi_path)
    modules = []
    for i in range(hvi.getNumberOfModules()):
        name = hvi.getModuleName(i)
        constants = {}
        for cname in KNOWN_CONSTANT_NAMES:
            err, val = hvi.readIntegerConstantWithIndex(i, cname)
            if err >= 0:
                constants[cname] = val
        modules.append({"name": name, "constants": constants})
    hvi.close()
    return modules


def main(only=None):
    with open(HVI_INFO_PATH) as f:
        info = json.load(f)

    # discover all .HVI files in the directory; add new entries preserving existing sample_rate
    for fname in sorted(os.listdir(HVI_DIR)):
        if not fname.endswith(".HVI"):
            continue
        if fname not in info:
            info[fname] = {"sample_rate": None, "modules": []}

    for hvi_name, entry in info.items():
        if hvi_name.startswith("_"):
            continue
        if only and hvi_name not in only:
            continue
        hvi_path = os.path.join(HVI_DIR, hvi_name)
        if not os.path.exists(hvi_path):
            print(f"skipping {hvi_name}: file not found")
            continue
        print(f"reading {hvi_name} ...")
        try:
            entry["modules"] = read_hvi_modules(hvi_path)
        except Exception as e:
            print(f"  error reading {hvi_name}: {e}")

    with open(HVI_INFO_PATH, "w") as f:
        json.dump(info, f, indent=2)


if __name__ == "__main__":
    # Optional: pass HVI filenames as args to process only those, e.g.:
    #   python build_hvi_info.py 1slot200us.HVI 2slot100us.HVI
    _filter = set(sys.argv[1:]) if len(sys.argv) > 1 else None
    main(_filter)
