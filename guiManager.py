# -*- coding:utf-8 -*-
import loginFrame
from gui import MyFrame

class GuiManager():
    def __init__(self, UpdateUI):
        self.UpdateUI = UpdateUI
        self.id = -1
        self.frameDict = {} # 用来装载已经创建的Frame对象

    def GetFrame(self, type, member_id):
        frame = self.frameDict.get(type)
        if frame is None:
            frame = self.CreateFrame(type, member_id)
            self.frameDict[type] = frame
            self.frameDict[member_id] = frame

        return frame

    def CreateFrame(self, type, member_id):
        if type == 0:
            return loginFrame.LoginFrame(parent=None, id=type, UpdateUI=self.UpdateUI)
        elif type == 1:
            return MyFrame(member_id)
