import csv
import sys

def append_to_csv(feedback_type, feedback_text, csv_filename='feedback_data.csv'):
    # Open the CSV file in append mode
    with open(csv_filename, 'a', newline='') as csvfile:
        # Create a CSV writer object
        csv_writer = csv.writer(csvfile)

        # Write the data to the CSV file
        csv_writer.writerow([feedback_type, feedback_text])

    print(f"Feedback ({feedback_type}): '{feedback_text}' has been appended to {csv_filename}.")

if __name__ == "__main__":
    # Check if the correct number of arguments is provided
    if len(sys.argv) != 3:
        print("Usage: python script_name.py feedback_type feedback_text")
        sys.exit(1)

    # Get feedback_type and feedback_text from command line arguments
    feedback_type = sys.argv[1]
    feedback_text = sys.argv[2]

    # Call the function to append data to CSV file
    append_to_csv(feedback_type, feedback_text)