# Intent-Based Energy Reduction Using Stream Mining

As energy consumption rises globally, the need for sustainable and efficient energy management systems becomes increasingly urgent. Conventional energy management systems are often limited by their inability to adapt dynamically to real-time fluctuations in usage and environmental factors. This project leverages stream mining and machine learning techniques to enable real-time adjustments in energy consumption, optimizing resource usage in response to user behavior and environmental conditions.

## Project System Architecture diagram

<img src="/SystemArchitecture.png" alt="System_Architecture" width="600">

## Features

- Stream processing using Apache Kafka and Apache Spark.
- Abnormal energy detection models: Gaussian Mixture Model, Isolation Forest, KMeans, and One-Class SVM.
- Data storage with InfluxDB.
- Real-time dashboards and visualizations with Grafana.
- Batch processing and model pretraining for adaptive energy reduction.

## Getting Started

Follow the steps below to set up and run the project.


#### Setup and Initialization

1. **Start the Necessary Services**  
   Run the following command in the root folder to start the services:  
   ```bash  
   bash entrypoint.sh  
   ```  
   This script will:
   - Install the required Python libraries and dependencies from `requirements.txt` file.  
   - Launch the necessary Docker containers using the `docker-compose.yml` file.  
   - Initialize the Kafka producer to stream data from the CSV file to the Kafka cluster in real time.

2. **Run the Kafka Consumer for Data Processing**  
   Once the containers are up and running, run the Kafka consumer script to consume the data from Kafka for further processing in Spark:  
   ```bash  
   cd spark  
   python3 kafka_to_features.py  
   ```  
   This script will consume the data from Kafka and make it ready for processing in Spark.

3. **Run the Desired Model**  
   Once the data is consumed and processed, you can run any of the available models. Replace `<model_name>` with the model script you wish to use:  
   ```bash
   cd spark
   python3 <model_name>.py  
   ```  
   Example models include:  
   - `Gaussian_Mixture_Model.py`  
   - `Isolation_Forest_Model.py`  
   - `KMeans_Model.py`  
   - `One_Class_SVM.py`

#### Data storage
5. InfluxDB is used for storing the processed data. You can access its GUI at:

  - URL: http://localhost:8086
  - Default credentials:
  - Username: admin
  - Password: admin
After logging in, generate an all-access API token from the API Tokens section and save it securely.

#### Abnormal Energy Detection
6. We have implemented four abnormal energy detection models, all of which can be found in the Spark folder: **Gaussian Mixture Model, Isolation Forest, KMeans, and One-Class SVM.** The models consume data streams directly from Kafka, where they analyze patterns of energy consumption to identify deviations indicative of abnormal usage. Once the analysis is complete, the results are sent to InfluxDB for efficient storage and further analysis, enabling seamless integration with visualization tools like Grafana for real-time insights.

#### Visualization
7. Grafana is used for creating real-time dashboards. Access Grafana at:

  - URL: http://localhost:3000  
  - Default credentials:  
  - Username: admin  
  - Password: admin  

Add a new InfluxDB data source in Grafana:

  - Query language: InfluxQL
  - URL: http://influxdb:8086
  - Database: iber
  - user: admin
  - Password: admin

Save the data source and build dashboards to visualize energy trends, detect abnormalities, and other metrics.

## Conclusion

This project uses stream mining and machine learning to optimize real-time energy consumption by analyzing user behavior and environmental data. With Apache Kafka for data streaming, Apache Spark for processing, and machine learning models for abnormal energy detection, the system improves energy efficiency. InfluxDB stores the data, and Grafana provides real-time visualizations, enabling better decision-making for sustainable energy management.
