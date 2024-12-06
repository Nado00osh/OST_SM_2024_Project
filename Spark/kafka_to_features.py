from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_timestamp, lit
from kafka import KafkaConsumer
from json import loads
import json

if __name__ == "__main__":
    # Define the features list
    features = ['Date','z1_AC2(kW)', 'z1_AC3(kW)', 'z1_Plug(kW)', 'z1_S1(RH%)', 'z1_S1(lux)',
                'z2_AC1(kW)', 'z2_Light(kW)', 'z2_Plug(kW)', 'z2_S1(RH%)', 'z2_S1(lux)', 'z3_Light(kW)',
                'z3_Plug(kW)', 'z4_AC1(kW)', 'z4_Light(kW)', 'z4_Plug(kW)', 'z4_S1(RH%)', 'z4_S1(lux)',
                'z5_AC1(kW)', 'z5_Light(kW)', 'z5_Plug(kW)', 'z5_S1(RH%)']

    topic = 'spark_iber_data_stream'
    
    # Initialize Kafka consumer
    consumer = KafkaConsumer(
        topic,
        bootstrap_servers=['localhost:9092'],
        auto_offset_reset='earliest',
        api_version=(0, 10),
        enable_auto_commit=True,
        value_deserializer=lambda x: loads(x.decode('utf-8'))
    )
    print("Connection to Kafka established")
    
    # Spark session
    spark = SparkSession.builder \
        .appName("KafkaToFeatures") \
        .getOrCreate()

    for message in consumer:
        data = message.value
        
        # Create DataFrame from Kafka message data
        df = spark.createDataFrame([data])

        # Convert the 'Date' field to a timestamp (assuming it's in the 'YYYY-MM-DD HH:MM:SS' format)
        if 'Date' in data:
            try:
                df = df.withColumn('Date', to_timestamp(col('Date'), 'yyyy-MM-dd HH:mm:ss'))
            except Exception as e:
                print(f"Error in converting Date: {e}")
                df = df.withColumn('Date', lit(None))  # Set to None if conversion fails

        # Fill null values with 0.0 for all fields except for the DataFrame itself
        # We loop through features and convert to float if it's not 'Date'
        filtered_data = {}
        for feature in features:
            if feature != 'Date':  # We exclude 'Date' from the conversion
                filtered_data[feature] = float(data.get(feature, 0.0) if data.get(feature) is not None else 0.0)
            else:
                filtered_data[feature] = data.get(feature, None)  # Leave Date as it is

        # Save filtered data row-by-row to a temporary JSON file
        with open('filtered_data.json', 'a') as f:
            json.dump(filtered_data, f)
            f.write('\n')

        print(f"Filtered data saved: {filtered_data}")
