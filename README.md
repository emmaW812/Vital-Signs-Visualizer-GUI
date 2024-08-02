# Vital-Signs-Visualizer-GUI
GUI capable of producing bar graphs, line graphs, trajectory map (given coordinates), probability mass histogram. + ingest and plot data real time

The blueprint used in the trajectory map was taken from the Orange4home data. The code will still work if you replace the image paths with your desired image (as long as it is in the same folder). Ensure all python files, the data CSV file, and the image for the trajectory map are in the same folder. Data CSV folder should have four columns: 'Time', 'Heart Rate', 'Respiration Rate', and 'Location'.
Update the pathway GUI_br.py to your actual data CSV file name: data = pd.read_csv("Vital Signs Data.csv")

**Here is a list of completed features for the GUI:**

Bar graph
Line graph
Trajectory map
Real-time data ingestion and simultaneous graph updates for the above graphs

Hovering over points on any graph displays a label with rate/time

**For customization**, users can:
  - Add a time range for data extraction
  - Select an interval length from "Seconds", "Minutes", "Hours", "Days", and "Weeks"

**In progress:**
  - Probability Mass Histogram
  - move left/right to show earlier/later values e.g., using the mouse to pull curves left/right, or page up/down         to show previous or next day/week/month
  - scale the x axis range easily to see wider/narrower time windows
  - zoom in and out capability

**GUI setup/file order:** GUI_br < batch_or_realtime < batch (or realtime) 
