# Started 1/19/18 as a replacement for the Qt GUI. Originally authored by
# Josh Carey
# joshuacarey@umass.edu
# Some miscellaneous notes:
# (1) The instrument server persists regardless of the GUI. So you can close
# and open it as much as you want and it should reconnect.
# (2) You need to start the instrument server before the GUI.
# TODO add instrument addition window.
# TODO work on generalized type checking, not just for a couple select types.
# TODO consider adding default values for parameters.
# TODO list of parameters that are irrelevant and should not be checked.
# TODO Fix bad window path issue for spyder.
# TODO fix coordinate system for right justification.
import objectsharer as objsh
# Tkinter is the native python GUI framework. Should be easier than Qt. Also
# no version upgrade issues.
import Tkinter as tk
# ttk provides the means to make the instrument tabs in the GUI. Also provides
# some other themed widgets.
import ttk as ttk

### NOTABLE CONSTANTS ###
# **************************#
# The time that the GUI will draw all the widgets again.
draw_time = 900  # in ms

refresh_continuously = True
fetch_time = 0.5  # in s
# This constant is used to resize the widgets to get them to take up all of
# the available space in the parent window.
fill_all = tk.N + tk.S + tk.W + tk.E
# The number of decimal points used in the parameter value display box,
# when the value in written in scientific notation.
precision = 5

# This is dictionary of colors to use to color the borders in the groups of
# parameters. Purely an aesthetic addition.
color_dict = {'red': '#ff0000', 'blue': '#0066ff', 'yellow': '#ffff00',
              'green': '#00cc00', 'pink': '#ff9999', 'white': '#ffffff',
              'violet': '#cc6699', 'orange': '#FFA500'}

# Initialize the ZeroMQ server backend and connect to the instrument server.
# The instr object will hold all the necessary information for interacting
# with the instrument server, and thus the physical hardware. The server
# always sits on the same address at the same port.
new_backend = objsh.ZMQBackend()
new_backend.start_server("127.0.0.1")
new_backend.connect_to("tcp://127.0.0.1:55555")
# The initial fetch of the instruments.
instr = objsh.helper.find_object('instruments')
# The root window. This is the top level object; its the only object with no
# so called parent widget. This is where the main information display will be.
root_window = tk.Tk()
root_window.title('QRLab')
import ctypes

user32 = ctypes.windll.user32
resolution_x = user32.GetSystemMetrics(0)
resolution_y = user32.GetSystemMetrics(1)
root_window.maxsize(width=resolution_x - 70, height=resolution_y - 70)
root_window.minsize(width=resolution_x - 70, height=resolution_y - 70)


def window_close(*args):
    root_window.destroy()


# Press ctrl-w to close the window.
root_window.bind('<Control-w>', window_close)
root_window.bind('<Control-q>', window_close)

tabs = ttk.Notebook(root_window)


# If create_instruments had a problem running, or the instrument server had
# some other issue, nothing will show up, because there are no instruments.
# The statement below makes sure that won't happen.

# A class for a custom exception to handle if the instrument server did not
# get initialized correctly.
class NoInstrumentsException(Exception):
    pass


def fetch_instruments():
    '''
    Fetches the instruments and returns them in a nice list.
    :return:
    '''
    instr = objsh.helper.find_object('instruments')
    return [x for x in instr.list_instruments() if 'temp' not in x]


# A list with the names of the currently active instruments as entries.
list_of_instruments = fetch_instruments()
if list_of_instruments == []:
    message = 'Error: the instrument server has no instruments. Was there an ' \
              'issue in creating instruments?'
    raise NoInstrumentsException(message)


def remove_widget(widget):
    widget.pack_forget()


