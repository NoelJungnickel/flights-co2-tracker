# Flight Tracker Python Backend

This directory contains the backend on the Flight-CO2-Tracker and is designedto be hosted in the cloud. The backend currently runs under `http://35.210.64.77:8000` in a GCP Virtual Machine.

## Structure

The Backend contains of four python files:
- `server_api.py`: Inside this file, there is a class to handle incoming request from the frontend.
    The current endpoints are:\
        `/api/total/{airspace}`: Get the total carbon emission of the specified airspace since server is running.
- `opensky_network.py`: Has a single function request current air state in a specific bounding box from the OpenSky API (Username and Password for OpenSky account have to be provided).
- `calculate_co2.py`: Contains a class to compute the co2 emission from an airspace. Inside there is a function `get_co2_emission`, which takes a the current air state in the specified area and returns the estimated carbon emission since the the last call (the class saves parts of the former state for the computation too).
- `main.py`: Handles the connection between the different parts. It schedules the requests to be made to OpenSky, startes the co2 computation from there, and aggregates and stores the computed carbon data (currently a Redis Database).

## Run the server

1. Clone the repository to the macine with `git clone`
2. Change into the local repository in the server directory
3. A `config.ini` file containing account information for OpenSky needs to be created (one account for each watched airspace is needed so that the service could run 24/7). It should be in the following form, where AIRSPACE_NAME has to be replaced with the name of the watched airspace (`berlin`, `paris`, `london` and `madrid` have predefined bounding boxes):
```
[AIRSPACE_NAME]
username = AIRSPACE_1_USERNAME
password = AIRSPACE_1_PASSWORD

[AIRSPACE_NAME]
username = AIRSPACE_2_USERNAME
password = AIRSPACE_2_PASSWORD
``` 
4. Start redis on the machine. It should be up and running on the port 6379.
5. Start the main function of the program:
```
python main.py --config PATH/TO/config.ini
```
6. Start the server api to get access to the data via http requests:
```
python server_api.py
```
