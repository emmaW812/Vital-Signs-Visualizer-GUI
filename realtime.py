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
import threading

import numpy as np
import pandas as pd
import time

class RealTimeWindow:
    def __init__(self, master, data, x_value, y_values, graph_type):
        self.new_window = tk.Toplevel(master)
        self.new_window.title('Filters')

        self.data = data
        self.x_value = x_value
        self.y_values = y_values
        self.graph_type = graph_type
        self.stop = False
        self.real_time = 0

        try:
            placeholder = self.data[self.y_values[1]].tolist()
            self.y2_exists = True
        except:
            self.y2_exists = False

        self.create_buttons()

    def create_buttons(self):
        # interval dropdown
        self.select_interval = customtkinter.CTkOptionMenu(self.new_window, values=["Seconds", "Minutes", "Hours"], command=self.interval_selected)
        self.select_interval.pack(pady=10, padx=10)
        self.select_interval.set("Select interval length")

        self.createbutton = tk.Button(self.new_window, text="Create", command=self.setup_graph)
        self.createbutton.pack(pady=10, padx=10)
    
    def interval_selected(self, selected_value):
        self.interval = selected_value 

    def create_line_graph(self, ax, times, y1, y2, y1label, y2label):
        # LINE GRAPH
        line1 = ax.plot(times, y1, label=y1label, color='orange', linewidth=2)
        if y2 is not None:
            line2 = ax.plot(times, y2, label=y2label, color='magenta', linewidth=2)
            ax.set_ylabel('Rates')
        else:
            ax.set_ylabel(y1label)
        
        ax.set_xlabel(f'Time ({self.interval})')

        name = self.name_graph(y1label,y2label)
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

    def create_bar_graph(self, ax, times, y1, y2, y1label, y2label):
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
        ax.set_xlabel(f'Time ({self.interval})')
        
        name = self.name_graph(y1label,y2label)
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
    
    def update_data(self, sec_len):
        while not self.stop:
            time.sleep(sec_len)
            last_row = self.data.iloc[-1]
            current_time = last_row[self.x_value]
            y1_value = last_row[self.y_values[0]]
            y2_value = last_row[self.y_values[1]] if self.y2_exists else None
            current_coords = last_row['Location']

            self.times.append(self.real_time)
            self.y1.append(y1_value)
            if self.y2_exists:
                self.y2.append(y2_value)
            self.coords.append(current_coords)

            #limit to only 60 points
            self.times = self.times[-60:]
            self.y1 = self.y1[-60:]
            self.y2 = self.y2[-60:]
            self.coords = self.coords[-60:]

            #increase self.real_time by seclen increments
            self.real_time+=1

            self.update_graph()

    def setup_graph(self):
        #first delete top buttons
        self.select_interval.destroy()
        self.createbutton.destroy()
        #create figure plot and subplot
        self.fig = Figure(figsize=(10, 6), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.new_window)

        self.y1label = self.y_values[0]
        self.y2label = self.y_values[1] if self.y2_exists else None

        self.sec_len = {
            "Seconds": 1,
            "Minutes": 60,
            "Hours": 3600,
            "Days": 86400,
            "Weeks": 604800
        }[self.interval]
        
        self.times, self.y1, self.y2, self.coords = [], [], [], []
        #run update data - will run every interval/seclen secs and then will run update graph
        self.update_thread = threading.Thread(target=self.update_data, args=(self.sec_len,))

        self.update_thread.start()
        
        stop_button = tk.Button(self.new_window, text="Stop", command=self.stop_update)
        stop_button.pack(side=tk.BOTTOM)
    
    def update_graph(self):
        self.ax.clear()
        if self.graph_type == "Line graph":
            self.create_line_graph(self.ax, self.times, self.y1, self.y2, self.y1label, self.y2label)
        elif self.graph_type == "Bar graph":
            self.create_bar_graph(self.ax, self.times, self.y1, self.y2, self.y1label, self.y2label)
        elif self.graph_type == "Trajectory map":
            self.create_trajectory_map(self.ax, self.times, self.y1, self.y2, self.y1label, self.y2label, self.coords) 
           
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    
    def stop_update(self):
        self.stop = True
        self.update_thread.join()
    
    def name_graph(self,y1label,y2label):
        title = ""
        if y2label is not None:
            if self.interval == "Seconds":
                title = y1label + " and " + y2label + " per " + self.interval.replace('s','')
            else:
                title = "Average " + y1label + " and " + y2label + " per " + self.interval.replace('s','')
        else:
            if self.interval == "Seconds":
                title = y1label + " per " + self.interval.replace('s','')
            else:
                title = "Average " + y1label + " per " + self.interval.replace('s','')
        return title

if __name__ == "__main__":
    root = tk.Tk()
    data = pd.read_csv("Vital Signs Data.csv")
    app = RealTimeWindow(master=root, data=data, x_value='Time', y_values=['Heart Rate','Respiration Rate'], graph_type="Line graph")
    root.mainloop()
