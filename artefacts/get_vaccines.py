# Read the JSON file with tha patient summary
from dateutil import parser
import json

with open('patientSummary.json') as f:
    data = json.load(f)


def main():
    # Find the entry with resourceType "Composition"
    composition_entry = next(entry for entry in data["entry"] if entry["resource"]["resourceType"] == "Composition")

    # Find the section with title "vaccinations"
    vaccinations_section = next(section for section in composition_entry["resource"]["section"] if section["title"] == "History of Immunizations")

    # Extract entries inside the section
    vaccinations_entries = vaccinations_section["entry"]

    # Extract only the numbers from the references
    vaccinations_numbers = [entry["reference"].split("/")[-1] for entry in vaccinations_entries]

    vaccinations_list = []
    for number in vaccinations_numbers:
        target_fullUrl = "urn:uuid:" + number
                        
        # Find the entry with the specified fullUrl
        target_entry = next((entry for entry in data.get("entry", []) if entry.get("fullUrl") == target_fullUrl), None)

        code =  target_entry["resource"]["vaccineCode"]["coding"][0]["code"]

        # Check if coding_display is equal to specified values
        no_info_values = ["no-immunization-info","no-known-immunizations"]
        
        if not(code in no_info_values):
            vaccine = target_entry["resource"]["vaccineCode"]["coding"][0]["display"]
            try:
                protocol_applied = target_entry["resource"]["protocolApplied"]
                if protocol_applied and "targetDisease" in protocol_applied[0]:
                    target_disease = protocol_applied[0]["targetDisease"][0]["coding"][0]["display"]
                else:
                    target_disease = None  # or any default value you want to assign
            except KeyError as e:
                print("KeyError:", e)
                print("target_entry structure:", target_entry)
                raise  # Reraise the exception to stop the execution and see the printed information

            date_time = target_entry["resource"]["occurrenceDateTime"]
            date_time_obj = parser.parse(date_time)
            # Extracting date and time components
            date = date_time_obj.date()
            time = date_time_obj.time()
            # Formatting date as dd/mm/yyyy
            date = date.strftime("%d/%m/%Y")
            # Formatting time as h:min
            time = time.strftime("%H:%M")

            vaccinations_list.append({
                "number": number,
                "vaccine": vaccine,
                "target_disease": target_disease,
                "date": date,
                "time": time
            })

    return vaccinations_list

if __name__ == "__main__":
    vaccinations = main()
    print(vaccinations)