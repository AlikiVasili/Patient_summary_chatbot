# Patient_summary_chatbot
A chatbot that supports patient summary

In order to run the first version of the chatbot:
1) You have to finetune the bioBert or the Bert model using bioBert_finetune.py or bert_finetune.py (note: the chatbot_v1.py id build to search for bioBert model, in order to use a bert model you have to motify a little bit the code - uncomment the bert commands and comment out the bioBert ones)
2) The chatbot_v1.py is a console based version of the chatbot in order to run a test case you can use the id -> Identity-MI-1111
3) The files get_patient_sumamry.py, get_allergies.py etc are scripts that takes the neccessary information from a test database

To build your own flows:

You have to modify the chatbot_v1.py file and insead of call the scripts write the code that you want to be executed in every case

Datasets for training:
1) train.csv is a dataset build in order to finetune bert or bioBert models, it has inside 11 different categories (allergies, vaccinations. hello, feeling, surgery, implants, intolerances, current_problems, illness_history,info and prescription) - you can add examples of a new category and finetune the model to regognise more intents - to do so you have to modify the parameters inside the finetune files
2) train_shuffled.py is a shuffled version of the train.csv -  you can create a shuffled version of your training dataset by run the shuffle_datset.py file

Necessary libraries:
1) ast
2) os
3) torch
4) transformers -> (for Bert - BertModel, BertTokenizer, AdamW, get_linear_schedule_with_warmup), (for bioBert - AdamW, get_linear_schedule_with_warmup, AutoTokenizer, AutoModel)
5) sklearn
6) pandas
