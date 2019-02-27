# -*- coding:utf-8 -*-
import wx
import guiManager as FrameManager

class MainAPP(wx.App):

    def OnInit(self):
        self.manager = FrameManager.GuiManager(self.UpdateUI)
        self.frame = self.manager.GetFrame(0, -1)
        self.frame.Show()
        return True

    def UpdateUI(self, type, member_id):
        self.frame.Show(False)
        self.frame = self.manager.GetFrame(type, member_id)
        self.frame.Show(True)

def main():
    app = MainAPP()
    app.MainLoop()

if __name__ == '__main__':
    main()