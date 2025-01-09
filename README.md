echo "# UV-Vis Data Analysis Tool

A Python application for analyzing UV-Vis data. This tool can read CSV files from UV-Vis instruments, process absorbance and transmittance data, and generate plots and CSV files for further analysis.

## Key Features
- **CSV File Reading**: Supports both old and new UV-Vis instrument CSV formats.
- **Interactive Plots**: Generates wavelength vs. absorbance/transmittance plots.
- **Data Export**: Saves analysis results to CSV files.
- **Degradation Calculation**: Automatically calculates sample degradation percentages.
- **User Interface**: Simple GUI built with Tkinter.

## Installation
1. Clone this repository:
   \`\`\`bash
   git clone https://github.com/username/uv-vis-analysis.git
   \`\`\`
2. Navigate to the project folder:
   \`\`\`bash
   cd uv-vis-analysis
   \`\`\`
3. Install dependencies:
   \`\`\`bash
   pip install -r requirements.txt
   \`\`\`

## Usage
1. Run the application:
   \`\`\`bash
   python main.py
   \`\`\`
2. Select the folder containing UV-Vis CSV files.
3. Enter sample names (separate with commas for multiple samples).
4. Enter a graph title.
5. Choose the type of plot (Absorbance or Transmittance).
6. Click \"Process Data\" to analyze the data and display the plot.
7. Analysis results will be saved in the \`GabunganAbsSampel\` folder.

## Folder Structure
\`\`\`
uv-vis-analysis/
│
├── src/                  # Source code for the application
│   ├── main.py           # Main application file
│   ├── plot.py           # Functions for generating plots
│   └── utils.py          # Utility functions
├── data/                 # Example UV-Vis CSV data files
│   └── sample_data.csv
├── output/               # Folder for saving analysis results
│   └── AbsSampel.csv
├── requirements.txt      # List of dependencies
├── README.md             # Project documentation
└── .gitignore            # File to ignore unnecessary files/folders
\`\`\`

## Example Data
UV-Vis CSV files should follow these formats:
- **Old Instrument**:
  \`\`\`
  No.  WL(nm)  Abs
  1    800.0   -0.008
  2    799.0