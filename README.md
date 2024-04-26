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

## Backend
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

## Frontend

# CareSnap Chatbot Frontend

## Introduction

Welcome to the CareSnap Chatbot frontend! This document provides an overview of the frontend structure and functionality.

## Table of Contents

- [CareSnap Chatbot Frontend](#caresnap-chatbot-frontend)
  - [Introduction](#introduction)
  - [Table of Contents](#table-of-contents)
  - [Description](#description)
  - [Instructions](#instructions)
  - [Test User](#test-user)
  - [Questionnaire](#questionnaire)
  - [Feedback](#feedback)
  - [Chat Container](#chat-container)
  - [Footer](#footer)
  - [Scripts](#scripts)

## Description

This frontend is designed to interact with the CareSnap Chatbot, a healthcare chatbot system. It consists of various sections, including About, Instructions, Test User, Questionnaire, and Feedback.

## Instructions

The Instructions section provides guidance on how to use the chatbot. It includes steps to initiate a conversation with the chatbot, such as copying the provided ID, opening the chatbot, pasting the ID, and logging in.

## Test User

The Test User section allows users to test the chatbot using a predefined ID. By providing the ID, users can log in as a test user (e.g., Maria Iosif) and interact with the chatbot.

## Questionnaire

The Questionnaire section prompts users to complete a questionnaire after testing the chatbot. Users can provide feedback on their experience, including comments, suggestions, or reporting problems.

## Feedback

The Feedback section enables users to submit feedback directly through the frontend. Users can select the type of feedback (comments, suggestions, or problems) and provide their input in the text area.

## Chat Container

The Chat Container is a component that contains the chat interface for interacting with the chatbot. It includes a form for logging in with a patient ID, sending messages to the chatbot, and displaying the chat history.

## Footer

The Footer section displays copyright information for the CareSnap Chatbot.

## Scripts

The frontend includes JavaScript scripts for handling user interactions, such as submitting feedback, logging in, sending messages to the chatbot, and toggling the chat container's visibility.
