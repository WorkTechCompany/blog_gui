#coding=utf-8

import wx
import logging
# 导入wxPython中的通用Button

import xDialog

class LoginFrame(wx.Frame):
    def __init__(self, parent=None, id=-1, UpdateUI=None, account=-1):
        wx.Frame.__init__(self, parent, id, title='登录界面', size=(290, 430), pos=(500, 200))

        self.UpdateUI = UpdateUI
        self.account = account
        self.InitUI() # 绘制UI界面

    def InitUI(self):
        panel = wx.Panel(self)

        # logo_sys = wx.Image(load_image('fo.jpg'), wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        # logo_sys = wx.StaticBitmap(panel,-1,wx.BitmapFromImage('fo.jpg'))
        # logo_sys = wx.Image("fo.png", wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        # wx.StaticBitmap(panel, -1, logo_sys, pos=(90, 90), size=(100, 100))

        logo_title = wx.StaticText(panel, -1, '博客注册工具', pos=(100, 210))
        logo_title.SetForegroundColour('#0a74f7')
        # titleFont = wx.Font(13, wx.DEFAULT, wx.BOLD, wx.NORMAL, True)
        # logo_title.SetFont(titleFont)

        button_Login = wx.Button(panel, -1, '登录', pos=(40, 270), size=(200, 40), style=wx.BORDER_MASK)
        button_Login.SetBackgroundColour('#0a74f7')
        button_Login.SetForegroundColour('white')
        self.Bind(wx.EVT_BUTTON, self.loginSys, button_Login)

    def loginSys(self, event):
        dlg = LoginDialog(self.loginFunction, '#0a74f7')
        dlg.Show()

    def loginFunction(self, account, password, member_id):
        # print('接收到用户的输入：', account, password)
        # logging.info('接收到用户的输入：%s, %s' % (account, password))
        self.UpdateUI(1, member_id) #更新UI-Frame

class LoginDialog(xDialog.InputDialog):
    def __init__(self, func_callBack, themeColor):
        xDialog.InputDialog.__init__(self, '登录系统', func_callBack, themeColor)