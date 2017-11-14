## GraphManager Service

Current directory contains:
* graphmanager-service implementation in `src/graph_manager` folder

VERSION: `0.2`

### Docker container

Using the Graph Manager Service Docker container:
* `docker pull attxproject/gm-api:dev` in the current folder;
* running the container `docker run -d -p 4302:4302 attxproject/gm-api:dev` runs the container in detached mode on the `4302` port (production version should have this port hidden);
* using the endpoints e.g. `http://localhost:4302/{versionNb}/{endpoint}` or the other listed below.

The version number is specified in `src/graph_manager/app.py` under `version` variable.

## Overview

The Graph Manager manages interaction with the Graph Store and retrieving statistics about it (e.g. list of named graphs, number of queries) and also it communicates with UnifiedViews plugins about the graph data information in the Graph Store.

Full information on how to run and work with the Graph Manager Service available at: https://attx-project.github.io/Service-Graph-Manager.html

## API Endpoints

The Graph Manager REST API has the following endpoints:
* `graph` - interface to the Fuseki Graph Store;
* `health` - checks if the application is running.

## Develop

### Requirements
1. Python 2.7
2. Gradle 3.0+ https://gradle.org/
3. Pypi Ivy repository either a local one (see https://github.com/linkedin/pygradle/blob/master/docs/pivy-importer.md for more information) or you can deploy your own version using https://github.com/blankdots/ivy-pypi-repo

### Building the Artifact with Gradle

Install [gradle](https://gradle.org/install). The tasks available are listed below:

* do clean build: `gradle clean build`
* see tasks: `gradle tasks --all` and depenencies `gradle depenencies`
* see test coverage `gradle pytest coverage` it will generate a html report in `htmlcov`

### Run without Gradle

To run the server, please execute the following (preferably in a virtual environment):
```
pip install -r pinned.txt
python src/graph_manager/graphservice.py server
python src/graph_manager/graphservice.py rpc
```

For testing purposes the application requires a running Fuseki, RabbitMQ. Also the health endpoint provides information on running services the service has detected: `http://localhost:4302/health`

The Swagger definition lives here:`swagger-gmAPI.yml`.
