# Stage 1: Build the package
FROM python:3.11 as builder

WORKDIR /librairies

# Copy the source code to the container
COPY ./librairies/pythonmodels /librairies/pythonmodels

WORKDIR /librairies/pythonmodels

# Build the package
RUN python setup.py bdist_wheel


# Stage 2: Create the final image
FROM python:3.11

WORKDIR /app

RUN mkdir /etc/librairies
# Copy the built wheel file from the previous stage
COPY --from=builder /librairies/pythonmodels/dist/*.whl /etc/librairies/pythonmodels/

# Install the wheel file
RUN pip install /etc/librairies/pythonmodels/*.whl

COPY ./services/checker/requirements.txt /etc/librairies

RUN pip install -r /etc/librairies/requirements.txt
# Copy the source code to the container

COPY ./services/checker/src/ /app

# Run the application
# CMD ["sleep" , "2073600"]
CMD [ "python", "app.py"]

