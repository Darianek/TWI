import wx
from gui_get_network import *
from gui_bot_detector import *

class MainMenu(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent)

        self.SetSize((350, 300))

        tekst = 'MAIN MENU'
        font = wx.Font(18, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        wx.StaticText(self, -1, tekst, (wx.VERTICAL, 10)).SetFont(font)

        self.btn1 = wx.Button(self, -1, "Get Social Network", (wx.VERTICAL, 100))
        self.btn2 = wx.Button(self, 1, "Bot Detector", (wx.VERTICAL, 135))

class MainForm(wx.Frame):

    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, 'Twitter Analyzer')

        sizer = wx.BoxSizer()
        self.SetSizer(sizer)

        self.main_menu = MainMenu(self)
        sizer.Add(self.main_menu, 1, wx.EXPAND)
        self.main_menu.btn1.Bind(wx.EVT_BUTTON, self.show_get_network)
        self.main_menu.btn2.Bind(wx.EVT_BUTTON, self.show_bot_detector)
        
        self.get_network = GetSocialNetwork(self)
        sizer.Add(self.get_network, 1, wx.EXPAND)
        self.get_network.btn.Bind(wx.EVT_BUTTON, self.show_main_menu)
        self.get_network.Hide()
        
        self.bot_detector = BotDetector(self)
        sizer.Add(self.bot_detector, 1, wx.EXPAND)
        self.bot_detector.btn.Bind(wx.EVT_BUTTON, self.show_main_menu)
        self.bot_detector.Hide()
                
        self.SetSize((350, 300))
        self.Centre()

    def show_main_menu(self, event):
        self.main_menu.Show()
        self.get_network.Hide()
        self.bot_detector.Hide()
        self.Layout()

    def show_get_network(self, event):
        self.get_network.Show()
        self.main_menu.Hide()
        self.Layout()
        
    def show_bot_detector(self, event):
        self.bot_detector.Show()
        self.main_menu.Hide()
        self.Layout()
        


if __name__ == "__main__":
    app = wx.App()
    frame = MainForm()
    frame.Show()
    app.MainLoop()