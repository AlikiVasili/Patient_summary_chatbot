# Use an official Python runtime as a parent image
FROM python:3.12.3-slim

# Set the working directory in the container
WORKDIR /app

COPY requirements.txt requirements.txt

# Install any needed dependencies specified in requirements.txt
RUN pip install -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app

# Expose the Flask port
EXPOSE 5000

# Define environment variable
ENV FLASK_APP=chatbot_app.py

# Run flask app when the container launches
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
