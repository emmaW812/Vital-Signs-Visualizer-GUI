import tkinter as tk
import customtkinter
from batch import BatchWindow
from realtime import RealTimeWindow
import pandas as pd

class Choose:
    def __init__(self, master, data, x_value, y_values, graph_type, coords):
        self.root = tk.Toplevel(master)
        self.root.geometry("300x150")
        self.root.title('Select Data Processing Mode')
        
        self.master = master
        self.data = data
        self.x_value = x_value
        self.y_values = y_values
        self.graph_type = graph_type
        self.coords = coords

        self.create_buttons()
    
    def create_buttons(self):
        self.select_mode = customtkinter.CTkOptionMenu(self.root, values=["Batch processing", "Real-time"])
        self.select_mode.grid(row=0,column=0,padx=10, pady=10)
        self.select_mode.set("Select mode")

        next_button = tk.Button(self.root, text="Next", command=self.open_filter_window)
        next_button.grid(row=0, column=1, padx=10, pady=10)

    def open_filter_window(self):
        mode = self.select_mode.get()
        if mode == "Batch processing":
            BatchWindow(self.root, self.data, self.x_value, self.y_values, self.graph_type, self.coords)
        elif mode == "Real-time":
            RealTimeWindow(self.root, self.data, self.x_value, self.y_values, self.graph_type)
        self.root.withdraw()



if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    data = pd.read_csv("Vital Signs Data.csv")
    app = Choose(master=root, data=data, x_value='Time', y_values=['Heart Rate','Respiration Rate'], graph_type="Trajectory map", coords=data['Location'].tolist())
    root.mainloop()