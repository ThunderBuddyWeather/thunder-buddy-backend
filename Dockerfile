# Use the official Python 3.12 slim image as the base.
# The slim version reduces the overall image size.
FROM python:3.12-slim

# Install curl and wget for healthchecks
RUN apt-get update && apt-get install -y curl wget && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container.
# All subsequent commands run within this directory.
WORKDIR /app

# Copy the requirements file into the container.
# This file lists all the Python dependencies your app requires.
COPY requirements.txt .

# Copy the .env.ci file into the container.
COPY .env.ci .

# Install Python dependencies specified in requirements.txt.
# The --no-cache-dir flag prevents pip from caching package downloads,
# which helps reduce the final image size.
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files first
COPY main.py .
COPY scripts/ scripts/
COPY tests/ tests/

# Create static directory and ensure it exists
RUN mkdir -p static && \
  echo "Created static directory at:" && \
  pwd && \
  ls -la

# Generate swagger.yaml during build with verbose output
RUN echo "Generating swagger.yaml..." && \
  python -v scripts/generate_swagger.py && \
  echo "Checking generated files:" && \
  ls -la static/ && \
  if [ -f static/swagger.yaml ]; then \
  echo "swagger.yaml was generated successfully" && \
  cat static/swagger.yaml | head -n 5 && \
  # Ensure proper permissions
  chmod 644 static/swagger.yaml && \
  # Make a backup copy
  cp static/swagger.yaml static/swagger.yaml.bak; \
  else \
  echo "swagger.yaml was not generated!" && \
  exit 1; \
  fi

# Create a volume for the static directory
VOLUME ["/app/static"]

# Expose port 5000 so that the container listens on this port at runtime.
EXPOSE 5000

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1 \
  FLASK_ENV=development \
  FLASK_DEBUG=1 \
  DB_HOST=db \
  DB_PORT=5432 \
  DB_NAME=thunderbuddy \
  DB_USERNAME=thunderbuddy \
  DB_PASSWORD=localdev \
  DATABASE_URL=postgresql://thunderbuddy:localdev@db:5432/thunderbuddy

# Copy the static files to a safe location and create an entrypoint script
RUN echo '#!/bin/sh\n\
  # Copy source files from mounted volume\n\
  if [ -d /src ]; then\n\
  echo "Copying source files from /src..."\n\
  cp -f /src/main.py /app/\n\
  cp -rf /src/scripts /app/\n\
  cp -rf /src/tests /app/\n\
  fi\n\
  if [ ! -f /app/static/swagger.yaml ] && [ -f /app/static/swagger.yaml.bak ]; then\n\
  echo "Restoring swagger.yaml from backup..."\n\
  cp /app/static/swagger.yaml.bak /app/static/swagger.yaml\n\
  fi\n\
  if [ ! -f /app/static/swagger.yaml ]; then\n\
  echo "Generating swagger.yaml..."\n\
  python scripts/generate_swagger.py\n\
  fi\n\
  exec python main.py\n' > /app/entrypoint.sh && \
  chmod +x /app/entrypoint.sh

# Set the container's entrypoint to our new script
ENTRYPOINT ["/app/entrypoint.sh"]

# Define default arguments to the ENTRYPOINT via CMD.
# Using an empty array (CMD []) here is a best practice, as it allows you
# to override or add additional arguments at runtime without changing the ENTRYPOINT.
CMD []
