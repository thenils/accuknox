

## Introduction
This project is designed to run on Ubuntu or any other Linux distribution that supports Docker. Docker provides a convenient and consistent environment for deploying and running applications.

## Requirements
Make sure you have Docker installed on your machine. You can download and install Docker from the official website: [Docker](https://www.docker.com/).

## Build Docker Image
To build the Docker image for this project, follow these steps:

```bash
docker-copose build .
```

This command will use the Dockerfile in the project directory to build an image named `accuknox`.

## Run Docker Container
Once the Docker image is built, you can run a Docker container using the following command:

```bash
docker-compose up
```

This command maps port 8000 on your host machine to port 80 inside the Docker container. Adjust the ports as needed based on your application's configuration.

Using this command to create super user 
```bash
docker-compose run web python manage.py createsuperuser
```

After running this command, your application should be accessible at `http://localhost:8000/admin` in your web browser.



## Additional Notes
- Make sure no other service is already using the specified host port (in this case, port 8000). If the port is already in use, you may need to choose a different one.
- Check the application documentation for any additional configuration or environment variables that may need to be set when running the Docker container.

