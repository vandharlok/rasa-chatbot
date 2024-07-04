FROM python:3.8.19-slim

# Install GCC compiler and other dependencies
RUN apt-get update && apt-get install -y build-essential

# Copy requirements file and install dependencies
COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN python -m pip install rasa 
# Update pip to the latest version
# Install Rasa and other dependencies
RUN pip install -r requirements.txt
RUN pip install https://github.com/explosion/spacy-models/releases/download/pt_core_news_md-3.7.0/pt_core_news_md-3.7.0.tar.gz

# Copy the rest of the application files
COPY . /app

# Train the model
RUN rasa train

# Switch to a non-root user if necessary (ensure UID 1001 is correct for your environment)
USER root

# Expose the port that Rasa will run on
EXPOSE 5005
EXPOSE 5055

ENTRYPOINT [ "rasa" ]

# Run the Rasa server
CMD ["run", "--enable-api", "--cors", "*"]