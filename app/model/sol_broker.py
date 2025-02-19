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

from forome_tools.sync_obj import SyncronizedObject
from app.config.a_config import AnfisaConfig
from .sol_pack import SolutionPack
from .sol_support import SolutionKindHandler, SolPanelHandler
from .family import FamilyInfo
#===============================================
class SolutionBroker(SyncronizedObject):
    def __init__(self, meta_info, ds_kind,
            derived_mode = False, zygosity_support = True):
        SyncronizedObject.__init__(self)
        self.mDataSchema = meta_info.get("data_schema", "CASE")
        self.mSolPack = SolutionPack.select(self.mDataSchema)
        self.mModes = set()
        self.mModes.add(self.mDataSchema)
        self.mDSKind = ds_kind
        assert self.mDSKind in {"ws", "xl"}
        self.mModes.add(self.mDSKind.upper())

        self.mSolEnv = None
        self.mSolKinds = None
        self.mNamedAttrs = dict()

        reference = meta_info["versions"].get("reference")
        self.mFastaBase = "hg38" if reference and "38" in reference else "hg19"

        if derived_mode:
            self.addModes({"DERIVED"})
        else:
            self.addModes({"PRIMARY"})

        self.mFamilyInfo = FamilyInfo(meta_info)
        self.addModes(self.mFamilyInfo.prepareModes())

        if (1 <= len(self.mFamilyInfo) <= 10 and zygosity_support):
            self.addModes({"ZYG"})
        self.mZygSupport = None

    def getDSKind(self):
        return self.mDSKind

    def getSolEnv(self):
        return self.mSolEnv

    def getDataSchema(self):
        return self.mDataSchema

    def getFamilyInfo(self):
        return self.mFamilyInfo

    def getFastaBase(self):
        return self.mFastaBase

    #===============================================
    def _setupEnv(self, sol_env, sol_makers):
        assert self.mSolEnv is None, "solEnv is already set"
        with self:
            self.mSolEnv = sol_env
            self.mSolKinds = dict()
            for sol_kind in sol_env.getSolKeys():
                kind_h = None
                if sol_kind in sol_makers:
                    kind_h = SolutionKindHandler(self,
                        sol_kind, sol_makers[sol_kind])
                elif sol_kind.startswith("panel."):
                    prefix, ptype = sol_kind.split('.')
                    panels_cfg = AnfisaConfig.configOption("panels.setup")
                    assert ptype in panels_cfg, ("Panel type not supported: " + ptype)
                    kind_h = SolutionKindHandler(self, sol_kind,
                        SolPanelHandler.makeSolEntry,
                        special_name = panels_cfg[ptype].get("special"))
                else:
                    assert sol_kind == "tags", "Bad sol kind: " + sol_kind
                    continue
                self.mSolKinds[sol_kind] = kind_h
            self.mSolEnv.attachBroker(self)

    def deactivate(self):
        if self.mSolEnv is not None:
            self.mSolEnv.detachBroker(self)

    #===============================================
    def addModes(self, modes):
        if modes:
            self.mModes |= set(modes)

    def testRequirements(self, modes):
        if not modes:
            return True
        return len(modes & self.mModes) == len(modes)

    def iterStdItems(self, item_kind):
        for it in self.mSolPack:
            if it["_tp"] == item_kind and self.testRequirements(it.get("req")):
                yield it

    def getStdItemData(self, item_kind, item_name):
        for it in self.iterStdItems(item_kind):
            if it["name"] == item_name:
                return it["data"]
        return None

    def getModes(self):
        return self.mModes

    #===============================================
    def regNamedAttr(self, name, attr_h):
        assert name not in self.mNamedAttrs, "Attribute duplication: " + name
        self.mNamedAttrs[name] = attr_h

    def getNamedAttr(self, name):
        return self.mNamedAttrs[name]

    #===============================================
    def refreshSolEntries(self, kind):
        with self:
            if kind in self.mSolKinds:
                self.mSolKinds[kind].refreshSolEntries()
            elif kind == "tags" and self.getDSKind() == "ws":
                if self.getTagsMan() is not None:
                    self.getTagsMan().refreshTags()

    def iterSolEntries(self, kind):
        sol_kind_h = self.mSolKinds[kind]
        for info in sol_kind_h.getListInfo():
            yield sol_kind_h.pickByName(info["name"])

    def getSpecialSolEntry(self, kind):
        sol_kind_h = self.mSolKinds[kind]
        return sol_kind_h.pickByName(sol_kind_h.getSpecialName())

    def noSolEntries(self, kind):
        return self.mSolKinds[kind].isEmpty()

    def pickSolEntry(self, kind, name):
        return self.mSolKinds[kind].pickByName(name)

    def normalizeSolEntry(self, kind, sol_entry):
        return self.mSolKinds[kind].normalizeSolEntry(sol_entry)

    def modifySolEntry(self, kind, instr, entry_data):
        with self:
            return self.mSolKinds[kind].modifySolEntry(instr, entry_data)

    def getSolEntryList(self, kind):
        return self.mSolKinds[kind].getListInfo()

    #===============================================
    def iterPanels(self, panel_type):
        for it in (self.iterSolEntries("panel." + panel_type)):
            yield (it.getName(), it.getSymList())

    def getPanelList(self, panel_name, panel_type, is_optional = False):
        for pname, names in self.iterPanels(panel_type):
            if pname == panel_name:
                return names
        assert is_optional, f"{panel_type}: Panel {panel_name} not found"
        return None

    def iterSpecialPanels(self):
        for sol_kind in self.mSolEnv.getSolKeys():
            kind_h = self.mSolKinds.get(sol_kind)
            if kind_h is None:
                continue
            special_name = kind_h.getSpecialName()
            if special_name is not None:
                yield kind_h.pickByName(special_name)

    def symbolsToPanels(self, panel_type, symbols):
        symbols = set(symbols)
        ret = []
        for pname, names in self.iterPanels(panel_type):
            if len(symbols & set(names)) > 0:
                ret.append(pname)
        return ret

    #===============================================
    def reportSolutions(self):
        ret = dict()
        for kind in ("filter", "dtree", "zone", "tab-schema", "panel.Symbol"):
            ret[kind] = [it["name"] for it in self.iterStdItems(kind)]
        return ret
