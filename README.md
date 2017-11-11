## GraphManager Service

Current directory contains:
* graphmanager-service implementation in `src/graph_manager` folder

VERSION: `0.2`

### Docker container

Using the Graph Manager Service Docker container:
* `docker pull attxproject/gm-api:dev` in the current folder;
* running the container `docker run -d -p 4302:4302 attxproject/gm-api:dev` runs the container in detached mode on the `4302` port (production version should have this port hidden);
* using the endpoints e.g. `http://localhost:4302/$versionNb/health` or the other listed below.

The version number is specified in `src/graph_manager/app.py` under `version` variable.

## Overview

The Graph Manager manages interaction with the Graph Store and retrieving statistics about it (e.g. list of named graphs, number of queries) and also it communicates with UnifiedViews plugins about the graph data information in the Graph Store.

The Graph Manager Service requires python 2.7 installed.

## API Endpoints

The Graph Manager REST API has the following endpoints:
* `graph` - interface to the Fuseki Graph Store;
* `health` - checks if the application is running.

## Develop

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

For testing purposes the application requires a running Fuseki, one can make a request to the address below to view pipelines and associated steps:

```
http://localhost:4302/$versionNb/index
```

The Swagger definition lives here:`swagger-gmAPI.yml`.

## Running Tests

In order work/generate tests:
* using Gradle: `gradle build` will run the tests automatically, and `gradle build` coverage will generate coverage report
* use the command: `py.test tests` in the `graph_manager` folder
