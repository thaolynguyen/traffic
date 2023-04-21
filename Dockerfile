FROM python:3.11-slim
EXPOSE 8181
# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

# Copy local code to the container image.
WORKDIR $traffic-generator
COPY . ./

# Install production dependencies.
RUN pip3 install -r requirements.txt

CMD [ "python", "./main.py"]