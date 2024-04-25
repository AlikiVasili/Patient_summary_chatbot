# Read the JSON file with tha patient summary
from dateutil import parser
import json

with open('patientSummary.json') as f:
    data = json.load(f)


def main():
    # Find the entry with resourceType "Composition"
    composition_entry = next(entry for entry in data["entry"] if entry["resource"]["resourceType"] == "Composition")

    # Find the section with title "illnesses"
    illnesses_section = next(section for section in composition_entry["resource"]["section"] if section["title"] == "History of Past Illness")

    # Extract entries inside the section
    illnesses_entries = illnesses_section["entry"]

    # Extract only the numbers from the references
    illnesses_numbers = [entry["reference"].split("/")[-1] for entry in illnesses_entries]

    illnesses_list = []
    for number in illnesses_numbers:
        target_fullUrl = "urn:uuid:" + number
                        
        # Find the entry with the specified fullUrl
        target_entry = next((entry for entry in data.get("entry", []) if entry.get("fullUrl") == target_fullUrl), None)

        code =  target_entry["resource"]["code"]["coding"][0]["code"]

        # Check if coding_display is equal to specified values
        no_info_values = ["no-problem-info","no-known-problems"]
        
        if not(code in no_info_values):
            try:
                description = target_entry["resource"]["code"]["coding"][0]["display"]
            except KeyError:
                description = None
            try:
                clinical_status = target_entry["resource"]["clinicalStatus"]["coding"][0]["display"]
            except KeyError:
                clinical_status = None
            try:
                severity = target_entry["resource"]["severity"]["coding"][0]["display"]
            except KeyError:
                severity = None
            try:
                date_time = target_entry["resource"]["onsetDateTime"]
                date_time_obj = parser.parse(date_time)
                # Extracting date and time components
                onset_date = date_time_obj.date()
                onset_time = date_time_obj.time()
                # Formatting date as dd/mm/yyyy
                onset_date = onset_date.strftime("%d/%m/%Y")
                # Formatting time as h:min
                onset_time = onset_time.strftime("%H:%M")
            except KeyError:
                onset_date = None
                onset_time = None
            try:
                end_date_time = target_entry["resource"]["abatementDateTime"]
                end_date_time_obj = parser.parse(end_date_time)
                # Extracting date and time components
                end_date = end_date_time_obj.date()
                end_time = end_date_time_obj.time()
                # Formatting date as dd/mm/yyyy
                end_date = end_date.strftime("%d/%m/%Y")
                # Formatting time as h:min
                end_time = end_time.strftime("%H:%M")
            except KeyError:
                end_date = None
                end_time = None

            illnesses_list.append({
                "number": number,
                "description": description,
                "clinical_status": clinical_status,
                "severity": severity,
                "onset_date": onset_date,
                "onset_time": onset_time,
                "end_date": end_date,
                "end_time": end_time
            })

    return illnesses_list

if __name__ == "__main__":
    illnesses = main()
    print(illnesses)