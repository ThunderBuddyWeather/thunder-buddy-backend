# Use the official Python 3.12 slim image as the base.
# The slim version reduces the overall image size.
FROM python:3.12-slim

# Set the working directory inside the container.
# All subsequent commands run within this directory.
WORKDIR /app

# Copy the requirements file into the container.
# This file lists all the Python dependencies your app requires.
COPY requirements.txt .

# Install Python dependencies specified in requirements.txt.
# The --no-cache-dir flag prevents pip from caching package downloads,
# which helps reduce the final image size.
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY main.py .
COPY scripts/ scripts/

# Expose port 5000 so that the container listens on this port at runtime.
EXPOSE 5000

# Add build argument for database URL
ARG DATABASE_URL
ENV DATABASE_URL=${DATABASE_URL}

# Add additional environment variables
ENV DB_HOST=db
ENV DB_PORT=5432
ENV DB_NAME=thunderbuddy
ENV DB_USER=thunderbuddy
ENV DB_PASSWORD=localdev

# Set the container's entrypoint to run your application.
# ENTRYPOINT enforces that the command will always be run.
ENTRYPOINT ["python", "main.py"]

# Define default arguments to the ENTRYPOINT via CMD.
# Using an empty array (CMD []) here is a best practice, as it allows you
# to override or add additional arguments at runtime without changing the ENTRYPOINT.
CMD []
