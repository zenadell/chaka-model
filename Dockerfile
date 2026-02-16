FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create a non-root user (required by Hugging Face Spaces)
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

# Hugging Face Spaces listens on port 7860
ENV PORT=7860

# Run the application using Gunicorn on port 7860
CMD ["gunicorn", "-b", "0.0.0.0:7860", "server:app"]
