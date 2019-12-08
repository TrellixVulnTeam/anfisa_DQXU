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

import logging

from app.config.a_config import AnfisaConfig
from .filter_base import FilterBase
from .dtree_parse import ParsedDTree
from .code_works import HtmlPresentation
#===============================================
class CaseStory:
    def __init__(self, parent = None, start = None):
        self.mParent = parent
        self.mPoints = []
        self.mStartPoint  = start

    def getMaster(self):
        if self.mParent is not None:
            return self.mParent.getMaster()
        assert False

    def getLevel(self):
        if self.mParent is None:
            return 0
        return self.mParent.getLevel() + 1

    def _getStartPoint(self):
        return self.mStartPoint

    def _getLastPoint(self):
        if len(self.mPoints) > 0:
            return self.mPoints[-1]
        return self.mStartPoint

    def _addPoint(self, point):
        self.getMaster().regPoint(point)
        self.mPoints.append(point)

    def checkDetermined(self):
        if (len(self.mPoints) == 0
                or self.mPoints[-1].getPointKind() != "Return"):
            return self
        for cond_point in self.mPoints[:-1]:
            if not cond_point.isActive():
                continue
            ret = cond_point.getSubStory().checkDetermined()
            if ret is not None:
                return ret
        return None

#===============================================
class CheckPoint:
    def __init__(self, story, frag, prev_point, point_no):
        self.mStory = story
        self.mFrag = frag
        self.mPointNo = point_no
        self.mPrevPoint = prev_point
        assert self.mFrag.getLevel() == self.mStory.getLevel()
        assert (self.mPrevPoint is None
            or self.mPrevPoint.getPointKind() == "If")

    def getStory(self):
        return self.mStory

    def getLevel(self):
        return self.mStory.getLevel()

    def getPrevPoint(self):
        return self.mPrevPoint

    def getPointKind(self):
        assert False

    def isActive(self):
        return True

    def getPointNo(self):
        return self.mPointNo

    def getDecision(self):
        return self.mFrag.getDecision()

    def getCondData(self):
        return self.mFrag.getCondData()

    def getMarkers(self):
        return self.mFrag.getMarkers()

    def _accumulateConditions(self):
        if self.getPrevPoint() is None:
            return self.mCondition
        assert self.getPrevPoint().getLevel() == self.getLevel()
        return self.getPrevPoint()._accumulateConditions().addOr(
            self.mCondition)

    def actualCondition(self):
        if self.getPrevPoint() is None:
            return self.getStory().getMaster().getCondEnv().getCondAll()
        return self.getPrevPoint()._accumulateConditions().negative()

    def getInfo(self, code_lines):
        return [self.getPointKind(), self.getLevel(),
            self.getDecision(), self.getCondData(),
            self.getCodeFrag(code_lines)]

    def getCodeFrag(self, code_lines):
        line_from, line_to = self.mFrag.getLineDiap()
        return "\n".join(code_lines[line_from - 1: line_to - 1])

#===============================================
class ImportPoint(CheckPoint):
    def __init__(self, story, frag, prev_point, point_no):
        CheckPoint.__init__(self, story, frag, prev_point, point_no)

    def getPointKind(self):
        return "Import"

    def isActive(self):
        return False

#===============================================
class ErrorPoint(CheckPoint):
    def __init__(self, story, frag, point_no):
        CheckPoint.__init__(self, story, frag, None, point_no)

    def getPointKind(self):
        return "Error"

    def isActive(self):
        return False

#===============================================
class TerminalPoint(CheckPoint):
    def __init__(self, story, frag, prev_point, point_no):
        CheckPoint.__init__(self, story, frag, prev_point, point_no)

    def getPointKind(self):
        return "Return"

    def actualCondition(self):
        if self.getPrevPoint() is None:
            return self.getStory().getMaster().getCondEnv().getCondAll()
        if self.getPrevPoint().getLevel() == self.getLevel():
            return self.getPrevPoint()._accumulateConditions().negative()
        return self.getPrevPoint().getAppliedCondition()

#===============================================
class ConditionPoint(CheckPoint):
    def __init__(self, story, frag, prev_point, point_no):
        CheckPoint.__init__(self, story, frag, prev_point, point_no)
        self.mCondition = self.getStory().getMaster().parseCondData(
            self.getCondData())
        self.mSubStory = CaseStory(self.getStory(), self)

    def getPointKind(self):
        return "If"

    def getSubStory(self):
        return self.mSubStory

    def getOwnCondition(self):
        return self.mCondition

    def getAppliedCondition(self):
        return self.actualCondition().addAnd(self.mCondition)

