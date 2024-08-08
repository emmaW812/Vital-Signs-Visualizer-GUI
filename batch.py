import tkinter as tk
import customtkinter
from tkinter import ttk
from tkinter import *

import matplotlib
matplotlib.use('TkAgg')

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.cbook as cbook
import matplotlib.pyplot as plt

from mpl_interactions import ioff, panhandler, zoom_factory

import matplotlib.image as mpimg
import mplcursors
import string

import numpy as np
import pandas as pd

class BatchWindow:
    def __init__(self, master, data, x_value, y_values, graph_type, coords):
        self.new_window = tk.Toplevel(master)
        self.new_window.title('Filters')

        self.data = data
        self.x_value = x_value
        self.y_values = y_values
        self.graph_type = graph_type

        self.min = False
        self.max = False

        self.times = self.data[self.x_value].tolist()

        self.timelen = self.data.shape[0]

        self.all_coords = coords

        self.y1 = self.data[self.y_values[0]].tolist()

        try:
            self.y2 = self.data[self.y_values[1]].tolist()
            self.y2_exists = True
        except:
            self.y2_exists = False
            self.y2 = None

        self.scaling = tk.BooleanVar()
        self.sliding = tk.BooleanVar()
        
        self.create_buttons()

    def create_buttons(self):
        # min and max button
        self.minbutton = tk.Button(self.new_window, text="Add start time (sec) >", command=self.create_entry_box_min)
        self.minbutton.pack(pady=10, padx=10)

        self.maxbutton = tk.Button(self.new_window, text="Add end time (sec) >", command=self.create_entry_box_max)
        self.maxbutton.pack(pady=10, padx=10)

        # interval dropdown
        self.select_interval = customtkinter.CTkOptionMenu(self.new_window, values=["Seconds", "Minutes", "Hours", "Days","Weeks","Months","Years"], command=self.interval_selected)
        self.select_interval.pack(pady=10, padx=10)
        self.select_interval.set("Select interval length")

        self.create_tooltip(self.select_interval, "Value will be the average rate throughout the interval duration.\nException: Trajectory map takes the coordinate at the start of each interval.")
        
        # enable x-axis scaling view window by adjusting size button and/or enable x-axis sliding to view earlier/later values button
        self.viewopt_label = Label(self.new_window, text="Select interactive view options")
        self.viewopt_label .pack(pady=5, padx=10)

        self.scaling_checkbutton = Checkbutton(self.new_window, text="Enable x-axis scaling in size of view window", variable=self.scaling, onvalue=True, offvalue=False)
        self.scaling_checkbutton.pack(pady=5, padx=10)

        self.sliding_checkbutton = Checkbutton(self.new_window, text="Enable x-axis sliding of view window", variable=self.sliding, onvalue=True, offvalue=False)
        self.sliding_checkbutton.pack(pady=5, padx=10)

        # create button
        self.createbutton = tk.Button(self.new_window, text="Create", command=self.create_graph)
        self.createbutton.pack(pady=10, padx=10)
    
    def create_tooltip(self, widget, text):
        tooltip = tk.Toplevel(widget)
        tooltip.withdraw()
        tooltip.overrideredirect(True)
        tooltip_label = tk.Label(tooltip, text=text, background="yellow", relief=tk.SOLID, borderwidth=1, padx=2, pady=2)
        tooltip_label.pack()

        def show_tooltip(event):
            tooltip.geometry(f"+{event.x_root+20}+{event.y_root+10}")
            tooltip.deiconify()

        def hide_tooltip(event):
            tooltip.withdraw()

        widget.bind("<Enter>", show_tooltip)
        widget.bind("<Leave>", hide_tooltip)
    
    def interval_selected(self, selected_value):
        self.interval = str(selected_value)

    def create_entry_box_min(self):
        self.min = True
        self.entry_box_min = tk.Entry(self.new_window)
        self.entry_box_min.pack(pady=10, padx=10)
        self.entry_box_min.insert(0, "Entry for min")

    def create_entry_box_max(self):
        self.max = True
        self.entry_box_max = tk.Entry(self.new_window)
        self.entry_box_max.pack(pady=10, padx=10)
        self.entry_box_max.insert(0, "Entry for max")
    
    def get_min_max_values(self):
        #if not specified set min to self.times[0] and max to self.times[-1]
        if self.min and self.max:
            min_value = float(self.entry_box_min.get())
            max_value = float(self.entry_box_max.get())
        elif self.min == True and self.max == False:
            min_value = float(self.entry_box_min.get())
            max_value = self.times[-1]
        elif self.min == False and self.max == True:
            max_value = float(self.entry_box_max.get())
            min_value = self.times[0]
        else:
            #neither
            min_value = self.times[0] + 1
            max_value = self.times[-1] + 1
        print(f"{min_value}, {max_value}")
        return min_value, max_value


    def make_interval_minmax_data(self, interval):
        j_count = 0
        times = []
        y1_avg = []
        y2_avg = [] if self.y2_exists else None
        coords = []

        #var for length of seconds of the interval chosen

        match interval:
            case "Seconds":
                sec_len = 1
            case "Minutes":
                sec_len = 60
            case "Hours":
                sec_len = 3600
            case "Days":
                sec_len == 86400
            case "Weeks":
                sec_len = 604800
            case "Months":
                sec_len = 2419200
            case "Years":
                sec_len = 29030400
        
        #MIN MAX RANGE
        self.min_value, self.max_value = self.get_min_max_values()
        
        #convert self.min and self.max to interval
        self.intmin = round(self.min_value / sec_len, 1)
        self.intmax = round(self.max_value / sec_len, 1)
        
        if self.timelen % sec_len != 0:
            self.timelen -= self.timelen % sec_len
        
        master = int(self.timelen/sec_len)
        #if self.timelen is not divisible by 60 - take out remainder

        for i in range(master):
            times.append(i+1)
            coords.append(self.all_coords[i])
            y1_temp = []
            y2_temp = [] if self.y2_exists else None
            for j in range(sec_len):
                y1_temp.append(self.y1[j + j_count * sec_len])
                if self.y2_exists:
                    y2_temp.append(self.y2[j + j_count * sec_len])
            j_count += 1
            y1_avg.append(np.average(y1_temp))
            if self.y2_exists:
                y2_avg.append(np.average(y2_temp))

        #new lists to store new values
        self.timesfiltered = []
        self.y1_avgfiltered = []
        self.y2_avgfiltered = [] if self.y2_exists else None
        self.coordsfiltered = []

        #convert to seconds
        tsec = [t * sec_len for t in times]

        for i, s in enumerate(tsec):
            if self.min == False and self.max == False:
                self.timesfiltered.append(times[i])
                self.y1_avgfiltered.append(y1_avg[i])
                self.y2_avgfiltered.append(y2_avg[i]) if self.y2_exists else None
                self.coordsfiltered.append(coords[i])
            elif self.min == False:
                if s <= self.max_value: 
                    self.timesfiltered.append(times[i])
                    self.y1_avgfiltered.append(y1_avg[i])
                    self.y2_avgfiltered.append(y2_avg[i]) if self.y2_exists else None
                    self.coordsfiltered.append(coords[i])
            elif self.max == False:
                if s >= self.min_value: 
                    self.timesfiltered.append(times[i])
                    self.y1_avgfiltered.append(y1_avg[i])
                    self.y2_avgfiltered.append(y2_avg[i]) if self.y2_exists else None
                    self.coordsfiltered.append(coords[i])
            else:
                if self.min_value <= s <= self.max_value: 
                    self.timesfiltered.append(times[i])
                    self.y1_avgfiltered.append(y1_avg[i])
                    self.y2_avgfiltered.append(y2_avg[i]) if self.y2_exists else None
                    self.coordsfiltered.append(coords[i])
        #return unfiltered too for scaling
        return self.timesfiltered, self.y1_avgfiltered, self.y2_avgfiltered, self.coordsfiltered,times, y1_avg, y2_avg, coords
        

    def create_line_graph(self, times, y1, y2, y1label, y2label,interval):
        # LINE GRAPH
        line1 = self.ax.plot(times, y1, label=y1label, color='orange', linewidth=2)
        if y2 is not None:
            line2 = self.ax.plot(times, y2, label=y2label, color='magenta', linewidth=2)
            self.ax.set_ylabel('Rates')
        else:
            self.ax.set_ylabel(y1label)
        
        self.ax.set_xlabel(f'Time ({interval})')

        name = self.name_graph(interval,y1label,y2label)
        self.ax.set_title(name)
        
        #create cursor
        if y2 is not None:
            cursor = mplcursors.cursor(line1, hover=mplcursors.HoverMode.Transient)
            cursor = mplcursors.cursor(line2, hover=mplcursors.HoverMode.Transient)
        else:
            cursor = mplcursors.cursor(line1, hover=mplcursors.HoverMode.Transient)

        @cursor.connect("add")
        def on_add(sel):
            line = sel.artist
            x, y = sel.target
            time = x
            sel.annotation.set(
                text=f"{time:.2f}: {y:.2f}", 
                position=(0, 20), 
                anncoords="offset points" 
            )
            sel.annotation.xy = (x, y)

        # Add legend
        self.ax.legend()

    def create_bar_graph(self, times, y1, y2, y1label, y2label,interval):
        bar_width = 0.4
        indices = np.arange(len(times))

        # Adjust positions to avoid overlap
        bars1 = self.ax.bar(indices, y1, bar_width, label=y1label, color='orange')
        if y2 is not None:
            bars2 = self.ax.bar(indices + bar_width, y2, bar_width, label=y2label, color='magenta')
            self.ax.set_ylabel('Rates')
        else:
            self.ax.set_ylabel(y1label)
        
        #set the location of the x ticks and labels
        self.ax.set_xticks(indices + bar_width / 2)
        self.ax.set_xticklabels(times, rotation=45)
        self.ax.set_xlabel(f'Time ({interval})')
        
        name = self.name_graph(interval,y1label,y2label)
        self.ax.set_title(name)
        
        #create cursor and annotations
        if y2 is not None:
            cursor = mplcursors.cursor([bars1, bars2], hover=mplcursors.HoverMode.Transient)
        else:
            cursor = mplcursors.cursor(bars1, hover=mplcursors.HoverMode.Transient)
        @cursor.connect("add")
        def on_add(sel):
            bar = sel.artist[sel.index]
            height = bar.get_height()
            sel.annotation.set(text=f"{times[sel.index]}: {height:.2f}",position=(0, 20), anncoords="offset points")
            sel.annotation.xy = (bar.get_x() + bar.get_width() / 2, height)

        self.ax.legend()

    def create_trajectory_map(self, times, y1, y2, y1label, y2label, coords):
        print(f"Number of coordinates: {len(coords)}")
        img = mpimg.imread('first_floor.png')

        self.ax.imshow(img, extent=[0, img.shape[1], 0, img.shape[0]])

        disconnect_zoom = zoom_factory(self.ax)

        x_coords = []
        y_coords = []
        for coord in coords:
            coord_str = coord.strip('[]')
            x_str, y_str = coord_str.split(', ')
            
            x = int(x_str)
            y = int(y_str)
        
            x_coords.append(x)
            y_coords.append(y)
        
        if len(x_coords) == 0 or len(y_coords) == 0:
            print("No valid coordinates to plot.")
            return

        trajmap = self.ax.plot(x_coords, y_coords, color='orange', marker='.', linestyle='-', label='Trajectory')

        cursor = mplcursors.cursor(trajmap, hover=True)
        @cursor.connect("add")
        def on_add(sel):
            index = int(sel.index)
            if y2 is not None:
                sel.annotation.set(text=f"{times[index]}: ({x_coords[index]:.2f},{y_coords[index]:.2f})\n{y1label}: {y1[index]}\n {y2label}: {y2[index]}",position=(0, 20), anncoords="offset points")
            else:
                sel.annotation.set(text=f"{times[index]}: ({x_coords[index]:.2f},{y_coords[index]:.2f})\n{y1label}: {y1[index]}",position=(0, 20), anncoords="offset points")

        
        self.ax.legend()

    def create_probability_histogram(self, times, y1, y2, y1label, y2label, interval):
        labels_y1 = {
        "10-20": 0,"20-40": 0,"40-60": 0, "60-80": 0, "80-100": 0, "100-120": 0, 
        "120-140": 0, "140-160": 0, "160-180": 0, "180-200": 0
        }
        labels_y2 = {
            "10-20": 0,"20-40": 0,"40-60": 0, "60-80": 0, "80-100": 0, "100-120": 0, 
            "120-140": 0, "140-160": 0, "160-180": 0, "180-200": 0
        }

        total_occurrences = len(times)

        for i, time in enumerate(times):
            #split label to get max or min
            for key in labels_y1:
                min_val, max_val = map(int, key.split('-'))
                if min_val <= y1[i] <= max_val:
                    labels_y1[key]+=1
                if self.y2_exists:
                    if min_val <= y2[i] <=max_val:
                        #append to labels_y2 key
                        labels_y2[key]+=1

        prob_y1 = [round(count * 100 / total_occurrences, 2) for count in labels_y1.values()]
        if self.y2_exists:
            prob_y2 = [round(count * 100 / total_occurrences, 2) for count in labels_y2.values()]
        
        labels = list(labels_y1.keys())

        self.create_bar_graph(labels, prob_y1, prob_y2, y1label, y2label,interval)

        #relabelling custom
        self.ax.set_ylabel("Probability mass")
        if self.y2_exists:
            self.ax.set_xlabel(f"Bin ranges ({y1label} and {y2label}, BPMs)")
        else:
            self.ax.set_xlabel(f"Bin range ({y1label}, BPM)")
        
        interval = interval.replace('s','')
        
        if self.y2_exists:
            self.ax.set_title(f"Distribution of Average {y1label} and {y2label} per {interval} Over a {self.intmin}-{self.intmax} {interval} Interval")
        else:
            self.ax.set_title(f"Distribution of Average {y1label} per {interval} Over a {self.intmin}-{self.intmax} {interval} Interval")
            

    def create_graph(self):
        #first delete top buttons
        self.minbutton.destroy()
        self.maxbutton.destroy()
        self.select_interval.destroy()
        self.createbutton.destroy()
        #delete interactive view options
        self.viewopt_label.destroy()
        self.scaling_checkbutton.destroy()
        self.sliding_checkbutton.destroy()

        #create figure plot and subplot
        fig = Figure(figsize=(10, 6), dpi=100)
        self.ax = fig.add_subplot(111)

        y1label = self.y_values[0]
        y2label = self.y_values[1] if self.y2_exists else None

        #f_ = the filtered version of the int_, int_ = full intervalled set
        f_times, f_y1, f_y2, f_coords, int_times, int_y1, int_y2, int_coords = self.make_interval_minmax_data(self.interval)           

        if self.graph_type == "Line graph":
            self.create_line_graph(f_times, f_y1, f_y2, y1label, y2label, self.interval)
        elif self.graph_type == "Bar graph":
            self.create_bar_graph(f_times, f_y1, f_y2, y1label, y2label, self.interval)
        elif self.graph_type == "Trajectory map":
            self.create_trajectory_map(f_times, f_y1, f_y2, y1label, y2label, f_coords)
        elif self.graph_type == "Probability histogram":
            #interval - will represent prob of  avg of interval durations being within each range from min - max range of time
            self.create_probability_histogram(f_times, f_y1, f_y2, y1label, y2label, self.interval)
        
        self.canvas = FigureCanvasTkAgg(fig, master=self.new_window)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        zoom_factory(self.ax)

        if self.min:
            self.entry_box_min.destroy()
        
        if self.max:
            self.entry_box_max.destroy()


        #0-length of half x bc you decrease 1 on each side for each +1 on slider
        self.scale_widget = Scale(self.new_window, from_=1, to=len(f_times)/2, orient=HORIZONTAL, label="Scale X-Axis View Window", command=lambda value: self.scale_graph(value, f_times))

        d = f_times[0]-int_times[0]
        print("pre-d: " + str(d))
        self.slide_widget1 = Scale(self.new_window, from_=int_times[0], to=f_times[0], sliderlength=min(100 * abs(d), 50),orient=HORIZONTAL, length=300, label="Reposition X-Axis", command=lambda value: self.slide_grap1(value, f_times, f_y1, f_y2, f_coords, y1label, y2label, int_times, int_y1, int_y2, int_coords))

        d = int_times[-1]-f_times[-1]
        print("post-d:" + str(d))
        self.slide_widget2 = Scale(self.new_window, from_=f_times[-1], to=int_times[-1], sliderlength=min(100 * abs(d), 50), orient=HORIZONTAL, length=300, label="Reposition X-Axis", command=lambda value: self.slide_graph2(value, f_times, f_y1, f_y2, f_coords, y1label, y2label, int_times, int_y1, int_y2, int_coords))
        
        if self.scaling.get():
            self.scale_widget.pack()  
        else:
            self.scale_widget.pack_forget()
        
        if self.sliding.get():
            self.slide_widget1.pack()
            self.slide_widget2.pack()
        else:
            self.slide_widget1.pack_forget()
            self.slide_widget2.pack()


    def scale_graph(self, value, f_times):
        scale_value = value
        #add scale_value each side 5-10 -> 6-11
        print("in progress, maybe delete bc very similar function to slide_graph")
        #take 
        '''self.ax.set_xlim(f_times, len(f_times)-scale_value)
        self.canvas.draw()
'''
    def slide_graph1(self, value, f_times, f_y1, f_y2, f_coords, y1label, y2label, int_times, int_y1, int_y2, int_coords):
        slide_value1 = int(value)

        sf_times = []
        sf_y1 = []
        if self.y2_exists:
            sf_y2 = [] 
        sf_coords = []

        #where the filtered graph starts and ends in indexes within the full range of data
        startg = int_times.index(f_times[0])
        endg = int_times.index(f_times[-1])

        #where the new indexes start and end
        start_idx = max(0, startg - slide_value1)
        
        #append data before the filtered range
        sf_times.extend(int_times[start_idx:startg])
        sf_y1.extend(int_y1[start_idx:startg])
        if self.y2_exists:
            sf_y2.extend(int_y2[start_idx:startg])
        sf_coords.extend(int_coords[start_idx:startg])

        # append filtered data
        sf_times.extend(f_times)
        sf_y1.extend(f_y1)
        if self.y2_exists:
            sf_y2.extend(f_y2)
        sf_coords.extend(f_coords)

        #regraph
        self.ax.clear()

        match self.graph_type:
            case "Line graph":
                self.create_line_graph(sf_times, sf_y1, sf_y2, y1label, y2label, self.interval)
            case "Bar graph":
                self.create_bar_graph(sf_times, sf_y1, f_y2, y1label, y2label, self.interval)
            case "Trajectory map":
                self.create_trajectory_map(sf_times, f_y1, f_y2, y1label, y2label, sf_coords)
            case "Probability histogram":
                self.create_probability_histogram(sf_times, sf_y1, sf_y2, y1label, y2label, self.interval)
        self.canvas.draw()

    def slide_graph2(self, value, f_times, f_y1, f_y2, f_coords, y1label, y2label, int_times, int_y1, int_y2, int_coords):
        slide_value2 = int(value)
        #add the indices of n1 hours before f_times to f_times, then add the andices of n2 hours after and replot
        #0|------------------| start time w1   {displayed graph} end |-----| w2 end data
        #ex 0-5 graph 5-10 10-24 hours
        sf_times = []
        sf_y1 = []
        if self.y2_exists:
            sf_y2 = [] 
        sf_coords = []
        #where the filtered graph starts and ends in indexes within the full range of data
        startg = int_times.index(f_times[0])
        endg = int_times.index(f_times[-1])
        end_idx = min(len(int_times), endg + slide_value2 + 1)  # +1 for inclusive end

        # append filtered data
        sf_times.extend(f_times)
        sf_y1.extend(f_y1)
        if self.y2_exists:
            sf_y2.extend(f_y2)
        sf_coords.extend(f_coords)

        # append data after the filtered range
        sf_times.extend(int_times[endg + 1:end_idx])
        sf_y1.extend(int_y1[endg + 1:end_idx])
        if self.y2_exists:
            sf_y2.extend(int_y2[endg + 1:end_idx])
        sf_coords.extend(int_coords[endg + 1:end_idx])

        self.ax.clear()

        match self.graph_type:
            case "Line graph":
                self.create_line_graph(sf_times, sf_y1, sf_y2, y1label, y2label, self.interval)
            case "Bar graph":
                self.create_bar_graph(sf_times, sf_y1, f_y2, y1label, y2label, self.interval)
            case "Trajectory map":
                self.create_trajectory_map(sf_times, f_y1, f_y2, y1label, y2label, sf_coords)
            case "Probability histogram":
                self.create_probability_histogram(sf_times, sf_y1, sf_y2, y1label, y2label, self.interval)
        self.canvas.draw()

    def name_graph(self,interval,y1label,y2label):
        title = ""
        #self.intmin, intmax
        if y2label is not None:
            if interval == "Seconds":
                title = y1label + " and " + y2label + " per " + interval.replace('s','') + " Over a " + str(self.intmin) + "-" + str(self.intmax) + interval.replace('s','') + "Interval"
            else:
                title = "Average " + y1label + " and " + y2label + " per " + interval.replace('s','')
        else:
            if interval == "Seconds":
                title = y1label + " per " + interval.replace('s','')
            else:
                title = "Average " + y1label + " per " + interval.replace('s','')
        return title

if __name__ == "__main__":
    root = tk.Tk()
    data = pd.read_csv("Vital Signs Data.csv")
    app = BatchWindow(master=root, data=data, x_value='Time', y_values=['Heart Rate','Respiration Rate'], graph_type="Line graph", coords=data['Location'].tolist())
    root.mainloop()
