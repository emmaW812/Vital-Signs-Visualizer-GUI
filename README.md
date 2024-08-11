# Vital-Signs-Visualizer-GUI
GUI capable of producing bar graphs, line graphs, trajectory map (given coordinates), probability mass histogram. + ingest and plot data real time

The blueprint used in the trajectory map was taken from the Orange4home data. The code will still work if you replace the image paths with your desired image (as long as it is in the same folder). Ensure all python files, the data CSV file, and the image for the trajectory map are in the same folder. Data CSV folder should have four columns: 'Time', 'Heart Rate', 'Respiration Rate', and 'Location'.
Update the pathway GUI_br.py to your actual data CSV file name: data = pd.read_csv("Vital Signs Data.csv") and the house blueprint for displaying trajectory map

**Here is a list of completed features for the GUI:**

Bar graph
Line graph
Trajectory map
Real-time data ingestion and simultaneous graph updates for the above graphs
Probability Mass Histogram

Hovering over points on any graph displays a label with rate/time

**For customization**, users can:
  - Add a time range for data extraction, adjust sliders to expand range after graphing
  - Select an interval length from "Seconds", "Minutes", "Hours", "Days", and "Weeks"
  - zoom in and out capability

**GUI setup/file order:** GUI_br < batch_or_realtime < batch (or realtime) 
