from flask import Flask, request, jsonify
from flask_cors import CORS
import ast
import os
import torch
from bioBert_model.bert_finetune import BERTClassifier
from transformers import AutoTokenizer
import subprocess
from fuzzywuzzy import fuzz

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

def find_allergy_category(user_input, category_keywords):
    # make the user input lower case
    user_input = user_input.lower()

    max_similarity = 0
    best_match = None

    # search to find the category with the biggest similarity
    for category, keywords in category_keywords.items():
        for keyword in keywords:
            similarity = fuzz.partial_ratio(user_input, keyword)
            if similarity > max_similarity:
                max_similarity = similarity
                best_match = category
    # If you did not find similarity bigger than 70 return None
    if max_similarity < 70:
        best_match = None

    return best_match

@app.route('/chat', methods=['POST'])
def chat():
    # Get the absolute path of the script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(script_dir, './bioBert_model/bio_bert_classifier.pth')
    # Load the saved model
    model = BERTClassifier(bert_model_name='dmis-lab/biobert-v1.1', num_classes=12)  # Initialize the model
    model.load_state_dict(torch.load(model_path))  # Load the saved model weights

    # Create a dictionary to map class indices to intent labels
    # the encoding is alphabetic 
    class_to_intent = {0: 'allergies',1: 'current_problems', 2: 'exit',3: 'feeling', 4: 'hello',5: 'illness_history', 6: 'implants', 7: 'info', 8: 'intolerances', 9: 'prescription'
                    ,10: 'surgery', 11: 'vaccination'}

    # Initialize the tokenizer
    tokenizer = AutoTokenizer.from_pretrained('dmis-lab/biobert-v1.1')
    #tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

    # Flag to track whether the user is logged in
    logged_in = False
    user_id = None
    patient_name = None
    patient_surname = None
    medical_id = None
    data = None

    user_message = request.json['message']

    # Tokenize user input
    inputs = tokenizer(user_message, return_tensors='pt', max_length=128, padding='max_length', truncation=True)
    # print(inputs)

    # Perform prediction
    with torch.no_grad():
        logits = model(input_ids=inputs['input_ids'], attention_mask=inputs['attention_mask'])
        top_k_values, top_k_indices = torch.topk(logits,k=2,dim=1)

    # Calculate the probabilities using softmax
    probabilities = torch.softmax(top_k_values, dim=1)
    # The top_k_indices now contains the indices of the top 2 predicted classes.
    # You can use these indices to retrieve the actual class labels or whatever you're predicting.
    predicted_class_1 = top_k_indices[:, 0]
    predicted_class_2 = top_k_indices[:, 1]
    # Now you have the top 2 predicted classes and their probabilities.
    # You can compare these probabilities to determine which one is more likely to be correct.
    probability_1 = probabilities[:, 0].item()
    probability_2 = probabilities[:, 1].item()
        
    confidence_threshold = 0.7
    no_inent_class = None

    # Compare probabilities to make a decision:
    if probability_1 > probability_2 and probability_1 > confidence_threshold:
        most_likely_class = predicted_class_1
        confidence = probability_1
    elif probability_2 > confidence_threshold:
        most_likely_class = predicted_class_2
        confidence = probability_2
    else:
        # No classified intent
        most_likely_class = None
        confidence = None
        if probability_1 > probability_2:
            no_inent_class = predicted_class_1
        else:
            no_inent_class = predicted_class_2

    bot_response = None
    # Check if a classified intent is found
    if most_likely_class is not None:
        # Map predicted class to intent label
        predicted_intent = class_to_intent[most_likely_class.item()]
        # Handle each intent differently
        if predicted_intent == 'allergies':
            # check if the user asked for a specific category
            # Define category keywords
            allergy_category_keywords = {
                "drug": ["drug", "drugs"],
                "food": ["food", "foods"],
                "substance": ["substance", "substances"]
            }
            category = find_allergy_category(user_message, allergy_category_keywords)

            # print the list of the allergies
            result = subprocess.run(['python', './patient_summary_scripts/get_allergies.py'], capture_output=True, text=True)

            # Check if the execution was successful
            if result.returncode == 0:
                # Safely evaluate the string as a literal to convert it to a list of dictionaries
                allergies = ast.literal_eval(result.stdout)

                # Filter allergies based on the recognized category
                if category is not None:
                    allergies = [entry for entry in allergies if category.lower() in entry['agent'].lower()]

                if not allergies:
                    bot_response = f"You have no allergies in the category {category}"
                else:
                    # Iterate through the entries and print only the 'agent'
                    i = 1
                    bot_response = "\nYou have the following allergies:"
                    for entry in allergies:
                        if entry['type'] == "allergy":
                            if entry['reaction'] == "No Reaction":
                                bot_response += f"\n{i}. {entry['type_description']} in {entry['agent']} (Clinical status: {entry['clinical_status']})"
                                i += 1
                            else:
                                bot_response += f"\n{i}. {entry['type_description']} in {entry['agent']}, Reaction: {entry['reaction']} (Clinical status: {entry['clinical_status']})"
                                i += 1
                    i = 1
                    bot_response += "\n\n"
                    bot_response +="\nYou have the following intolerances:"
                    for entry in allergies:
                        if entry['type'] == "allergy":
                            if entry['reaction'] == "No Reaction":
                                bot_response += f"\n{i}. {entry['type_description']} in {entry['agent']} (Clinical status: {entry['clinical_status']})"
                                i += 1
                            else:
                                bot_response += f"\n{i}. {entry['type_description']} in {entry['agent']}, Reaction: {entry['reaction']} (Clinical status: {entry['clinical_status']})"
                                i += 1
        elif predicted_intent == 'current_problems':
            # print the list of the current problems
            result = subprocess.run(['python', './patient_summary_scripts/get_problems_list.py'], capture_output=True, text=True)

            # Check if the execution was successful
            if result.returncode == 0:
                # Safely evaluate the string as a literal to convert it to a list of dictionaries
                problems = ast.literal_eval(result.stdout)

                # Iterate through the entries and print them
                i = 1
                bot_response = "Your have the following problems:"
                for entry in problems:
                    bot_response += f"\n{i}. {entry['description']}, Severity: {entry['severity']}, (Status: {entry['clinical_status']})"
                    i = i + 1
            else:
                # Print an error message
                bot_response = "Error occurred while running the script."
                bot_response += f"\nError message: {result.stderr}"

        elif predicted_intent == 'feeling':
            bot_response = "I am perfect! Hope you are too!"

        elif predicted_intent == 'hello':
            bot_response = "Hello! Tell me how I can assist you."

        elif predicted_intent == 'illness_history':
            # print the list of the illness history
            result = subprocess.run(['python', './patient_summary_scripts/get_history_of_illness.py'], capture_output=True, text=True)

            # Check if the execution was successful
            if result.returncode == 0:
                # Safely evaluate the string as a literal to convert it to a list of dictionaries
                illness = ast.literal_eval(result.stdout)

                # Iterate through the entries and print them
                i = 1
                bot_response = "Your history of illness is:"
                for entry in illness:
                    bot_response = f"\n{i}. {entry['description']}, Severity: {entry['severity']}, Period: {entry['onset_date']}({entry['onset_time']}) - {entry['end_date']}({entry['end_time']}), (Status: {entry['clinical_status']})"
                    i = i + 1
            else:
                # Print an error message
                bot_response = "Error occurred while running the script."
                bot_response += f"\nError message: {result.stderr}"

        elif predicted_intent == 'implants':
            # print the list of the implants
            result = subprocess.run(['python', "./patient_summary_scripts/get_procedures.py"], capture_output=True, text=True)

            # Check if the execution was successful
            if result.returncode == 0:
                # Safely evaluate the string as a literal to convert it to a list of dictionaries
                procedures = ast.literal_eval(result.stdout)

                # Iterate through the entries and print them
                i = 1
                implants = []
                for entry in procedures:
                    if entry["focal_devices_list"] != None:
                        for focal_device in entry["focal_devices_list"]:
                            if ('implant' in focal_device["device_description"].lower()) or ('implantable' in focal_device["device_description"].lower()):
                                implants.append({
                                    "number": entry['number'],
                                    "description": entry['description'],
                                    "clinical_status": entry['clinical_status'],
                                    "date": entry['date'],
                                    "time": entry['time'],
                                    "focal_devices_list": entry['focal_devices_list']
                                })
                    i = i + 1
                    
                if implants:
                    i = 1
                    bot_response = "You have the following implants:"
                    for entry in implants:
                        bot_response += f"\n{i}. "
                        for focal_device in entry["focal_devices_list"]:
                            bot_response += f"{focal_device['device_description']}, "
                        bot_response += f"Surgery: {entry['description']}, Date/Time: {entry['date']}, {entry['time']}"
                        i = i + 1
                else:
                    bot_response = "You do not have any implants!"
            else:
                # Print an error message
                bot_response = "Error occurred while running the script."
                bot_response += f"\nError message: {result.stderr}"

        elif predicted_intent == 'info':
            bot_response = "I can answer any question related to your personal medical history. In medical history documents you can find information about allergies, vaccination, surgeries, medical devices, implants, current problems and past illnesses. Also you can see your prescriptions. "

        elif predicted_intent == 'intolerances':
            # print the list of the intolerances
            result = subprocess.run(['python', './patient_summary_scripts/get_allergies.py'], capture_output=True, text=True)

            # Check if the execution was successful
            if result.returncode == 0:
                # Safely evaluate the string as a literal to convert it to a list of dictionaries
                allergies = ast.literal_eval(result.stdout)

                # Iterate through the entries and print only the 'agent'
                i = 1
                bot_response = "\nYou have the following intolerances:"
                for entry in allergies:
                    if entry['type'] == "intolerance":
                        if entry['reaction'] == "No Reaction":
                            bot_response += f"\n{i}. {entry['type_description']} in {entry['agent']} (Clinical status: {entry['clinical_status']})"
                            i = i + 1
                        else:
                            bot_response += f"\n{i}. {entry['type_description']} in {entry['agent']}, Reaction: {entry['reaction']} (Clinical status: {entry['clinical_status']})"
                            i = i + 1
                print("")
            else:
                # Print an error message
                bot_response = "Error occurred while running the script."
                bot_response += f"\nError message: {result.stderr}"

        elif predicted_intent == 'prescription':
            # print the list of the prescriptions/medication
            result = subprocess.run(['python', './patient_summary_scripts/get_medication.py'], capture_output=True, text=True)

            # Check if the execution was successful
            if result.returncode == 0:
                # Safely evaluate the string as a literal to convert it to a list of dictionaries
                medications = ast.literal_eval(result.stdout)

                # Iterate through the entries and print only the 'agent'
                i = 1
                bot_response = "\nYou have the following prescriptions for medication:"
                for entry in medications:
                    bot_response += f"\n{i}. {entry['product_name']}, {entry['product_packageSizeUnit']}, {entry['product_description']}"
                    bot_response += f"\n    General Instructions: {entry['general_instructions']}, Patient Instructions: {entry['patient_instructions']}"
                    bot_response += f"\n    Duration: {entry['bounds_duration_value']} per {entry['bounds_duration_unit']} for {entry['period']} {entry['period_unit']}"
                    bot_response += f"\n   Use: {entry['route']}\n"
                    i = i + 1
            else:
                # Print an error message
                bot_response = "Error occurred while running the script."
                bot_response += f"\nError message: {result.stderr}"

        elif predicted_intent == 'surgery':
            # print the list of the surgeries/procedures
            result = subprocess.run(['python', './patient_summary_scripts/get_procedures.py'], capture_output=True, text=True)

            # Check if the execution was successful
            if result.returncode == 0:
                # Safely evaluate the string as a literal to convert it to a list of dictionaries
                procedures = ast.literal_eval(result.stdout)

                # Iterate through the entries and print them
                i = 1
                bot_response = "You have done the following procedures:"
                for entry in procedures:
                    bot_response += f"\n{i}. {entry['description']} - "
                    for focal_device in entry["focal_devices_list"]:
                        bot_response += f"{focal_device['device_description']}, "
                    bot_response += f"(Status: {entry['clinical_status']}), Date and time: {entry['date']}, {entry['time']}\n"
                    i = i + 1
            else:
                # Print an error message
                bot_response = "Error occurred while running the script."
                bot_response += f"\nError message: {result.stderr}"

        elif predicted_intent == 'vaccination':
            # print the list of the vaccinations
            result = subprocess.run(['python', './patient_summary_scripts/get_vaccines.py'], capture_output=True, text=True)

            # Check if the execution was successful
            if result.returncode == 0:
                # Safely evaluate the string as a literal to convert it to a list of dictionaries
                vaccines = ast.literal_eval(result.stdout)

                # Iterate through the entries and print them
                i = 1
                bot_response = "You have done the following vaccines:"
                for entry in vaccines:
                    if entry['target_disease'] == None:
                        bot_response += f"{i}. {entry['vaccine']}, Date and time: {entry['date']}, {entry['time']}"
                    else:
                        bot_response += f"{i}. {entry['vaccine']}, Date and time: {entry['date']}, {entry['time']} (Target Disease: {entry['target_disease']})"
                    i = i + 1
            else:
                # Print an error message
                bot_response = "Error occurred while running the script."
                bot_response += f"\nError message: {result.stderr}"

        elif predicted_intent == 'exit':
            bot_response = "I hope that i was helpful! Bye bye!"
        else:
            # Handle the case when there is no classified intent
            if no_inent_class != None:
                bot_response = "I am not quite sure that I understand what you want!"
                bot_response += f'Do you may mean {class_to_intent[no_inent_class.item()]}? If yes write this {class_to_intent[no_inent_class.item()]} otherwise try again to tell me what you are looking for.'

    else:
        bot_response = "Intent not recognized. Please try again."

    return jsonify({'response': bot_response})

if __name__ == '__main__':
    app.run(debug=True)
