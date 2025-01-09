# UV-Vis Data Analysis Tool

A Python application for analyzing UV-Vis data. This tool can read CSV files from UV-Vis instruments, process absorbance and transmittance data, and generate plots and CSV files for further analysis.

## Key Features
- **CSV File Reading**: Supports both old and new UV-Vis instrument CSV formats.
- **Interactive Plots**: Generates wavelength vs. absorbance/transmittance plots.
- **Data Export**: Saves analysis results to CSV files.
- **Degradation Calculation**: Automatically calculates sample degradation percentages.
- **User Interface**: Simple GUI built with Tkinter.

## Installation
1. Clone this repository:
   ```bash
   git clone https://github.com/username/uv-vis-analysis.git

   Navigate to the project folder:

cd uv-vis-analysis
Install dependencies:

pip install -r requirements.txt
Usage
Run the application:

python main.py
Select the folder containing UV-Vis CSV files.

Enter sample names (separate with commas for multiple samples).

Enter a graph title.

Choose the type of plot (Absorbance or Transmittance).

Click "Process Data" to analyze the data and display the plot.

Analysis results will be saved in the GabunganAbsSampel folder.