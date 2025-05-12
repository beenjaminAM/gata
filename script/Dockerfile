FROM mcr.microsoft.com/playwright/python:v1.52.0-noble

USER pwuser
WORKDIR /home/pwuser/app

# Copy required files
COPY requirements.txt .
COPY at.py .

# Install python dependencies
RUN pip install -r requirements.txt

# run script
CMD ["python", "./at.py"]