class InstrumentInputItem():
    """
    The subassembly of instrument label, value display, Get box, Set box,
    get button, and set button.
    """

    def __init__(self, frame, key, name_value_dict, instrument_name):
        """
        :param frame: The Tkinter frame in which to draw the object.
        :param key: The parameter that an instrument uses, i.e. power,
        frequency, channels, etc.
        :param name_value_dict: A dict containing the parameter names
                as keys and the actual values as entries.
        :param instrument_name: The instrument name.
        """
        self.frame = frame
        self.key = key
        self.instrument_name = instrument_name
        self.label = tk.Label(self.frame, text=key)
        tk.Grid.rowconfigure(self.frame, 0, weight=1)
        tk.Grid.columnconfigure(self.frame, 0, weight=1)
        self.label.grid(row=1, column=1, sticky=fill_all)
        self.option_dict = instr[self.instrument_name].get_shared_parameters()
        # Some parameters are special. They are quantized, in that they can
        # have only a small set of values. Some of these values can be
        # represented by a dropdown menu. Others define a mapping between
        # what to show the user and what to pass to the instrument. The
        # conditions below handle these cases.
        self.option_condition = 'option_list' in self.option_dict[key]
        self.format_map_condition = 'format_map' in self.option_dict[key]
        if self.format_map_condition:
            self.format_map = self.option_dict[key]['format_map']
        if self.option_condition or self.format_map_condition:
            if self.option_condition:
                dropdown_options = self.option_dict[key]['option_list']
            if self.format_map_condition:
                dropdown_options = self.format_map.values()
            self.valuevar = tk.StringVar(self.frame)
            self.setvar = tk.StringVar(self.frame)
            # When the GUI first starts, set all of the parameters to the
            # values already present in the instrument server.
            self.valuevar.set(str(instr[self.instrument_name].get(self.key)))
            self.setvar.set(str(instr[self.instrument_name].get(self.key)))

            self.drop_down_box = tk.OptionMenu(self.frame, self.valuevar,
                                               *dropdown_options)
            self.drop_down_box.config(bg='#d0d0d1')

            self.drop_down_box.grid(row=1, column=2, sticky=fill_all)
            self.drop_down_box_set = tk.OptionMenu(self.frame, self.setvar,
                                                   *dropdown_options)
            self.drop_down_box_set.grid(row=1, column=3, sticky=fill_all)
        else:
            self.parameter_value_box = tk.Entry(self.frame, bg='#d0d0d1')
            self.parameter_value_box.insert(0, str(name_value_dict[key]))
            self.parameter_value_box.grid(row=1, column=2)
            self.set_box = tk.Entry(self.frame)
            self.set_box.insert(0, str(name_value_dict[key]))
            self.set_box.bind('<Return>', self.SetParameter)
            self.set_box.grid(row=1, column=3, sticky=fill_all)

        self.get_button = tk.Button(self.frame, text='Get',
                                    command=self.GetParameter)
        self.get_button.grid(row=1, column=4)
        self.set_button = tk.Button(self.frame, text='Set',
                                    command=self.SetParameter)
        self.set_button.grid(row=1, column=5, sticky=fill_all)
        self.hide_button = tk.Button(self.frame, text='HIDE',
                                     command=self.hide_all,
                                     bg='#FF3030', fg='white')
        self.hide_button.grid(row=1, column=6, sticky=fill_all)

    # Hides the instrument info assembly of widgets.
    def hide_all(self):
        self.get_button.grid_forget()
        self.set_button.grid_forget()
        if self.option_condition:
            self.drop_down_box.grid_forget()
            self.drop_down_box_set.grid_forget()
        else:
            self.parameter_value_box.grid_forget()
            self.set_box.grid_forget()
        self.hide_button.config(text='SHOW', command=self.regrid, bg='#4651FC',
                                fg='white')

    # Makes all of the widget elements reappear.
    def regrid(self):
        self.get_button.grid(row=1, column=4)
        self.set_button.grid(row=1, column=5, sticky=fill_all)
        if self.option_condition:
            self.drop_down_box.grid(row=1, column=2, sticky=fill_all)
            self.drop_down_box_set.grid(row=1, column=3, sticky=fill_all)
        else:
            self.parameter_value_box.grid(row=1, column=2)
            self.set_box.grid(row=1, column=3, sticky=fill_all)
        self.hide_button.config(text='HIDE', command=self.hide_all,
                                bg='#FF3030', fg='white')

    def GetParameter(self):
        """
        Fetches the value from the instrument server and displays that
        information in the text field.
        :return:
        """
        try:
            param = instr[self.instrument_name].get(self.key)
        except objsh.TimeoutError as err:
            print 'The instrument server has now timed out'
            param = None
        if self.option_condition:
            self.valuevar.set(str(param))
        if self.format_map_condition:
            self.valuevar.set(str(self.format_map[param]))
        if not self.format_map_condition and not self.option_condition:
            self.parameter_value_box.delete(0, 'end')
            try:
                number_conditions = (abs(param) > 100) or (param < 0.01)
            except TypeError:
                number_conditions = False
            if ((type(param) is float) or (
                    type(param) is int)) and number_conditions:
                # Format the parameter into scientific notation,
                # with variable number of decimal points.
                param = ('%.' + str(precision) + 'E') % param
            self.parameter_value_box.insert(0, str(param))

    def SetParameter(self, *args):
        """
        This function sets the parameter (obviously). The bind statement
        above keeps trying to pass 2 arguments to this function, while the
        set button only wants to pass 1 (the class reference self). The args
        capture this second argument and then promptly throws it away.
        :param args:
        :return:
        """
        if self.option_condition: 
            new_value = self.setvar.get()
        if self.format_map_condition:
            new_value = self.setvar.get()
            for i in self.format_map.keys():
                if self.format_map[i] == new_value:
                    new_value = i
        if (not self.option_condition) and (not self.format_map_condition):
            new_value = self.set_box.get()
        # Do some type conversion, to make sure the server gets passed the
        # correct type of value. Looking over the instrument plugins,
        # these seems to be the most used types.
        parameter_type = self.option_dict[self.key]['type']
        if new_value[0:3] == 'P: ':
            new_value = eval(new_value[3:])
        print type(parameter_type)
        if parameter_type == type('string'):
            new_value = str(new_value)
        if parameter_type == type(3):
            new_value = int(new_value)
        if parameter_type == type(1.0):
            new_value = float(new_value)
        if parameter_type == type(1 + 1j):
            new_value = complex(new_value)
        if parameter_type == type(True):
            if new_value == 'True':
                new_value = True
            if new_value == 'False':
                new_value = False
        instr[self.instrument_name].set(self.key, new_value)


