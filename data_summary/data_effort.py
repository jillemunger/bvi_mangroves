import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Data
data = {
    'Site': ['Paraquita Bay', 'Frenchman\'s Cay', 'Hans Creek A', 'Sea Cow\'s Bay', 'Paraquita Bay',
             'Frenchman\'s Cay', 'Hans Creek A', 'Hans Creek B', 'Sea Cow\'s Bay', 'Paraquita Bay B', 'Hans Creek B'],
    'Start': ['1/15/24', '1/15/24', '1/16/24', '1/14/24', '3/17/24', 
              '3/18/24', '3/19/24', '3/19/24', '3/17/24', '6/19/24', '6/20/24'],
    'End': ['2/29/24', '3/4/24', '2/21/24', '3/6/24', '6/9/24', 
            '6/16/24', '7/30/24', '6/4/24', '6/16/24', '9/21/24', '9/22/24']
}

# Convert to DataFrame
df = pd.DataFrame(data)

# Convert Start and End columns to datetime
df['Start'] = pd.to_datetime(df['Start'], format='%m/%d/%y')
df['End'] = pd.to_datetime(df['End'], format='%m/%d/%y')

# Plot setup
fig, ax = plt.subplots(figsize=(10, 6))

# Plot each bar for the site
for idx, row in df.iterrows():
    ax.barh(row['Site'], (row['End'] - row['Start']).days, left=row['Start'], height=0.4, color='skyblue')

# Formatting the x-axis as months
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b-%y'))

# Invert y-axis to match the style in the example
ax.invert_yaxis()

# Add gridlines for readability
ax.grid(True, axis='x', linestyle='--', alpha=0.7)

# Labels
ax.set_xlabel('Month', fontweight='bold')
ax.set_ylabel('Site', fontweight='bold')
plt.title('Tortola Data Collection Effort', fontweight='bold')

# Rotate date labels for better readability
plt.xticks(rotation=45)

# Show the plot
plt.tight_layout()
plt.show()
