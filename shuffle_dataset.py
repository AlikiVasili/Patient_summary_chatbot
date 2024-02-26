import csv
import random

# Open the input CSV file
with open('train.csv', 'r') as input_file:
    # Read the CSV data into a list of rows
    rows = list(csv.reader(input_file))

# Extract the header row (first row)
header_row = rows[0]

# Shuffle the data rows (excluding the header)
data_rows = rows[1:]
random.shuffle(data_rows)

# Create a shuffled list of rows including the header
shuffled_rows = [header_row] + data_rows

# Open a new output CSV file for writing the shuffled data
with open('train_shuffled.csv', 'w', newline='') as output_file:
    # Create a CSV writer object
    csv_writer = csv.writer(output_file)

    # Write the shuffled rows back to the output CSV file
    csv_writer.writerows(shuffled_rows)

print("Data rows shuffled and saved to shuffled_output.csv while keeping the header row intact.")
