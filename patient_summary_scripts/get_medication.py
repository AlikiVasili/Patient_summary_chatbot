# Read the JSON file with tha patient summary
from dateutil import parser
import json

with open('patientSummary.json') as f:
    data = json.load(f)


def main():
    # Find the entry with resourceType "Composition"
    composition_entry = next(entry for entry in data["entry"] if entry["resource"]["resourceType"] == "Composition")

    # Find the section with title "medication"
    medication_section = next(section for section in composition_entry["resource"]["section"] if section["title"] == "Medication List")

    # Extract entries inside the section
    medication_entries = medication_section["entry"]

    # Extract only the numbers from the references
    medication_numbers = [entry["reference"].split("/")[-1] for entry in medication_entries]

    medication_list = []
    for number in medication_numbers:
        target_fullUrl = "urn:uuid:" + number
                        
        # Find the entry with the specified fullUrl
        target_entry = next((entry for entry in data.get("entry", []) if entry.get("fullUrl") == target_fullUrl), None)
        
        try:
            medication_reference = target_entry["resource"]["medicationReference"]
        except KeyError:
            medication_reference = None
        try:
            date_time = target_entry["resource"]["authoredOn"]
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
        try:
            dosageInstruction = target_entry["resource"]["dosageInstruction"]
            if dosageInstruction and "text" in dosageInstruction[0]:
                    instructions = dosageInstruction[0]["text"]
            else:
                instructions = None  # or any default value you want to assign

            if dosageInstruction and "patientInstruction" in dosageInstruction[0]:
                    patient_instructions = dosageInstruction[0]["patientInstruction"]
            else:
                patient_instructions = None  # or any default value you want to assign

            if dosageInstruction and "timing" in dosageInstruction[0]:
                    period = dosageInstruction[0]["timing"]["repeat"]["period"]
                    period_unit = dosageInstruction[0]["timing"]["repeat"]["periodUnit"]
                    bounds_duration_value = dosageInstruction[0]["timing"]["repeat"]["boundsDuration"]["value"]
                    bounds_duration_unit = dosageInstruction[0]["timing"]["repeat"]["boundsDuration"]["unit"]
            else:
                period = None  # or any default value you want to assign
                period_unit = None
                bounds_duration_value = None
                bounds_duration_unit = None

            if dosageInstruction and "route" in dosageInstruction[0]:
                    route = dosageInstruction[0]["route"]["coding"][0]["display"]
            else:
                route = None  # or any default value you want to assign

            # Get medication info
            medication_number = medication_reference["reference"].split("/")[-1]
            medication_fullUrl = "urn:uuid:" + medication_number
                        
            # Find the entry with the specified fullUrl
            metication_entry = next((entry for entry in data.get("entry", []) if entry.get("fullUrl") == medication_fullUrl), None)
            resource = metication_entry.get('resource', {})
            extension = resource.get('extension', [{}])[1].get('extension', [])
            try:
                product_name = next((ext['valueString'] for ext in extension if ext.get('url') == 'productName'), None)
            except KeyError:
                product_name = None
            try:
                product_strength = next((ext['valueString'] for ext in extension if ext.get('url') == 'strength'), None)
            except KeyError:
                product_strength = None
            try:
                product_description = next((ext['valueString'] for ext in extension if ext.get('url') == 'description'), None)
            except KeyError:
                product_description = None
            try:
                product_packageSizeUnit = next((ext['valueString'] for ext in extension if ext.get('url') == 'packageSizeUnit'), None)
            except KeyError:
                product_packageSizeUnit = None

        except KeyError as e:
            print("KeyError:", e)
            print("target_entry structure:", target_entry)
            raise  # Reraise the exception to stop the execution and see the printed information

        medication_list.append({
            "number": number,
            "med_ref": medication_reference,
            "product_name": product_name,
            "product_strength": product_strength,
            "product_description": product_description,
            "product_packageSizeUnit": product_packageSizeUnit,
            "authored_date": date,
            "authored_time": time,
            "general_instructions": instructions,
            "patient_instructions": patient_instructions,
            "period": period,
            "period_unit": period_unit,
            "bounds_duration_value": bounds_duration_value,
            "bounds_duration_unit": bounds_duration_unit,
            "route": route
        })

    return medication_list

if __name__ == "__main__":
    medication = main()
    print(medication)