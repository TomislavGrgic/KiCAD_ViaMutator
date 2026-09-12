import pcbnew
import wx
import os

# WX GUI form that show the plugin progress
class ViaMutatorWindow(wx.Frame):
    SIZE_SCALAR = 1e6

    def __init__(self):
        wx.Dialog.__init__(
            self,
            None,
            id=wx.ID_ANY,
            title=u"Via Mutator",
            pos=wx.DefaultPosition,
            size=wx.DefaultSize,
            style=wx.DEFAULT_DIALOG_STYLE)

        icon = wx.Icon(os.path.join(os.path.dirname(__file__), 'icon.png'))
        self.SetIcon(icon)

        boxSizer = wx.BoxSizer(wx.VERTICAL)
        board = pcbnew.GetBoard()

        #Create list
        self.options = wx.ListBox(self)
        self.fill_options(board)

        #Create value inputs
        self.diameter_in = wx.TextCtrl(self)
        self.drill_in = wx.TextCtrl(self)

        #Create buttons
        self.cancel_btn = wx.Button(self, label="Cancel")
        self.replace_btn = wx.Button(self, label="Replace")

        self.cancel_btn.Bind(wx.EVT_BUTTON, self.on_exit)
        self.replace_btn.Bind(wx.EVT_BUTTON, self.on_replace)

        #display menu
        boxSizer.Add(wx.StaticText(self, label="Select the vias you want to change: "), 0, wx.ALL, 5)
        boxSizer.Add(self.options, 0, wx.ALL, 5)

        boxSizer.Add(wx.StaticText(self, label="Select new values: "), 0, wx.ALL, 5)
        boxDiameter = wx.BoxSizer(wx.HORIZONTAL)
        boxDrill = wx.BoxSizer(wx.HORIZONTAL)

        #Inputs
        boxDiameter.Add(wx.StaticText(self, label="Diameter: "), 0, wx.ALL, 1)
        boxDiameter.Add(self.diameter_in, 0, wx.ALL, 1)
        boxDiameter.Add(wx.StaticText(self, label=" mm"), 0, wx.ALL, 1)
        boxDrill.Add(wx.StaticText(self, label="Drill:    "), 0, wx.ALL, 1)
        boxDrill.Add(self.drill_in, 0, wx.ALL, 1)
        boxDrill.Add(wx.StaticText(self, label=" mm"), 0, wx.ALL, 1)

        boxSizer.Add(boxDiameter, 0, wx.ALL, 5)
        boxSizer.Add(boxDrill, 0, wx.ALL, 5)

        #Buttons tab
        boxButtons = wx.BoxSizer(wx.HORIZONTAL)
        boxButtons.Add(self.cancel_btn, 0, wx.ALL, 5)
        boxButtons.Add(self.replace_btn, 0, wx.ALL, 5)
        
        boxSizer.Add(boxButtons, 0, wx.ALL, 5)

        self.SetSizer(boxSizer)
        self.Layout()
        boxSizer.Fit(self)

        self.Centre(wx.BOTH)


    def on_exit( self, event ):
        self.Close(True)


    def on_replace(self, event):
        board = pcbnew.GetBoard()

        #Change vias
        size = self.options.GetSelection()
        new_diameter = int(self.diameter_in.GetLineText(0)) * self.SIZE_SCALAR
        new_drill = int(self.drill_in.GetLineText(0)) * self.SIZE_SCALAR
        self.replace_vias(board, (new_diameter,new_drill), self.via_sizes[size])

        #Refresh the board and options menu
        self.fill_options(board)
        pcbnew.Refresh()


    def fill_options(self, board):
        #First empty out the list i any items exist. Idk if there is a better way for this
        while self.options.Count != 0:
            self.options.Delete(0)

        self.via_sizes = self.find_all_via_sizes(board)
        for size in self.via_sizes:
            self.options.Append(f"Diameter: {size[0]/self.SIZE_SCALAR} mm, Drill: {size[1]/self.SIZE_SCALAR} mm")


    def replace_vias(self, board, via_size_new, via_size_old) -> int:
        tracks = board.GetTracks()
        diameter_size, drill_size = via_size_new

        count = 0
        for via in tracks:
            if not hasattr(via, "GetViaType"):
                continue

            diameter = via.GetWidth()
            drill = via.GetDrill()

            count += 1

            if (diameter,drill) == via_size_old:
                via.SetWidth(int(diameter_size))
                via.SetDrill(int(drill_size))

        return count


    def find_all_via_sizes(self, board):
        tracks = board.GetTracks()

        via_sizes = []

        for via in tracks:
            if not hasattr(via, "GetViaType"):
                continue

            diameter = via.GetWidth()
            drill = via.GetDrill()

            if (diameter,drill) not in via_sizes:
                via_sizes.append((diameter,drill))

        return via_sizes


class Plugin(pcbnew.ActionPlugin):
    def defaults(self):
        self.name = "Via Mutator"
        self.category = "Via Editing"
        self.description = "Changes via sizes in batches"
        self.show_toolbar_button = True
        self.pcbnew_icon_support = hasattr(self, "show_toolbar_button")
        self.icon_file_name = os.path.join(os.path.dirname(__file__), 'icon.png')
        self.dark_icon_file_name = os.path.join(os.path.dirname(__file__), 'icon.png')

    def Run(self):
        ViaMutatorWindow().Show()

        