class InstrumentInformationDisplayFrame():
    """
    This is the frame the contains all of the information about the instrument;
    Its the thing that gets added to the tab in the actual GUI.
    """

    def __init__(self, win, instrument_name, add=True):
        # self.full_information_dict = instr[
        #   instrument_name].get_shared_parameters()
        self.instrument_name = instrument_name
        self.add = add
        self.frame = tk.Frame(root_window)
        tk.Grid.rowconfigure(self.frame, 0, weight=1)
        tk.Grid.columnconfigure(self.frame, 0, weight=1)
        self.refresh_button = tk.Button(self.frame, text=u"\U0001F5D8",
                                        command=self.refresh_all_parameters)
        # u"\U0001F5D8" is the unicode string that represents a sort of refresh
        #  symbol. This label could have been any other character or phrase;
        # it was purely an aesthetic choice.
        instrument_label = tk.Label(self.frame, text=
        "Displayed instrument: " + instrument_name)
        instrument_label.pack()
        self.refresh_button.pack()
        self.scrollbar = tk.Scrollbar(self.frame, orient=tk.VERTICAL)
        self.canvas = tk.Canvas(self.frame, yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.canvas.yview)
        name_value_dict = instr[instrument_name].get_parameter_values()
        self.fields = {}

        self.sorted_instrument_keys = instr[
            instrument_name].get_shared_parameters().keys()
        self.sorted_instrument_keys.sort()
        # The fake frame doesn't contain anything. Its used as padding so the
        # first and last fields don't get cut off.
        self.fake_frame = tk.Frame(root_window)
        self.total_information_dict = instr[
            self.instrument_name].get_shared_parameters()
        self.canvas.create_window(0, 0,
                                  window=self.fake_frame,
                                  anchor=tk.W)
        self.grouped_parameters = filter(lambda x:
                                         'gui_group' in
                                         self.total_information_dict[x],
                                         self.sorted_instrument_keys)
        self.misc_parameters = set(self.sorted_instrument_keys) - set(
            self.grouped_parameters)
        self.groups = [self.total_information_dict[x]['gui_group'] for x
                       in self.grouped_parameters]
        self.groups = set(sorted(self.groups, key=lambda x: x[1]))
        self.name_and_value_frame = tk.LabelFrame(self.canvas)
        self.name_and_value_frame.pack(fill=tk.BOTH, expand=1)
        self.organized_dict = {}
        # for group in self.groups:
        #     result = []
        #     for parameter in self.grouped_parameters:
        #         if self.total_information_dict[parameter]['gui_group'] is
        # group:
        #             result.append(parameter)
        #     self.organized_dict[group] = result

        self.grouped_frames = [(group_name, tk.LabelFrame(
            self.name_and_value_frame, text=str(group_name), background=
            color_dict[
                key]))
                               for
                               group_name, key in
                               zip(self.groups, color_dict)]
        self.misc_frame = tk.LabelFrame(self.name_and_value_frame, text=
        'Miscellaneous')
        for parameter in self.grouped_parameters:
            for frame in self.grouped_frames:
                if self.total_information_dict[parameter]['gui_group'] is \
                        frame[0]:
                    self.temp_frame = tk.Frame(frame[1])
                    self.hide_button = tk.Button(self.temp_frame, text=
                    'Hide Group', command=lambda:
                    self.hide_parameter_group(frame[1], self.hide_button))
                    item = InstrumentInputItem(self.temp_frame, parameter,
                                               name_value_dict, instrument_name)
                    self.fields[parameter] = item
                    self.temp_frame.pack(fill=tk.BOTH, expand=1, anchor=
                    tk.E)
            # self.hide_button.grid()


        for index, frame in enumerate(self.grouped_frames):
            frame[1].pack(fill=tk.BOTH, expand=1)
        for entry in self.misc_parameters:
            self.dumb_frame = tk.Frame(self.misc_frame)
            item = InstrumentInputItem(self.dumb_frame, entry,
                                       name_value_dict, instrument_name)
            self.fields[entry] = item
            self.dumb_frame.pack(fill=tk.BOTH, expand=1)
        self.misc_frame.pack(fill=tk.BOTH, expand=1)
        #     f = self.canvas.create_window(0, 0,
        #                                   window=self.name_and_value_frame,
        #                                   anchor=tk.W)
        #
        #     # To move things aronud on the canvas, use the coords method with
        #     #  new coordinates.
        #     self.canvas.coords(f, 0, 40 + i * 35)
        # for frame, index in zip(self.grouped_frames, range(0,
        #                                                    len(
        # self.grouped_frames))):
        #     thing = self.canvas.create_window(0, 0, window = frame[1],
        #                                       anchor = tk.W)
        #     self.canvas.coords(thing, 0, 40+index*35)
        thing = self.canvas.create_window(0, 0,
                                          window=self.name_and_value_frame,
                                          anchor=tk.W)
        self.canvas.coords(thing, 0, 400)

        # for i, key in enumerate(self.sorted_instrument_keys):
        #     try:
        #         self.group_selection = instr[
        #             self.instrument_name].get_shared_parameters()[key][
        #             'gui_group']
        #     except KeyError:
        #         self.group_selection = 'misc'
        #     if self.group_selection is 'always':
        #         self.always_group_frame = tk.Frame(self.name_and_value_frame)
        #         self.always_label = tk.Label(self.always_group_frame, text=
        #         'Always group')
        #
        #         item = InstrumentInputItem(self.always_group_frame, key,
        #                                    name_value_dict, instrument_name)
        #         self.always_group_frame.pack()
        #     if self.group_selection is 'misc':
        #         self.misc_group_frame = tk.Frame(self.name_and_value_frame)
        #         self.misc_label = tk.Label(self.misc_group_frame, text=
        #         "Miscellaneous parameters")
        #         item = InstrumentInputItem(self.misc_group_frame, key,
        #                                    name_value_dict, instrument_name)
        #         # self.misc_label.pack()
        #
        #         self.misc_group_frame.pack()
        #     else:
        #         self.other_frame = tk.Frame(self.name_and_value_frame)
        #         self.other_label = tk.Label(self.other_frame, text=str(
        #             self.group_selection))
        #         item = InstrumentInputItem(self.other_frame, key,
        #                                    name_value_dict, instrument_name)
        #
        #         # self.other_label.pack()
        #         self.other_frame.pack()
        #
        #     self.fields[key] = item
        #     f = self.canvas.create_window(0, 0,
        #                                   window=self.name_and_value_frame,
        #                                   anchor=tk.W)
        #
        #     # To move things aronud on the canvas, use the coords method with
        #     #  new coordinates.
        #     self.canvas.coords(f, 0, 40 + i * 35)

        t = self.canvas.create_window(0, 0,
                                      window=self.fake_frame,
                                      anchor=tk.W)
        # self.canvas.coords(t, 0, 40 + (i + 1) * 35)
        # Note: to get the scrollbar to work, its necessary to put the
        # frame on the canvas. To do this and make the scrollbar work,
        # you need to use the create_window. You cannot just pack it.
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))
        self.canvas.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas.pack(pady=10, ipady=0, fill=tk.BOTH, expand=1)
        self.frame.pack()
        if self.add is True:
            tabs.add(self.frame, text=instrument_name)

    def refresh_all_parameters(self):
        for item in self.fields:
            self.fields[item].GetParameter()

    def mouse_scroll(self, event):
        self.canvas.yview_scroll(-1 * (event.delta / 120), "units")

    def hide_parameter_group(self, frame, button_object):
        frame.pack_forget()
        button_object.config(text = 'Show Group', command = lambda:
        self.show_parameter_group(frame, button_object))

    def show_parameter_group(self, frame, button_object):
        frame.pack()
        button_object.config(text = 'Hide Group', command = lambda:
        self.hide_parameter_group(frame, button_object))


