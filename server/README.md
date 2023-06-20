# Flight Tracker Python Backend

This directory contains the backend on the Flight-CO2-Tracker and is designedto be hosted in the cloud. The backend currently runs under `http://35.210.64.77:8000` in a GCP Virtual Machine.

## Structure

The Backend contains of four python files:
- `server_api.py`: Inside this file, there is a class to handle incoming request from the frontend.
    The current endpoints are:
        `/api/total/{airspace}`: Get the total carbon emission of the specified airspace since server is running.
- `opensky_network.py`: Has a single function request current air state in a specific bounding box from the OpenSky API (Username and Password for OpenSky account have to be provided).
- `calculate_co2.py`: Contains a class to compute the co2 emission from an airspace. Inside there is a function `get_co2_emission`, which takes a the current air state in the specified area and returns the estimated carbon emission since the the last call (the class saves parts of the former state for the computation too).
- `main.py`: Handles the connection between the different parts. It schedules the requests to be made to OpenSky, startes the co2 computation from there, and aggregates and stores the computed carbon data (currently a Redis Database).
