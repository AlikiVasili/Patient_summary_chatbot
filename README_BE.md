Installation
1) Clone the repository to your local machine.
2) Ensure you have Python installed (version 3.6 or higher).
3) Install the required dependencies
4) Download the pre-trained BERT model and place it in the specified directory (./bioBert_model/bio_bert_classifier.pth).

Usage
1) Run the Flask application by executing python chatbot_app.py in your terminal.
2) Once the application is running, you can interact with the chatbot by sending HTTP POST requests to the /chat endpoint, providing the user message in JSON format.
	Example usage:
	curl -X POST -H "Content-Type: application/json" -d '{"message": "What are my current problems?"}' http://localhost:5000/chat

3)Receive responses from the chatbot containing relevant information based on the user's query.

Logging
1) Conversation logs are stored in the conversation_logs.txt file, including timestamps, user messages, and detected intents.
2) The logging mechanism aids in analyzing user interactions and system performance, facilitating further enhancements.

Feedback
1) Users can provide feedback to improve the system by sending CSV-formatted messages containing feedback type and text.
2) Feedback messages are processed, and appropriate actions are taken to incorporate user feedback into system enhancements.