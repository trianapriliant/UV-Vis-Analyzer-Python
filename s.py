import csv

# Define the input and output file names
input_file = 'combined_data.csv'  # Replace with your input file name
output_file = 'separated_data.csv'  # Replace with your desired output file name

# Open the input CSV file
with open(input_file, 'r', newline='', encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile)
    
    # Read all rows from the input file
    rows = [row for row in reader]

# Split the single column data by semicolons
split_data = [row[0].split(';') for row in rows]

# Open the output CSV file
with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    
    # Write the split data to the output file
    writer.writerows(split_data)

print(f"Data has been separated and saved to {output_file}")