**# Spotter Backend Assessment**



A Django REST API that calculates an efficient fuel strategy for a road trip between two locations in the United States.



The API:



1\. Geocodes the start and destination.

2\. Calculates the driving route.

3\. Finds fuel stations along the route.

4\. Matches those stations against the provided fuel-price dataset.

5\. Determines where to refuel based on fuel price and vehicle range.

6\. Calculates total fuel purchased and total fuel cost.



**## Tech Stack**



\- Python 3.12

\- Django

\- Django REST Framework

\- PostgreSQL

\- Geoapify Geocoding API

\- Geoapify Routing API

\- Geoapify Places API

\- Shapely

\- Requests

\- Postman



**## Project Structure**



\`\`\`text

pithon/

├── config/

│   ├── settings.py

│   ├── urls.py

│   └── ...

│

├── fuel/

│   ├── migrations/

│   ├── models.py

│   └── ...

│

├── routes/

│   ├── services/

│   │   ├── fuel_matcher.py

│   │   ├── geocoder.py

│   │   ├── geoapify.py

│   │   ├── optimizer.py

│   │   ├── route_optimizer.py

│   │   └── route_position.py

│   │

│   ├── tests/

│   ├── serializers.py

│   ├── urls.py

│   └── views.py

│

├── data/

│   └── fuel-prices-for-be-assessment.csv

│

├── logs/

├── docker-compose.yml

├── .env.example

├── manage.py

├── requirements.txt

└── README.md

\`\`\`



**## Requirements**



\- Python 3.12+

\- PostgreSQL

\- Geoapify API key



**## Setup**



**### 1. Clone the repository**



\`\`\`bash

git clone \<your-github-repository-url>

cd pithon

\`\`\`



**### 2. Create a virtual environment**



\`\`\`bash

python3 -m venv .venv

\`\`\`



Activate it:



**#### macOS/Linux**



\`\`\`bash

source .venv/bin/activate

\`\`\`



**#### Windows**



\`\`\`bash

.venv\Scripts\activate

\`\`\`



**### 3. Install dependencies**



\`\`\`bash

pip install -r requirements.txt

\`\`\`



**### 4. Configure environment variables**



Create a \`.env\` file in the project root:



\`\`\`env

DJANGO_SECRET_KEY=your-secret-key

DEBUG=True



GEOAPIFY_API_KEY=your_geoapify_api_key



DB_NAME=spotter

DB_USER=spotter

DB_PASSWORD=spotter_password

DB_HOST=localhost

DB_PORT=5432

\`\`\`



The \`.env\` file should **\*\*not\*\*** be committed to Git.



A \`.env.example\` file can be used as a template:



\`\`\`env

DJANGO_SECRET_KEY=your-secret-key

DEBUG=True



GEOAPIFY_API_KEY=your_geoapify_api_key



DB_NAME=spotter

DB_USER=spotter

DB_PASSWORD=spotter_password

DB_HOST=localhost

DB_PORT=5432

\`\`\`



**### 5. Start PostgreSQL with Docker**



The project includes a Docker Compose configuration for running PostgreSQL locally.



Start the PostgreSQL container:



```bash

docker compose up -d

```



Verify that the container is running:



```bash

docker compose ps

```



PostgreSQL will be available at:



```text

Host: localhost

Port: 5432

Database: spotter

User: spotter

```



The database credentials are loaded from the `.env` file by Docker Compose.



The PostgreSQL data is stored in a Docker named volume, so stopping the container does not remove the database data.



To stop PostgreSQL:



```bash

docker compose down

```



**### 6. Run migrations**



```bash

python manage.py migrate

