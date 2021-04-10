import wx
import twitter_get_user_data as tgud

class GetSocialNetwork(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        tekst = 'Get Social Network'
        font = wx.Font(18, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        wx.StaticText(self, -1, tekst, (wx.VERTICAL, 10)).SetFont(font)
                
        self.lblname = wx.StaticText(self, -1, "Enter username:", pos=(wx.VERTICAL, 80))
        self.screen_name = wx.TextCtrl(self, -1, "", pos=(120, 75))
    

        wx.StaticText(self, -1, "Enter deepth:", pos=(wx.VERTICAL, 120))
        self.deepth = wx.TextCtrl(self, -1, "", pos=(100, 115))


        self.okbtn = wx.Button(self, -1, "OK", (wx.VERTICAL, 170))
        self.Bind(wx.EVT_BUTTON, self.Oker, self.okbtn)
        self.btn = wx.Button(self, -1, "Go back", (wx.VERTICAL, 220))
        
    def Oker(self, event):
        screen_name = self.screen_name.GetValue()
        deepth = int(self.deepth.GetValue())
        
        btn = event.GetEventObject()
        btn.Disable()
        
        tgud.create_graph(screen_name, deepth)
        
        btn.Enable()