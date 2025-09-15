# Use slim Python base image
FROM python:3.11-slim-bookworm

# Set working directory
WORKDIR /app

# Copy everything into container
COPY . /app

# Install dependencies
RUN apt-get update -y && \
    apt-get install -y awscli && \
    pip install --no-cache-dir -r requirements.txt

# Expose Streamlit port
EXPOSE 8501

# Run Streamlit app
CMD ["streamlit", "run", "interview_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
