echo "Running Docker"
docker-compose up -d

#####
echo "Installing Python libraries"
if [ -f requirements.txt ]; then
    echo "requirements.txt found. Installing packages..."
    pip install -r requirements.txt
else
    echo "requirements.txt not found. Skipping library installation."
fi

#####

echo "Starting kafka"
cd Kafka
python3 kafka_stream.py   #   Run Kafka in the background

