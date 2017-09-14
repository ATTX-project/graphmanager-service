## GraphManager Service

Current directory contains:
* graphmanager-service implementation in `src/graph_manager` folder

VERSION: 0.2

### GM API Docker container

Using the GM API Docker container:
* `docker pull attxproject/graphmanager-service` in the current folder;
* running the container `docker run -d -p 4302:4302 attxprojectgraphmanager-service` runs the container in detached mode on the `4302` port (production version should have this port hidden);
* using the endpoints `http://localhost:4302/$versionNb/index` or `http://localhost:4302/$versionNb/clusterids` or the other listed below.

The version number is specified in `src/graph_manager/gmapi.py` under `version` variable.

#  GraphManager Service server

## Overview
The GM exposes information from the Graph Store to the Distribution component (Elasticsearch). It runs the mapping processing, clustering of IDs for the data and also it communicates with the Workflow API about the Provenance information in the Graph Store.

The GM API requires python 2.7 installed.

## API Endpoints

The Graph Manager REST API has the following endpoints:
* `index` - on given indexing parameters index the data from the Graph Store and insert it into Distribution Component endpoint;
* `cluster` - cluster the IDs from the working data in the Graph Store;
* `link` - retrieve the links in the Graph Store;
* `linkstrategy` - retrieve either all or specific linking strategies from the Graph Store;
* `prov` - retrieve provenance from the Workflow API and update the Graph Store with the provenance information.
* `health` - checks if the application is running.

## Develop

### Build with Gradle

Install [gradle](https://gradle.org/install). The tasks available are listed below:

* do clean build: `gradle clean build`
* see tasks: `gradle tasks --all` and depenencies `gradle depenencies`
* see test coverage `gradle graph_manager:pytest coverage` it will generate a html report in `build/coverage/htmlcov`

### Run without Gradle

To run the server, please execute the following (preferably in a virtual environment):
```
pip install -r requirements
python src/gm_api/gmapi.py
```
in the `graph_manager` folder

For testing purposes the application requires a running UnifiedViews, WF-API, Elasticsearch both 1.3.4 and Elasticsearch 5.x and Fuseki, one can make a request to the address below to view pipelines and associated steps:

```
http://localhost:4302/$versionNb/index
```

The Swagger definition lives here:`gmAPI-swagger.yml`.


## Running Tests

In order work/generate tests:
* use the command: `py.test tests` in the `graph_manager` folder
* coverage: `py.test --cov-report html --cov=graph_manager tests/` in the `graph_manager` folder
* generate cover report `py.test tests --html=build/test-report/index.html --self-contained-html` - this will generate a `build/test-report/index.html` folder that contains html based information about the tests coverage.
