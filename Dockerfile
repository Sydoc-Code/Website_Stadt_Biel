# Dockerfile

# 1. Use an official Python runtime as a parent image
FROM python:3.11-slim

# 2. Install system dependencies for the MS ODBC Driver
# This is the key part that fixes the pyodbc issue
RUN apt-get update && apt-get install -y curl gnupg unixodbc-dev

# 3. Add Microsoft's official repository and install the driver
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list
RUN apt-get update
RUN ACCEPT_EULA=Y apt-get install -y msodbcsql18

# 4. Set the working directory in the container
WORKDIR /app


# 6. Copy your application code into the container
COPY . .