#===============================================
class FilterDTree(FilterBase, CaseStory):
    def __init__(self, cond_env, code, dtree_name = None,
            updated_time = None, updated_from = None):
        FilterBase.__init__(self, cond_env,
            updated_time, updated_from)
        CaseStory.__init__(self)
        parsed = ParsedDTree(cond_env, code)
        self.mCode = parsed.getTreeCode()
        self.mError = parsed.getError()
        self.mHashCode = parsed.getHashCode()
        self.mDTreeName = dtree_name
        self.mPointList = None
        self.mFragments = parsed.getFragments()

        if self.mError is not None:
            msg_text, lineno, offset = parsed.getError()
            logging.error(("Error in tree %s code: (%d:%d) %s\n" %
                (dtree_name if dtree_name else "", lineno, offset, msg_text))
                + "Code:\n======\n"
                + parsed.getTreeCode() + "\n======")

    def isActive(self):
        return self.mPointList is not None

    def activate(self):
        if self.mPointList is not None:
            return
        self.mPointList = []
        prev_point = None
        for instr_no, frag_h in enumerate(self.mFragments):
            if frag_h.getInstrType() == "Error":
                self._addPoint(ErrorPoint(self, frag_h, instr_no))
                continue
            if frag_h.getInstrType() == "Import":
                assert frag_h.getDecision() is None
                self._addPoint(ImportPoint(self,
                    frag_h, prev_point, instr_no))
                for unit_name in frag_h.getImportEntries():
                    assert frag_h.getHashCode() is not None
                    is_ok = self.importUnit(instr_no, unit_name,
                        self.getActualCondition(instr_no),
                        frag_h.getHashCode())
                    assert is_ok
                continue
            if frag_h.getInstrType() == "If":
                assert frag_h.getDecision() is None
                cond_point = ConditionPoint(self,
                    frag_h, prev_point, instr_no)
                self._addPoint(cond_point)
                prev_point = cond_point
                continue
            if frag_h.getInstrType() == "Return":
                assert frag_h.getCondData() is None
                if frag_h.getLevel() != 0:
                    assert frag_h.getLevel() == 1
                    prev_point.getSubStory()._addPoint(
                        TerminalPoint(prev_point.getSubStory(),
                            frag_h, prev_point, instr_no))
                else:
                    self._addPoint(TerminalPoint(self,
                        frag_h, prev_point, instr_no))
                continue
            assert False, "Bad frag type: %s" % frag_h.getInstrType()

    def __len__(self):
        return len(self.mPointList)

    def getSolKind(self):
        return "dtree"

    def noErrors(self):
        return self.mError is None

    def getHashCode(self):
        return self.mHashCode

    def getMaster(self):
        return self

    def getError(self):
        return self.mError

    def getCode(self):
        return self.mCode

    def getDTreeName(self):
        return self.mDTreeName

    def regPoint(self, point):
        assert point.getPointNo() == len(self.mPointList)
        self.mPointList.append(point)

    def pointNotActive(self, point_no):
        return not self.mPointList[point_no].isActive()

    def getActualCondition(self, point_no):
        return self.mPointList[point_no].actualCondition()

    def checkZeroAfter(self, point_no):
        return self.mPointList[point_no].getPointKind() == "If"

    def reportInfo(self):
        marker_seq = []
        marker_dict = {}
        for point in self.mPointList:
            cond_seq = []
            for mark_idx, mark_info in enumerate(point.getMarkers()):
                cond_data, cond_loc = mark_info
                marker_seq.append((point.getPointNo(), mark_idx, cond_loc))
                cond_seq.append(cond_data)
            if len(cond_seq) > 0:
                marker_dict[point.getPointNo()] = cond_seq
        html_lines = self._decorCode(marker_seq)
        ret_handle = {
            "points": [point.getInfo(html_lines) for point in self.mPointList],
            "markers": marker_dict,
            "code": self.mCode,
            "hash": self.mHashCode,
            "error": self.mError is not None}
        if self.mDTreeName:
            ret_handle["dtree-name"] = self.mDTreeName
        return ret_handle

    def _decorCode(self, marker_seq = None):
        code_lines = self.mCode.splitlines()
        html_lines = []
        cur_diap = None

        for frag_h in self.mFragments:
            if frag_h.getInstrType() == "Error":
                if cur_diap is not None:
                    html_lines += HtmlPresentation.decorProperCode(
                        code_lines, cur_diap, marker_seq)
                    cur_diap = None
                html_lines += HtmlPresentation.presentErrorCode(
                    code_lines, frag_h.getLineDiap(), frag_h.getErrorInfo())
            else:
                if cur_diap is None:
                    cur_diap = frag_h.getLineDiap()
                else:
                    cur_diap = [cur_diap[0], frag_h.getLineDiap()[1]]
        if cur_diap is not None:
            html_lines += HtmlPresentation.decorProperCode(
                        code_lines, cur_diap, marker_seq)
        return html_lines

    def collectRecSeq(self, dataset):
        max_ws_size = AnfisaConfig.configOption("max.ws.size")
        html_lines = self._decorCode()
        ret = set()
        info_seq = []
        for point in self.mPointList:
            info_seq.append([point.getCodeFrag(html_lines), None, None])
            if not point.isActive:
                continue
            condition = point.actualCondition()
            point_count = dataset.evalTotalCount(condition)
            info_seq[-1][1] = point_count
            if point.getPointKind() == "Return":
                info_seq[-1][2] = point.getDecision()
            if point.getDecision() is True:
                assert point.getPointKind() == "Return"
                assert point_count < max_ws_size
                if point_count > 0:
                    seq = dataset.evalRecSeq(condition, point_count)
                    ret |= set(seq)
            assert len(ret) < max_ws_size
        return sorted(ret), info_seq
