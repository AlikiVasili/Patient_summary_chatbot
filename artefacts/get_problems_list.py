# Read the JSON file with tha patient summary
from dateutil import parser
import json

with open('patientSummary.json') as f:
    data = json.load(f)


def main():
    # Find the entry with resourceType "Composition"
    composition_entry = next(entry for entry in data["entry"] if entry["resource"]["resourceType"] == "Composition")

    # Find the section with title "Problem List"
    problems_section = next(section for section in composition_entry["resource"]["section"] if section["title"] == "Problem List")

    # Extract entries inside the section
    problems_entries = problems_section["entry"]

    # Extract only the numbers from the references
    problems_numbers = [entry["reference"].split("/")[-1] for entry in problems_entries]

    problems_list = []
    for number in problems_numbers:
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
                
            problems_list.append({
                "number": number,
                "description": description,
                "clinical_status": clinical_status,
                "severity": severity,
            })

    return problems_list

if __name__ == "__main__":
    problems = main()
    print(problems)