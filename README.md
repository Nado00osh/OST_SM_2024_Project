# Intent-Based Energy Reduction Using Stream Mining

As energy consumption rises globally, the need for sustainable and efficient energy management systems becomes increasingly urgent. Conventional energy management systems are often limited by their inability to adapt dynamically to real-time fluctuations in usage and environmental factors. This project leverages stream mining and machine learning techniques to enable real-time adjustments in energy consumption, optimizing resource usage in response to user behavior and environmental conditions.

## Project System Architecture diagram

<img src="/SystemArchitecture.png" alt="System_Architecture" width="600">

## Features

- Stream processing using Apache Kafka and Apache Spark.
- Abnormal energy detection models: Gaussian Mixture Model, Isolation Forest, KMeans, and One-Class SVM.
- Data storage with InfluxDB.
- Real-time dashboards and visualizations with Grafana.
- Batch processing and model retraining for adaptive energy reduction.

## Getting Started

Follow the steps below to set up and run the project.

## Initialization

1. Run the following command in the root folder to start the necessary services:

./entrypoint.sh

This script will:
    - Install the required libraries and dependencies.
    - Launch the Docker containers using docker-compose.

2. After the containers are up, navigate to the Spark directory:
  cd spark
3. Run the Kafka feature extraction script:
  python3 kafka_to_features.py
4. Once the features are processed, you can run the desired model. Replace <model_name> with one of the available model scripts:
  python3 <model_name>.py
Example models include:
  - Gaussian_Mixture_Model.py
  - Isolation_Forest_Model.py
  - KMeans_Model.py
  - One_Class_SVM.py

#### Data storage
5. InfluxDB is used for storing the processed data. You can access its GUI at:

  - URL: http://localhost:8086
  - Default credentials:
  - Username: admin
  - Password: admin
After logging in, generate an all-access API token from the API Tokens section and save it securely.

#### Abnormal Energy Detection
6. We have implemented four abnormal energy detection models, all of which can be found in the models folder: **Gaussian Mixture Model, Isolation Forest, KMeans, and One-Class SVM.** The models consume data streams directly from Kafka, where they analyze patterns of energy consumption to identify deviations indicative of abnormal usage. Once the analysis is complete, the results are sent to InfluxDB for efficient storage and further analysis, enabling seamless integration with visualization tools like Grafana for real-time insights.

#### Visualization
7. Grafana is used for creating real-time dashboards. Access Grafana at:

  - URL: http://localhost:3000
  - Default credentials:
  - Username: admin
  - Password: admin

Add a new InfluxDB data source in Grafana:

  - Query language: Flux
  - URL: http://influxdb:8086
  - Organization: 
  - Token: Use the InfluxDB API token you generated earlier.
  - Default Bucket:

Save the data source and start building dashboards to visualize energy trends, detected abnormalities, and other metrics.

#### Final Notes
- Ensure that all .env variables (e.g., Kafka and InfluxDB configurations) are properly set before starting the services.
- The time range of stored data corresponds to the original timestamps from the CU-BEMS dataset. Set your dashboards to display this range for accurate visualizations.
- Check the visualizations folder for preconfigured Grafana.
