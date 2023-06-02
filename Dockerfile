FROM selenium/standalone-chrome

USER root

# Update the package list and install Python
RUN apt-get update && \
    apt-get install -y python3 python3-pip

# Set the working directory
WORKDIR /app

# Copy your Python code into the container
COPY . /app

RUN pip3 install -r requirements.txt
# Set the command to run your Python script
# CMD ["python3", "your_script.py"]
