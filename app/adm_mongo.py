#  Copyright (c) 2019. Partners HealthCare and other members of
#  Forome Association
#
#  Developed by Sergey Trifonov based on contributions by Joel Krier,
#  Michael Bouzinier, Shamil Sunyaev and other members of Division of
#  Genetics, Brigham and Women's Hospital
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
import sys, json, re, traceback
from argparse import ArgumentParser
from pymongo import MongoClient
#=====================================
parser = ArgumentParser()
parser.add_argument("-c", "--config", default = "./anfisa.json",
    help = "Anfisa config file")
parser.add_argument("-a", "--aspects", default = "FDT",
    help = "Aspects: All/Filter/Dtree/Panels/Tags/Info")
parser.add_argument("--pretty", action = "store_true",
    help = "Pretty JSON print")
parser.add_argument("--dry", action = "store_true",
    help = "Dry run: just report instead of data change")
parser.add_argument("-m", "--mode", default = "list",
    help="Command: list/dump/restore/drop/GeneDb/upgrade-a")
parser.add_argument("datasets", nargs = "*",
    help = "Dataset names or pattern with '*'")
run_args = parser.parse_args()

#===============================================
sAspectMap = {
    "I": "dsinfo",
    "F": "filter",
    "P": "panel.Symbol",
    "D": "dtree",
    "T": "tags"
}

#===============================================
class NameFilter:
    def __init__(self, datasets):
        self.mNameSet = set()
        self.mRegExps = []
        if len(datasets) == 0:
            self._addRegex('*')
        else:
            for ds_nm in datasets:
                if '*' in ds_nm:
                    self._addRegex(ds_nm)
                else:
                    self.mNameSet.add(ds_nm)

    def _addRegex(self, ds_nm_patt):
        assert '*' in ds_nm_patt, "Regex w/o star pattern: " + ds_nm_patt
        chunks = [re.escape(chunk) for chunk in ds_nm_patt.split('*')]
        self.mRegExps.append(re.compile(r'\b' + '.*'.join(chunks) + r'\b'))

    def filterName(self, ds_name):
        if ds_name in self.mNameSet:
            return True
        for patt in self.mRegExps:
            if patt.match(ds_name):
                return True
        return False

    def filterNames(self, ds_list):
        ret = []
        for ds_name in ds_list:
            if self.filterName(ds_name):
                ret.append(ds_name)
        return ret

def presentation(obj, pretty_mode):
    if pretty_mode:
        return json.dumps(obj,
            indent = 4, sort_keys = True, ensure_ascii = False)
    return json.dumps(obj, ensure_ascii = False)


#===============================================
try:
    with open(run_args.config, "r", encoding = "utf-8") as inp:
        cfg = json.loads(inp.read())
except Exception:
    print("Error in configuration file", run_args.config, file = sys.stderr)
    traceback.print_exc(file = sys.stderr)
    assert False

#===============================================
if run_args.mode == "GeneDb":
    assert len(run_args.datasets) == 1, "DB file name expected as argument"
    mongo_db = MongoClient(
        cfg.get("mongo-host"), cfg.get("mongo-port"))["GeneDb"]
    cnt = 0
    print("Creation GeneDb", file = sys.stderr)
    mongo_db["meta"].drop()
    mongo_db["symbols"].drop()
    with open(run_args.datasets[0], "r", encoding = "utf-8") as inp:
        for line in inp:
            rec = json.loads(line)
            if "meta" in rec:
                mongo_db["meta"].insert_one(rec)
            else:
                cnt += 1
                mongo_db["symbols"].insert_one(rec)
                if cnt % 10000 == 0:
                    print(f"Storing {cnt} records...",
                        end = '\r', file = sys.stderr)
        print(f"\nStored {cnt} records, done", file = sys.stderr)
    sys.exit()

#===============================================
mongo_db = MongoClient(
    cfg.get("mongo-host"), cfg.get("mongo-port"))[cfg["mongo-db"]]

aspects = set()
for asp_code in run_args.aspects:
    if asp_code.upper() == "A":
        aspects = set(sAspectMap.values())
    elif asp_code.upper() in sAspectMap:
        aspects.add(sAspectMap[asp_code.upper()])
    else:
        assert False, ("Bad aspect code: " + asp_code
            + " (All/Info/Filter/Dtree/Panels/Tags)")

assert len(aspects) > 0, (
    "Aspect (All/Info/Filter/Dtree/Panels/Tags) not defined")

print("//Aspects: " + " ".join(sorted(aspects)), file = sys.stderr)

