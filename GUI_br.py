import tkinter as tk
from tkinter import ttk
import customtkinter
import pandas as pd

#from window1 import NewWindow
from batch_or_realtime import Choose

data = pd.read_csv("Vital Signs Data.csv")

#adding new column (y) entry
def add_column_y2():
    add_button.destroy()
    y_label = ttk.Label(frame, text=f"Column name (y2)")
    y_label.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
    y_entry = ttk.Entry(frame, width=20)
    y_entry.grid(row=2, column=1, padx=5, pady=5)
    y_entries.append(y_entry)


#save entries, new window
def open_new_window():
    x_value = x_entry.get()
    y_values = [y_entry.get() for y_entry in y_entries]
    graph_type = select_graphs.get()
    coords = data['Location'].tolist()
    print("X Value:", x_value)
    print("Y Values:", y_values)

    Choose(root, data, x_value, y_values, graph_type, coords)

def create_tooltip(widget, text):
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

#main application window
root = tk.Tk()
root.title("Visualizer")

#frame for the visualizer
frame = ttk.Frame(root, padding="10")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

#place the labels and entries
ttk.Label(frame, text="Column name (x)").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
x_entry = ttk.Entry(frame, width=20)
x_entry.grid(row=0, column=1, padx=5, pady=5)

ttk.Label(frame, text="Column name (y)").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
y_entry = ttk.Entry(frame, width=20)
y_entry.grid(row=1, column=1, padx=5, pady=5)

y_entries = [y_entry]

#buttons
add_button = ttk.Button(frame, text="Add column data (y)", command=add_column_y2)
add_button.grid(row=2, column=0, padx=5, pady=5)

select_graphs = customtkinter.CTkOptionMenu(frame, values=["Bar graph", "Line graph", "Trajectory map","Probability Histogram"])
select_graphs.grid(row=3,column=0,padx=5, pady=5)
select_graphs.set("Select graph type")

create_tooltip(select_graphs, "Bar graph, Line graph, and Trajectory map can be viewed in real-time.\nProbability Histogram cannot.\nFor Trajectory map, if y1 and y2 are defined, rates at the recorded location point will be displayed when hovered over.")

next_button = ttk.Button(frame, text="Next", command=open_new_window)
next_button.grid(row=4, column=1, padx=5, pady=5)

root.mainloop()