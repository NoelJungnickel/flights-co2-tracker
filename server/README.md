# Flight Tracker Python Backend

This directory contains the backend on the Flight CO2 Tracker and is designed to be hosted in the cloud. The backend is currently hosted at `http://35.210.64.77:8000` in a GCP Virtual Machine.
For retrieving flight data, we use the real-time data provided by the Opensky Network: `https://opensky-network.org`
Detailed information about them can be found on their website and in the original OpenSky paper.
```
Matthias Schäfer, Martin Strohmeier, Vincent Lenders, Ivan Martinovic and Matthias Wilhelm.
"Bringing Up OpenSky: A Large-scale ADS-B Sensor Network for Research".
In Proceedings of the 13th IEEE/ACM International Symposium on Information Processing in Sensor Networks (IPSN), pages 83-94, April 2014.
```
For our carbon computation, we also rely on a Flight Fuel Consumption API, which can be further investigated via `https://despouy.ca/flight-fuel-api/`

At the moment, we compute carbon emissions within the airspaces of Berlin, Paris, London and Madrid and for a handful of celebrities defined in `main.py`. To make carbon computations with different airspaces or celebrities, you can just edit the `BOUNDING_BOXES` and `CELEB_AIRCRAFTS` variables there and provide the necessary data (airspace coordinates or icao24 codes of celebrity jets) in the way specified.

## General Code Structure

The Backend consists of the following python files:
- `database.py`: Provides an abstract class `Database` that defines the required functions for interacting with the carbon emission data storage. The `RedisDatabase` class implements these functions using Redis as the storage backend.
- `opensky_network.py`: Contains functions to fetch aircraft states and flight data from the OpenSky Network API.
- `flight_fuel_consumption_api.py` Provides a function to query the Flight Fuel Consumption API and retrieve the fuel consumption data for flights given specific aircraft data.
- `carbon_computation.py`: Contains the `StateCarbonComputation` class, which calculates the total carbon emissions in a specific airspace based on aircraft states. It maintains airspace data with state vectors and computes the distance traveled by each aircraft after receiving a new state vector from the OpenSky Network API. It also provides methods to estimate the CO2 emissions based on the fuel consumption rate. It also contains a basic function to compute the carbon emission based on the traveled distance using the Flight Fuel Consumption API.
- `main.py`: Acts as the entry point and handles the initialization of components, scheduling of jobs, and command-line argument parsing utilizing worker threads to perform the carbon computations and data storage jobs concurrently. Jobs currently include retrieving data from OpenSky and performing carbon computation on airstates in our airspaces every minute, aggregating that value in the database. Additionally, the total value is stored separately every hour and flight data of specific planes is retrieved every hour for computing celebrity emissions.
- `server_api.py`: This file sets up a FastAPI application to serve as the server-side API. It interacts with the database and exposes several endpoints to retrieve information about the airspaces, total carbon emissions, and carbon emission data over time. Currently, the following endpoints are provided:
    - `/api/serverstart`: Retrieves the startup time of the server.
        ```
        {
            "timestamp": 1688570053
        }
        ```
    - `/api/airspaces`: Retrieves a list of supported airspaces with their bounding boxes.
        ```
        {
            "airspaces": {
                "berlin": [
                    52.3418234221,
                    13.0882097323,
                    52.6697240587,
                    13.7606105539
                ],
                ...
            }
        }
        ```
    - `/api/{airspace}/total`: Retrieves the total carbon emission for a specific airspace.
        ```
        {
            "airspace_name": "berlin",
            "total": 0.0
        }
        ```
    - `/api/{airspace}/data?begin=""&end=""`: Retrieves carbon emission data of specific airspace within a time range.
        ```
        {
            "airspace_name": "berlin",
            "data": {
                "1688570063": 2274.5379754689091,
                "1688573663": 14038.3486858304127,
                ...
            }
        }
        ```
    - `/api/leaderboard`: Retrieves the carbon emission of celebrities of the past 30 days.
        ```
        {
            "celeb_emission":{
                "Bill Gates": 344989.05000000005,
                "Michael Jordan": 90107.66333333333,
                ...
            }
        }
        ```


## Run The Server

### Using Docker-Compose
1. Make sure to have Docker and Docker Compose installed on your system
2. Clone the repository to the machine with `git clone`
3. Change into the local repository in the server/src directory
```
cd flights-co2-tracker/server/src
```
4. Create a account_data.json file here with opensky account data for specific airspaces. The currently supported airspaces are Berlin, Paris, London, and Madrid, but it is possible to specify additional airspaces with their respective bounding boxes in the main.py file. The data for the accounts has to be provided in the following format:
```
{
    "berlin": {
        "username": USERNAME1,
        "password": PASSWORD1
    },
    "paris": {
        "username": USERNAME2,
        "password": PASSWORD2
    },
    ...
}
```
One account per airspace is not required, but currently the airstates are polled every minute from OpenSky. If you want to run the service over a longer period of time, you might get blocked if using fewer accounts.
5. Start Docker on the machine. It should be up and running before continuing.
6. Build the needed docker images with:
```
docker-compose build
```
The first build could take a couple of minutes to finish.

7. Initialize and start the containers with:
```
docker-compose up
```
The containers can be stopped, restarted, and deleted using::
```
docker-compose stop
docker-compose start
docker-compose down
```
8. You should see three different containers being started and you can now send requests to the api via `http://127.0.0.1:8000` and be provided with the data specified by the defined endpoints.

### Using Python Virtual Environment
1. You need to have python and most likely Redis installed on your system
2. Create and activate a python virtual environment to install required packages
3. Perform steps 3 and 4 of the docker-compose start process and create a file for OpenSky account data in a specific directory and format.
4. Install python packages with:
```
pip install -r requirements.txt
pip install -r api/requirements.txt
```
4. If you want to host the database yourself, start Redis on your machine. Typically, it runs on the Redis port 6379.
5. Start the main computation script by running:
```
python main.py
```
If you don't host the Redis database locally or Redis is running on a different port, you need to specify the host and/or port as follows:
```
python main.py --db_host "Redis_IP_ADDRESS" --db_port "Redis_PORT"
```
If you created the account_data file under a different name or in a different directory, you can use:
```
python main.py --accounts "/path/to/accounts_file"
```
6. Start the server-side API using:
```
python api/server_api.py --api_host "HOST_IP_ADDRESS" --api_port "HOST_PORT"
```
If the arguments are not specified, the API is started under `127.0.0.1:8000`. Again, if you have a different Redis setup, db_host and db_port have to be provided in the same way as above.
Be aware that to start the API, server_api.py has to be able to import database.py, which is in the parent directory. You can either copy the database.py file to the api directory, update your pythonpath to include the src directory or try to import database using a relative path.

7. You can now send requests to the API via `http://127.0.0.1:8000` and be provided with the data specified by the defined endpoints.
