# Read the JSON file with tha patient summary
from dateutil import parser
import json

with open('patientSummary.json') as f:
    data = json.load(f)


def main():
    # Find the entry with resourceType "Composition"
    composition_entry = next(entry for entry in data["entry"] if entry["resource"]["resourceType"] == "Composition")

    # Find the section with title "procedures"
    procedures_section = next(section for section in composition_entry["resource"]["section"] if section["title"] == "History of Procedures")

    # Extract entries inside the section
    procedures_entries = procedures_section["entry"]

    # Extract only the numbers from the references
    procedures_numbers = [entry["reference"].split("/")[-1] for entry in procedures_entries]

    procedures_list = []
    for number in procedures_numbers:
        target_fullUrl = "urn:uuid:" + number
                        
        # Find the entry with the specified fullUrl
        target_entry = next((entry for entry in data.get("entry", []) if entry.get("fullUrl") == target_fullUrl), None)

        code =  target_entry["resource"]["code"]["coding"][0]["code"]

        # Check if coding_display is equal to specified values
        no_info_values = ["no-procedure-info","no-known-procedures"]
        
        if not(code in no_info_values):
            try:
                description = target_entry["resource"]["code"]["coding"][0]["display"]
            except KeyError:
                description = None

            try:
                clinical_status = target_entry["resource"]["status"]
            except KeyError:
                clinical_status = None

            try:
                date_time = target_entry["resource"]["performedDateTime"]
                date_time_obj = parser.parse(date_time)
                # Extracting date and time components
                date = date_time_obj.date()
                time = date_time_obj.time()
                # Formatting date as dd/mm/yyyy
                date = date.strftime("%d/%m/%Y")
                # Formatting time as h:min
                time = time.strftime("%H:%M")
            except KeyError:
                date = None
                time = None

            focal_devices_list = []
            try:
                focal_devices_references = target_entry["resource"]["focalDevice"]
                for entry in focal_devices_references:
                    focal_device_num = entry["manipulated"]["reference"].split("/")[-1]
                    try:
                        target_device_URL =  "urn:uuid:" + focal_device_num
                        traget_entry_device =  next((entry for entry in data.get("entry", []) if entry.get("fullUrl") == target_device_URL), None)
                        device_description = traget_entry_device["resource"]["type"]["coding"][0]["display"]
                    except KeyError:
                        device_description = None
                    focal_devices_list.append({
                        "reference_num": focal_device_num,
                        "device_description": device_description
                    })
            except KeyError:
                focal_devices_list = None

            procedures_list.append({
                "number": number,
                "description": description,
                "clinical_status": clinical_status,
                "date": date,
                "time": time,
                "focal_devices_list": focal_devices_list
            })

    return procedures_list

if __name__ == "__main__":
    procedures = main()
    print(procedures)