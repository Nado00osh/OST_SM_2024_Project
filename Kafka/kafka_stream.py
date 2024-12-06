from kafka import KafkaProducer
import csv
import time
import json
from datetime import datetime

# Kafka configuration
topic_name = 'spark_iber_data_stream'
kafka_broker = 'localhost:9092'

# Create a Kafka Producer instance
producer = KafkaProducer(
    bootstrap_servers=kafka_broker,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Path to the CSV file
csv_file = '../Data/test_data.csv'

# List of required features
features = ['Date','z1_AC2(kW)', 'z1_AC3(kW)', 'z1_Plug(kW)', 'z1_S1(RH%)', 'z1_S1(lux)',
            'z2_AC1(kW)', 'z2_Light(kW)', 'z2_Plug(kW)', 'z2_S1(RH%)', 'z2_S1(lux)',
            'z3_Light(kW)', 'z3_Plug(kW)', 'z4_AC1(kW)', 'z4_Light(kW)', 'z4_Plug(kW)',
            'z4_S1(RH%)', 'z4_S1(lux)', 'z5_AC1(kW)', 'z5_Light(kW)', 'z5_Plug(kW)',
            'z5_S1(RH%)']

# Function to clean data by validating and converting fields
def clean_data(row):
    cleaned_row = {}
    for feature in features:
        value = row.get(feature, '')  # Get the value for the feature
        if feature == 'Date':
            try:
                # Convert Date string to datetime object with time as well (Assumed format: YYYY-MM-DD HH:MM:SS)
                cleaned_row['Date'] = datetime.strptime(value, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
            except ValueError:
                cleaned_row['Date'] = None  # Handle invalid date format
        else:
            try:
                # Convert the value to float if valid, otherwise default to 0.0
                cleaned_row[feature] = float(value) if value else 0.0
            except ValueError:
                cleaned_row[feature] = 0.0  # Default to 0.0 for invalid values
    return cleaned_row

# Stream data row by row
with open(csv_file, 'r') as file:
    csv_reader = csv.DictReader(file)
    for row in csv_reader:
        # Clean the data before sending
        cleaned_row = clean_data(row)
        # Send the cleaned data to the Kafka topic
        producer.send(topic_name, value=cleaned_row)
        print(f"Sent: {cleaned_row}")  # Print the sent data for debugging
        time.sleep(0.1)  # Add a delay to simulate real-time streaming

# Close the Kafka producer
producer.close()
