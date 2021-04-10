import wx
from user_bot_detector_ann import ann_predict_bot
from user_bot_detector_decision_trees import dt_pretict_bot
from twitter_get_user import *


class BotDetector(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        tekst = 'Bot Detector'
        font = wx.Font(18, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        wx.StaticText(self, -1, tekst, (wx.VERTICAL, 10)).SetFont(font)

        self.screen_name = ''

        self.cb1 = wx.CheckBox(self, label='Single user:', pos=(0, 55))
        self.screen_name1 = wx.TextCtrl(self, -1, '', pos=(106, 50))
         
        
        self.btn1 = wx.Button(self, -1, "Decision Trees", (wx.VERTICAL, 130))
        self.Bind(wx.EVT_BUTTON, self.Oker, self.btn1)

        self.btn2 = wx.Button(self, -1, "ANN", (121, 130))
        self.Bind(wx.EVT_BUTTON, self.Oker, self.btn2)
        
        self.btn = wx.Button(self, -1, "Go back", (wx.VERTICAL, 220))
        
    def Oker(self, event):
        
        cb = event.GetEventObject() 
        if self.cb1.GetValue():
            screen_name = self.screen_name1.GetValue()
            
        option = cb.GetLabel()
        
        btn = event.GetEventObject()
        btn.Disable()
                
        wait = wx.BusyInfo("Please wait, working...")
        
        prediction = True
        
        if option == 'ANN':
            prediction = ann_predict_bot(screen_name)
        elif option == 'Decision Trees':
            prediction = dt_pretict_bot(screen_name)
  
        if prediction == 1:
            message = 'User is bot'
        else:
            message = 'User is normal'
        
        del wait
        dlg = wx.MessageDialog(self, message, style=wx.OK|wx.CENTRE|wx.ICON_NONE)
        dlg.SetOKLabel('OK')
        dlg.ShowModal()
        btn.Enable()
                    