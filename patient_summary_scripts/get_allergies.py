# Read the JSON file with tha patient summary
import json

with open('patientSummary.json') as f:
    data = json.load(f)


def main():
    # Find the entry with resourceType "Composition"
    composition_entry = next(entry for entry in data["entry"] if entry["resource"]["resourceType"] == "Composition")

    # Find the section with title "Allergies and Intolerances"
    allergies_section = next(section for section in composition_entry["resource"]["section"] if section["title"] == "Allergies and Intolerances")

    # Extract entries inside the section
    allergies_entries = allergies_section["entry"]

    # Extract only the numbers from the references
    allergies_numbers = [entry["reference"].split("/")[-1] for entry in allergies_entries]

    allergies_list = []
    for number in allergies_numbers:
        target_fullUrl = "urn:uuid:" + number
                        
        # Find the entry with the specified fullUrl
        target_entry = next((entry for entry in data.get("entry", []) if entry.get("fullUrl") == target_fullUrl), None)

        code =  target_entry["resource"]["code"]["coding"][0]["code"]

        # Check if coding_display is equal to specified values
        no_info_values = ["no-allergy-info", "no-known-allergies", "no-known-medication-allergies", "no-known-environmental-allergies", "no-known-food-allergies"]
        
        if not(code in no_info_values):
            try:
                agent = target_entry["resource"]["code"]["coding"][0]["display"]
            except KeyError:
                agent = None
            try:
                clinical_status = target_entry["resource"]["clinicalStatus"]["coding"][0]["display"]
            except KeyError:
                clinical_status = None
            try:
                type = target_entry["resource"]["type"]
            except KeyError:
                type = None
            try:
                type_description = target_entry["resource"]["_type"]["extension"][0]["valueCodeableConcept"]["coding"][0]["display"]
            except KeyError:
                type_description = None
            # Check if "reaction" key and its nested structure exist
            if "reaction" in target_entry["resource"] and "manifestation" in target_entry["resource"]["reaction"]:
                # Access the first item in the list under "manifestation" and then access the "coding" key
                reaction = target_entry["resource"]["reaction"]["manifestation"][0].get("coding", [{}])[0].get("display", "No Reaction Display")
            else:
                reaction = "No Reaction"

            allergies_list.append({
                "number": number,
                "type": type,
                "type_description": type_description,
                "agent": agent,
                "clinical_status": clinical_status,
                "reaction": reaction
            })
            #allergies_list.append({"number": number, "type": type,"agent": agent,"clinical_status": clinical_status, "reaction": reaction})

    return allergies_list

if __name__ == "__main__":
    allergies = main()
    print(allergies)