def produce_initial_display_dictionary():
    list_of_instruments = fetch_instruments()
    display_window = {}
    for instrument in list_of_instruments:
        display_window[instrument] = InstrumentInformationDisplayFrame(
            root_window,
            instrument, add=True)
    return display_window


display_window = produce_initial_display_dictionary()

tabs.pack(expand=1, fill='both')


class ContinuousRefreshFunction(object):
    '''
    The reason for this class is that tkinter wants a function as a parameter
    for the after function. I want to do something that requires preserving
    state across function calls, so I can use a class and essentially
    fake being a function, with the __call__ magic method. It works because
    tkinter only calls the function, and doesn't check what kind of object it
    is.
    '''

    def __init__(self, initializing_instruments, window):
        self.instruments = initializing_instruments
        self.display_window = window

    def __call__(self):
        new_instruments = fetch_instruments()
        if new_instruments != self.instruments:
            diff_instruments = list(
                set(new_instruments) - set(self.instruments))
            for i in diff_instruments:
                self.display_window[i] = InstrumentInformationDisplayFrame(
                    root_window, i, add=True)
            self.instruments = new_instruments

        for instrument in self.instruments:
            # Need to refetch the instruments so that the window will
            # display new
            # instruments.
            self.display_window[instrument].refresh_all_parameters()
            # The after function takes the run time, the function to be run,
            # and its arguments.
        root_window.after(draw_time, self.__call__)


