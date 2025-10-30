# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
# This is done first to leverage Docker's build cache:
# If requirements.txt doesn't change, Docker won't re-install packages.
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code (e.g., app.py)
COPY . .

# Expose the port that Streamlit runs on
EXPOSE 8501

# Run the Streamlit app when the container launches
# --server.address=0.0.0.0 ensures it's accessible from outside the container
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]

