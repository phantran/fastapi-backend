# MVP Match backend 1

## Requirements
- Make sure Docker and Docker Compose are installed https://docs.docker.com/compose/install/
- Python 3.9

## Run

Use the command below to spin up all docker containers of the application.
The stack includes:
- API container which is the main application code,
- Redis container for caching
- MySQL database for persistence
```commandline
docker-compose up
```

After running the command above is executed successfully, the API endpoints will be available at 
```commandline
http://localhost:8000/api/v1
```

For example: Accessing the link below to see the Swagger documentation for usage of all API endpoints
```commandline
http://localhost:8000/api/v1/docs
```

## Run tests

```commandline
pytest tests/integration_tests 
```