import tkinter as tk
import customtkinter
from tkinter import ttk

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
        
        self.create_buttons()

    def create_buttons(self):
        # min and max button
        self.minbutton = tk.Button(self.new_window, text="Add start time (sec) >", command=self.create_entry_box_min)
        self.minbutton.pack(pady=10, padx=10)

        self.maxbutton = tk.Button(self.new_window, text="Add end time (sec) >", command=self.create_entry_box_max)
        self.maxbutton.pack(pady=10, padx=10)

        # interval dropdown
        self.select_interval = customtkinter.CTkOptionMenu(self.new_window, values=["Seconds", "Minutes", "Hours", "Days","Weeks"], command=self.interval_selected)
        self.select_interval.pack(pady=10, padx=10)
        self.select_interval.set("Select interval length")

        # be able to create and view two graphs at once? + connect to real time
        self.createbutton = tk.Button(self.new_window, text="Create", command=self.create_graph)
        self.createbutton.pack(pady=10, padx=10)
    
    def interval_selected(self, selected_value):
        self.interval = selected_value

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
        if self.min and self.max:
            min_value = float(self.entry_box_min.get())
            max_value = float(self.entry_box_max.get())
        elif self.min == True and self.max == False:
            min_value = float(self.entry_box_min.get())
            max_value = None
        elif self.min == False and self.max == True:
            max_value = float(self.entry_box_max.get())
            min_value = None
        else:
            #neither
            min_value = None
            max_value = None
        return min_value, max_value


    def make_interval_minmax_data(self, interval):
        j_count = 0
        times = []
        y1_avg = []
        y2_avg = [] if self.y2_exists else None
        coords = []

        print(interval)
        print(type(interval))

        #var for length of seconds of the interval chosen

        if interval == "Seconds":
            sec_len = 1
        elif interval == "Minutes":
            sec_len = 60
        elif interval == "Hours":
            sec_len = 3600
        elif interval == "Days":
            sec_len = 86400
        elif interval == "Weeks":
            sec_len = 604800
        
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
        
        #MIN MAX RANGE
        min_value, max_value = self.get_min_max_values()

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
                if s <= max_value: 
                    self.timesfiltered.append(times[i])
                    self.y1_avgfiltered.append(y1_avg[i])
                    self.y2_avgfiltered.append(y2_avg[i]) if self.y2_exists else None
                    self.coordsfiltered.append(coords[i])
            elif self.max == False:
                if s >= min_value: 
                    self.timesfiltered.append(times[i])
                    self.y1_avgfiltered.append(y1_avg[i])
                    self.y2_avgfiltered.append(y2_avg[i]) if self.y2_exists else None
                    self.coordsfiltered.append(coords[i])
            else:
                if min_value <= s <= max_value: 
                    self.timesfiltered.append(times[i])
                    self.y1_avgfiltered.append(y1_avg[i])
                    self.y2_avgfiltered.append(y2_avg[i]) if self.y2_exists else None
                    self.coordsfiltered.append(coords[i])

        return self.timesfiltered, self.y1_avgfiltered, self.y2_avgfiltered, self.coordsfiltered
    

    def create_line_graph(self, ax, times, y1, y2, y1label, y2label,interval):
        # LINE GRAPH
        line1 = ax.plot(times, y1, label=y1label, color='orange', linewidth=2)
        if y2 is not None:
            line2 = ax.plot(times, y2, label=y2label, color='magenta', linewidth=2)
            ax.set_ylabel('Rates')
        else:
            ax.set_ylabel(y1label)
        
        ax.set_xlabel(f'Time ({interval})')

        name = self.name_graph(interval,y1label,y2label)
        ax.set_title(name)
        
        #create cursor
        if y2 is not None:
            cursor = mplcursors.cursor(line1, hover=mplcursors.HoverMode.Transient)
            cursor = mplcursors.cursor(line2, hover=mplcursors.HoverMode.Transient)
        else:
            cursor = mplcursors.cursor(line1, hover=mplcursors.HoverMode.Transient)
        print("Cursor created")

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
        ax.legend()

    def create_bar_graph(self, ax, times, y1, y2, y1label, y2label,interval):
        bar_width = 0.4
        indices = np.arange(len(times))

        # Adjust positions to avoid overlap
        bars1 = ax.bar(indices, y1, bar_width, label=y1label, color='orange')
        if y2 is not None:
            bars2 = ax.bar(indices + bar_width, y2, bar_width, label=y2label, color='magenta')
            ax.set_ylabel('Rates')
        else:
            ax.set_ylabel(y1label)
        
        #set the location of the x ticks and labels
        ax.set_xticks(indices + bar_width / 2)
        ax.set_xticklabels(times, rotation=45)
        ax.set_xlabel(f'Time ({interval})')
        
        name = self.name_graph(interval,y1label,y2label)
        ax.set_title(name)
        
        #create cursor and annotations
        if y2 is not None:
            cursor = mplcursors.cursor([bars1, bars2], hover=mplcursors.HoverMode.Transient)
        else:
            cursor = mplcursors.cursor(bars1, hover=mplcursors.HoverMode.Transient)
        print("Cursor created")
        @cursor.connect("add")
        def on_add(sel):
            bar = sel.artist[sel.index]
            height = bar.get_height()
            sel.annotation.set(text=f"{times[sel.index]}: {height:.2f}",position=(0, 20), anncoords="offset points")
            sel.annotation.xy = (bar.get_x() + bar.get_width() / 2, height)

        ax.legend()
    
    def create_trajectory_map(self, ax, times, y1, y2, y1label, y2label, coords):
        print(f"Number of coordinates: {len(coords)}")
        img = mpimg.imread('first_floor.png')

        ax.imshow(img, extent=[0, img.shape[1], 0, img.shape[0]])

        disconnect_zoom = zoom_factory(ax)

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

        trajmap = ax.plot(x_coords, y_coords, color='orange', marker='.', linestyle='-', label='Trajectory')

        cursor = mplcursors.cursor(trajmap, hover=True)
        @cursor.connect("add")
        def on_add(sel):
            index = int(sel.index)
            if y2 is not None:
                sel.annotation.set(text=f"{times[index]}: ({x_coords[index]:.2f},{y_coords[index]:.2f})\n{y1label}: {y1[index]}\n {y2label}: {y2[index]}",position=(0, 20), anncoords="offset points")
            else:
                sel.annotation.set(text=f"{times[index]}: ({x_coords[index]:.2f},{y_coords[index]:.2f})\n{y1label}: {y1[index]}",position=(0, 20), anncoords="offset points")

        
        ax.legend()

    def create_graph(self):
        #first delete top buttons
        self.minbutton.destroy()
        self.maxbutton.destroy()
        self.select_interval.destroy()
        self.createbutton.destroy()
        #create figure plot and subplot
        fig = Figure(figsize=(10, 6), dpi=100)
        ax = fig.add_subplot(111)

        y1label = self.y_values[0]
        y2label = self.y_values[1] if self.y2_exists else None

        times_avg, y1_avg, y2_avg, coords = self.make_interval_minmax_data(self.interval)

        if self.graph_type == "Line graph":
            self.create_line_graph(ax, times_avg, y1_avg, y2_avg, y1label, y2label, self.interval)
        elif self.graph_type == "Bar graph":
            self.create_bar_graph(ax, times_avg, y1_avg, y2_avg, y1label, y2label, self.interval)
        elif self.graph_type == "Trajectory map":
            self.create_trajectory_map(ax, times_avg, y1_avg, y2_avg, y1label, y2label, coords)

        canvas = FigureCanvasTkAgg(fig, master=self.new_window)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        if self.min:
            self.entry_box_min.destroy()
        
        if self.max:
            self.entry_box_max.destroy()
    
    def name_graph(self,interval,y1label,y2label):
        title = ""
        if y2label is not None:
            if interval == "Seconds":
                title = y1label + " and " + y2label + " per " + interval.replace('s','')
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
    app = BatchWindow(master=root, data=data, x_value='Time', y_values=['Heart Rate','Respiration Rate'], graph_type="Trajectory map", coords=data['Location'].tolist())
    root.mainloop()