#===============================================
def upgradeIt(it):
    if it["_tp"] == "dsinfo" or "data" in it:
        return None
    fld_name = it["_tp"]
    if fld_name not in it:
        print("Warning strange item:", presentation(it))
        return None
    ret = {"_tp": it["_tp"], "name": it["name"], "data": it[fld_name]}
    for key in ("time", "from", "rubric"):
        if key in it:
            ret[key] = it[key]
    rest_keys = set(it.keys()) - set(ret.keys()) - {"_id", fld_name}
    assert len(rest_keys) == 0, repr(sorted(rest_keys))
    return ret

#===============================================
name_flt = NameFilter(run_args.datasets)

ds_present_set = set()
for coll_name in mongo_db.list_collection_names():
    if coll_name != "system.indexes":
        ds_present_set.add(coll_name)

if run_args.mode == "list":
    print(presentation(name_flt.filterNames(ds_present_set),
        run_args.pretty))
elif run_args.mode == "dump":
    for ds_name in name_flt.filterNames(ds_present_set):
        print(presentation({"_tp": "DS", "name": ds_name}, run_args.pretty))
        for it in mongo_db[ds_name].find():
            if it.get("_tp") in aspects:
                rep_it = dict()
                for name, val in it.items():
                    if name != "_id":
                        rep_it[name] = val
                print(presentation(rep_it, run_args.pretty))
elif run_args.mode == "drop":
    for ds_name in name_flt.filterNames(ds_present_set):
        if len(aspects) == len(sAspectMap):
            print("-> Dataset to drop:\t", ds_name, file = sys.stderr)
            if not run_args.dry:
                mongo_db[ds_name].drop()
        else:
            cnt = 0
            for it in mongo_db[ds_name].find():
                if it.get("_tp") in aspects:
                    cnt += 1
            if cnt == 0:
                print("--> Nothing to drop in:\t", ds_name, file = sys.stderr)
                continue
            print("-> Records to drop in\t", ds_name, "count=", cnt,
                file = sys.stderr)
            if not run_args.dry:
                for asp in aspects:
                    mongo_db[ds_name].delete_many({"_tp": asp})
elif run_args.mode == "restore":
    if len(run_args.datasets) == 0:
        print("-> Restore all information to original place",
            file = sys.stderr)
        ds_name = None
        restore_all = True
    elif len(run_args.datasets) == 1:
        ds_name = run_args.datasets[0]
        print("-> Store information into", ds_name, file = sys.stderr)
        restore_all = False
    else:
        print("== Oops: use either no or one datatset in restore command",
            file = sys.stderr)
        sys.exit()
    ds_count = 0
    rec_count = 0
    for line in sys.stdin:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        it = json.loads(line)
        if it["_tp"] == "DS":
            if rec_count > 0:
                if ds_name is not None:
                    print("-> Added records:", rec_count, file = sys.stderr)
                else:
                    print("->Skipped records:", rec_count, file = sys.stderr)
            rec_count = 0
            if restore_all:
                ds_name = it["name"]
                if not name_flt.filterName(ds_name):
                    ds_name = None
            else:
                if ds_count > 0:
                    print("-> Ignore next data", file = sys.stderr)
                    ds_name = None
            if ds_name:
                print("-> Dataset", ds_name, file = sys.stderr)
            continue
        if it["_tp"] not in aspects:
            continue
        rec_count += 1
        if ds_name is None:
            continue
        if not run_args.dry:
            key_instr = {"_tp": it["_tp"]}
            if "name" in it:
                key_instr["name"] = it["name"]
            mongo_db[ds_name].update_one(
                key_instr, {"$set": it}, upsert = True)
    if rec_count > 0:
        if ds_name is not None:
            print("-> Added records:", rec_count, file = sys.stderr)
        else:
            print("-> Skipped records:", rec_count, file = sys.stderr)
elif run_args.mode == "upgrade-a":
    for ds_name in name_flt.filterNames(ds_present_set):
        print(presentation({"_tp": "DS", "name": ds_name}, run_args.pretty))
        modified = []
        for it in mongo_db[ds_name].find():
            mod_it = upgradeIt(it)
            if mod_it is not None:
                modified.append(mod_it)
        if len(modified) == 0:
            print("= skipped (nothing to upgrade)")
        else:
            for mod_it in modified:
                mongo_db[ds_name].update_one(
                    {"_tp": mod_it["_tp"], "name": mod_it["name"]},
                    {"$set": mod_it})
            print("= upgraded", len(modified), "items")
else:
    print("Oops: command not supported", file = sys.stderr)