refresh_function_instance = ContinuousRefreshFunction(list_of_instruments,
                                                      display_window)
# I have to set this value to get this scheme to work with Tkinter. I'm not
# sure why, or what it even does.
refresh_function_instance.__name__ = 'LOL'

#
# def continuous_refresh(display_dict, instruments_in_list_form):
#     """
#     This function refreshes every single parameter for every single
#     instrument. Its structured with the after statements so that it runs
#     while the main window of the GUI is running.
#     :param display_dict: A dict where the keys are the names of the
#     instruments and the items are the InstrumentInputItem objects, which
#     each have a refresh all parameters attribute function.
#     :param instruments_in_list_form: A list of all the active instruments.
#     :return:
#     """
#     new_instruments = fetch_instruments()
#     if new_instruments != stack[-1]:
#         new_instruments = instruments_in_list_form
#         stack.append(new_instruments)
#         display_dict = produce_display_dictionary()
#     for instrument in instruments_in_list_form:
#         # Need to refetch the instruments so that the window will display new
#         # instruments.
#         display_dict[instrument].refresh_all_parameters()
#         # The after function takes the run time, the function to be run,
#         # and its arguments.
#     root_window.after(draw_time, continuous_refresh, display_window,
#                       instruments_in_list_form)


if refresh_continuously:
    root_window.after(draw_time, refresh_function_instance)
root_window.mainloop()
