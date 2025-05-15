# This Python script processes time-series NDVI data (exported as CSVs from Google Earth Engine) 
# to analyze how vegetation health changed before and after Hurricane Irma (Sept 6, 2017) 
# at four mangrove sites in the British Virgin Islands

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

# Define file paths
file_paths = [
    "/Users/jillmunger/Desktop/UNH/research/remote_sensing/time_series/french_NDVI_timeseries.csv",
    "/Users/jillmunger/Desktop/UNH/research/remote_sensing/time_series/hans_NDVI_timeseries.csv",
    "/Users/jillmunger/Desktop/UNH/research/remote_sensing/time_series/paraquita_NDVI_timeseries.csv",
    "/Users/jillmunger/Desktop/UNH/research/remote_sensing/time_series/scb_NDVI_timeseries.csv"
]

# Mapping file names to proper site names
site_name_map = {
    "french": "Frenchman's Cay",
    "hans": "Hans Creek",
    "paraquita": "Paraquita Bay",
    "scb": "Sea Cow's Bay"
}

def process_file(file_path):
    df = pd.read_csv(file_path)
    df.columns = ['date', 'ndvi']  # Rename columns
    df['date'] = pd.to_datetime(df['date'].str.strip(), errors='coerce')  # Convert date properly
    site_key = os.path.basename(file_path).split('_')[0]  # Extract site key from filename
    df['site'] = site_name_map.get(site_key, site_key)  # Assign proper site name
    return df

# Process all files and concatenate them
dfs = [process_file(fp) for fp in file_paths]
ndvi_data = pd.concat(dfs, ignore_index=True)

# Define hurricane date
hurricane_date = pd.to_datetime("2017-09-06")

# Determine the time range to use (equal months before and after the hurricane)
time_window = pd.DateOffset(months=6)  # Adjust as needed
start_date = hurricane_date - time_window
end_date = hurricane_date + time_window
ndvi_data = ndvi_data[(ndvi_data['date'] >= start_date) & (ndvi_data['date'] <= end_date)]

# Label periods
ndvi_data['period'] = ndvi_data['date'].apply(lambda x: 'Before' if x < hurricane_date else 'After')

# Create boxplots
plt.figure(figsize=(10, 6))
sns.boxplot(x='site', y='ndvi', hue='period', data=ndvi_data)
plt.title("NDVI Values Before and After Hurricane Irma", fontsize=18)
plt.xlabel("Site", fontsize=14)
plt.ylabel("NDVI", fontsize=14)
plt.legend(title="Period", loc='upper right', fontsize=12)  # Move legend to upper right
plt.xticks(rotation=45, fontsize=12)
plt.yticks(fontsize=12)
plt.tight_layout()

# Save the plot
output_path = "/Users/jillmunger/Desktop/UNH/research/remote_sensing/time_series/ndvi_boxplot_all.png"
plt.savefig(output_path)
print(f"Boxplot saved to {output_path}")

## Save processed data to CSV
# csv_output_path = "/Users/jillmunger/Desktop/UNH/research/remote_sensing/time_series/ndvi_combined.csv"
# ndvi_data.to_csv(csv_output_path, index=False)
# print(f"Processed data saved to {csv_output_path}")
