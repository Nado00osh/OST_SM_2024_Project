import time
from pyspark.sql import SparkSession
from influxdb_client import InfluxDBClient, Point, WritePrecision
import json
from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import datetime
import pandas as pd

# InfluxDB connection setup
org = "elte"
username = 'admin'
password = 'admin'
database = 'iber'
retention_policy = 'autogen'
bucket = f'{database}/{retention_policy}'

# Initialize InfluxDB client for writing data
with InfluxDBClient(url="http://localhost:8086", token=f'{username}:{password}', org='-', bucket=bucket) as client:
    write_api = client.write_api(write_options=SYNCHRONOUS)

    # Initialize Spark session
    spark = SparkSession.builder \
        .appName("PredictAndStoreToInflux") \
        .getOrCreate()

    # Function to check if new data is appended to the JSON file
    def read_new_data(file_path, last_line_position):
        new_data = []
        try:
            with open(file_path, 'r') as file:
                file.seek(last_line_position)  # Start reading from the last known position
                lines = file.readlines()  # Read all new lines since the last position
                if lines:
                    new_data = [json.loads(line) for line in lines]  # Parse each line as JSON
                    last_line_position = file.tell()  # Update last read position to the end of the file
        except FileNotFoundError:
            pass
        return new_data, last_line_position

    # Function to aggregate energy consumption for each zone based on the season
    def aggregate_data(data_batch):
        # Define the zones and their respective devices
        zone_devices = {
            'z1': ['z1_AC2(kW)', 'z1_AC3(kW)', 'z1_Plug(kW)'],
            'z2': ['z2_AC1(kW)', 'z2_Light(kW)', 'z2_Plug(kW)'],
            'z3': ['z3_Light(kW)', 'z3_Plug(kW)'],
            'z4': ['z4_AC1(kW)', 'z4_Light(kW)', 'z4_Plug(kW)'],
            'z5': ['z5_AC1(kW)', 'z5_Light(kW)', 'z5_Plug(kW)']
        }

        # Initialize a dictionary to store the energy consumption for each zone by season
        season_zone_energy = {
            'spring': {zone: 0.0 for zone in zone_devices},
            'summer': {zone: 0.0 for zone in zone_devices},
            'autumn': {zone: 0.0 for zone in zone_devices},
            'winter': {zone: 0.0 for zone in zone_devices}
        }

        # Iterate through data and calculate energy consumption based on the season and zone
        for data in data_batch:
            if 'Date' in data:
                try:
                    # Extract the month from 'Date' field (ensure it's in the correct format)
                    date = datetime.strptime(data['Date'], '%Y-%m-%d %H:%M:%S')
                    month = date.month  # Extract month
                except Exception as e:
                    print(f"Error parsing Date: {e}")
                    continue  # Skip this data point if Date is invalid
            else:
                continue  # Skip this data point if Date is missing

            # Iterate through each zone and calculate the total energy consumption for each zone
            for zone, devices in zone_devices.items():
                zone_energy = sum([data.get(device, 0.0) for device in devices])  # Sum energy for all devices in the zone

                # Assign the energy consumption to the appropriate season
                if 3 <= month <= 5:  # Spring
                    season_zone_energy['spring'][zone] += zone_energy
                elif 6 <= month <= 8:  # Summer
                    season_zone_energy['summer'][zone] += zone_energy
                elif 9 <= month <= 11:  # Autumn
                    season_zone_energy['autumn'][zone] += zone_energy
                else:  # Winter
                    season_zone_energy['winter'][zone] += zone_energy

        return season_zone_energy

    # Function to read, process, and store data in InfluxDB with aggregation
    def process_and_store_data(file_path):
        last_line_position = 0  # Initially, set position to the start of the file
        no_new_data_count = 0  # Counter for how many cycles no new data is found
        data_batch = []  # Batch of data for aggregation
        aggregation_window_size = 10  # Number of data points to aggregate before sending to InfluxDB
        
        while True:
            new_data, last_line_position = read_new_data(file_path, last_line_position)

            if new_data:
                no_new_data_count = 0
                for data in new_data:
                    # Do not remove the 'Date' field; just store it as part of the data
                    date = data.get('Date', None)

                    # Ensure that all the features are processed and stored correctly
                    feature_values = [data[feature] for feature in data.keys()]
                    
                    # Convert the data to a pandas DataFrame to match the feature names
                    feature_array = pd.DataFrame([feature_values], columns=["z1_AC2(kW)", "z1_AC3(kW)", "z1_Plug(kW)", "z1_S1(RH%)", "z1_S1(lux)",
                                                                             "z2_AC1(kW)", "z2_Light(kW)", "z2_Plug(kW)", "z2_S1(RH%)", "z2_S1(lux)",
                                                                             "z3_Light(kW)", "z3_Plug(kW)", "z4_AC1(kW)", "z4_Light(kW)", "z4_Plug(kW)",
                                                                             "z4_S1(RH%)", "z4_S1(lux)", "z5_AC1(kW)", "z5_Light(kW)", "z5_Plug(kW)", "z5_S1(RH%)"])

                    # Add back the 'Date' to the data for aggregation
                    if date:
                        data['Date'] = date
                    
                    data_batch.append(data)

                    if len(data_batch) >= aggregation_window_size:
                        aggregated_data = aggregate_data(data_batch)

                        # Write the aggregated data for each season and zone to InfluxDB
                        for season, season_data in aggregated_data.items():
                            point = Point("aggregated_abnormal_data").tag("bucket", bucket).tag("season", season)
                            for zone, energy in season_data.items():
                                point = point.field(f'{zone}_energy_kW', energy)

                            write_api.write(bucket=bucket, org=org, record=point)
                            print(f"Aggregated data sent to InfluxDB for {season}: {point}")

                        data_batch = []

            else:
                no_new_data_count += 1

            time.sleep(10)

            if no_new_data_count > 0:
                print("No new data for the last 10 seconds. Exiting.")
                break

    # Start processing and storing data
    file_path = '../../Spark/filtered_data.json'
    process_and_store_data(file_path)