```



**### 7. Import fuel-price data**






The assessment dataset is located at:



\`\`\`text

data/fuel-prices-for-be-assessment.csv

\`\`\`



Import the supplied fuel-price data into the \`FuelStation\` table before using the API.



**## Running the Application**



Start the Django development server:



\`\`\`bash

python manage.py runserver

\`\`\`



The API will be available at:



\`\`\`text

http\://127.0.0.1:8000/

\`\`\`



**## API**



**### Optimize Route**



\`\`\`http

POST /api/v1/routes/optimize/

\`\`\`



**### Request**



Content-Type:



\`\`\`text

application/json

\`\`\`



Example:



\`\`\`json

{

&#x20;   "start": "Los Angeles, CA",

&#x20;   "destination": "Albuquerque, NM"

}

\`\`\`



**### Postman**



\`\`\`text

POST

http\://127.0.0.1:8000/api/v1/routes/optimize/

\`\`\`



Body:



\`\`\`json

{

&#x20;   "start": "Los Angeles, CA",

&#x20;   "destination": "Albuquerque, NM"

}

\`\`\`



**## Response**



The response contains:



\- Route distance

\- Route duration

\- Route geometry

\- Selected fuel stops

\- Fuel price

\- Fuel purchased at each stop

\- Cost at each stop

\- Total fuel purchased

\- Total fuel cost



Example structure:



\`\`\`json

{

&#x20;   "route": {

&#x20;       "distance_miles": 787.03,

&#x20;       "duration_seconds": 43210.0,

&#x20;       "geometry": {}

&#x20;   },

&#x20;   "fuel": {

&#x20;       "stops": [

&#x20;           {

&#x20;               "name": "LOVES TRAVEL STOP #553",

&#x20;               "distance_miles": 431.37,

&#x20;               "price_per_gallon": 3.596,

&#x20;               "gallons_purchased": 28.703,

&#x20;               "cost": 103.21

&#x20;           }

&#x20;       ],

&#x20;       "total_gallons": 28.703,

&#x20;       "total_cost": 103.21

&#x20;   }

}

\`\`\`



**## Fuel Optimization**



The vehicle assumptions from the assessment are:



\`\`\`text

Maximum range: 500 miles

Fuel economy: 10 MPG

Starting condition: Full tank

\`\`\`



The optimizer considers fuel stations in route order.



The general strategy is:



1\. Start with a full tank.

2\. Determine whether the destination can be reached with the available fuel.

3\. If not, look for a cheaper fuel station ahead within the vehicle's range.

4\. If a cheaper station exists, purchase enough fuel to reach it.

5\. Otherwise, purchase enough fuel to continue the journey.

6\. Repeat until the destination is reachable.

7\. Calculate the total gallons purchased and total cost.



Fuel prices are taken from the supplied assessment dataset.



**## Station Matching**



The supplied CSV contains duplicate records.



The imported dataset contains:



\- 8,151 CSV rows

\- 6,738 unique OPIS Truckstop IDs



The database uses \`opis_id\` as a unique identifier.



Fuel stations discovered through Geoapify are matched against the local database using station name, city, and state.



This allows the application to use the fuel prices supplied with the assessment instead of relying on prices returned by the external places service.



**## Route Positioning**



Geoapify returns the route geometry.



For each matched fuel station, the application calculates its position along the route.



This allows the optimizer to work with stations ordered by:



\`\`\`text

distance from start

\`\`\`



rather than simply using geographic distance from the origin.



**## External API Usage**



The application uses Geoapify for:



**### Geocoding**



Two location geocoding requests are performed concurrently.



Geocoded locations are cached for 30 days to avoid repeatedly geocoding the same locations.



**### Routing**



One routing request is made for each optimization request.



The routing response provides:



\- Route distance

\- Duration

\- Route geometry

\- Polyline6 representation



**### Fuel Station Discovery**



The Geoapify Places API is used to find fuel stations along the calculated route.



The category used is:



\`\`\`text

service.vehicle.fuel

\`\`\`



The application does not make a routing request for every fuel station.



**## Performance**



The application measures the main stages of the request:



\`\`\`text

Geocoding

Routing

Fuel station lookup

Station matching

Fuel optimization

Total request time

\`\`\`



Concurrent geocoding and caching reduce unnecessary latency for repeated locations.



The fuel matching and optimization operations are performed locally.



**## Logging**



Application logs use Python's standard \`logging\` module.



Normal \`INFO\` messages are written to the development server console.



\`ERROR\` messages are also persisted to:



\`\`\`text

logs/errors.log

\`\`\`



The log directory is excluded from Git.



Example:



\`\`\`text

INFO routes.services.route_optimizer - Routing: 1.62s

INFO routes.services.route_optimizer - Fuel station lookup: 2.31s

ERROR routes.services.geoapify - Geoapify places request failed: status=400

\`\`\`



API keys and sensitive credentials are not logged.



**## Error Handling**



The API handles failures from external services and returns appropriate HTTP responses.



Examples:



**### Invalid input**



\`\`\`text

400 Bad Request

\`\`\`



**### Geocoding failure**



\`\`\`text

400 Bad Request

\`\`\`



**### Fuel optimization failure**



\`\`\`text

400 Bad Request

\`\`\`



**### External Geoapify failure**



\`\`\`text

502 Bad Gateway

\`\`\`



The API does not expose raw external-service responses to clients.



**## Testing**



Run the automated test suite with:



\`\`\`bash

python manage.py test

\`\`\`



The tests cover:



\- Route-position calculations

\- Haversine distance

\- Fuel-station matching

\- Fuel optimization

\- Serializer validation

\- API behavior

\- Geocoding behavior



Example:



\`\`\`text

Found 13 test(s).



.............



\----------------------------------------------------------------------

Ran 13 tests in 0.029s



OK

\`\`\`



**## Known Limitation**



Geoapify's Places-along-route endpoint imposes limits on the route geometry supplied to the Places API.



Very long routes can exceed the provider's geometry limits, such as:



\`\`\`text

filter.geometry must not exceed 102400 UTF-8 bytes

\`\`\`



or:



\`\`\`text

filter.geometry must not contain more than 10000 positions

\`\`\`



The limitation is specific to the external Places API and does not affect the fuel optimization algorithm itself.



Routes within the practical geometry limits of the Places API can be processed normally.



**## Security**



The following files and directories should not be committed:



\`\`\`text

.env

logs/

.venv/

\_\_pycache\_\_/

\`\`\`



The API key and database credentials are supplied through environment variables.



**## Design Considerations**



The implementation intentionally avoids geocoding every fuel station in the supplied dataset.



Instead:



\`\`\`text

Start / Destination

&#x20;       ↓

&#x20;   Geocoding

&#x20;       ↓

&#x20;     Routing

&#x20;       ↓

Fuel stations along route

&#x20;       ↓

Match against local database

&#x20;       ↓

Calculate route position

&#x20;       ↓

Fuel optimization

&#x20;       ↓

API response

\`\`\`



This keeps external API usage low while allowing the supplied fuel-price dataset to remain the source of fuel prices.



**## API Endpoint Summary**



\`\`\`text

POST /api/v1/routes/optimize/

\`\`\`



Request:



\`\`\`json

{

&#x20;   "start": "Los Angeles, CA",

&#x20;   "destination": "Albuquerque, NM"

}

\`\`\`



Response:



\`\`\`json

{

&#x20;   "route": {

&#x20;       "distance_miles": 787.03,

&#x20;       "duration_seconds": 43210.0,

&#x20;       "geometry": {}

&#x20;   },

&#x20;   "fuel": {

&#x20;       "stops": [],

&#x20;       "total_gallons": 0.0,

&#x20;       "total_cost": 0.0

&#x20;   }

}

\`\`\`



**## License**



This project was created as part of a technical assessment for Spotter.