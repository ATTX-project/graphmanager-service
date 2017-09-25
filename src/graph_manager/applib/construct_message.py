import json
import requests
from graph_manager.utils.logs import app_logger
from datetime import datetime
from graph_manager.utils.graph_store import GraphStore
from graph_manager.utils.broker import broker
from graph_manager.utils.messaging_publish import Publisher
from graph_manager.utils.file import results_path
from urlparse import urlparse
from requests_file import FileAdapter

artifact_id = 'GraphManger'  # Define the GraphManger agent
agent_role = 'storage'  # Define Agent type


def store_graph(message_data):
    """Store data in the Graph Store."""
    startTime = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    storage = GraphStore()
    named_graph = message_data["payload"]["graphManagerInput"]["namedGraph"]
    content_type = message_data["payload"]["graphManagerInput"]["contentType"]
    data = retrieve_data(message_data["payload"]["graphManagerInput"]["inputType"],
                         message_data["payload"]["graphManagerInput"]["input"])
    PUBLISHER = Publisher(broker['host'], broker['user'], broker['pass'], broker['provqueue'])
    try:
        request = storage.graph_update(named_graph, data, content_type)
        endTime = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        PUBLISHER.push(construct_prov(message_data, "success", startTime, endTime))
        app_logger.info('Stored graph data in: {0} graph'.format(named_graph))
        return construct_response(message_data["provenance"], request)
    except Exception as error:
        endTime = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        PUBLISHER.push(construct_prov(message_data, "error", startTime, endTime))
        app_logger.error('Something is wrong: {0}'.format(error))
        raise error


def query_graph(message_data):
    """Query named graph in Graph Store."""
    storage = GraphStore()
    named_graph = message_data["payload"]["graphManagerInput"]["namedGraph"]
    query = message_data["payload"]["graphManagerInput"]["input"]
    if named_graph == "default":
        request = storage.graph_sparql("", query)
    else:
        request = storage.graph_sparql(named_graph, query)
    output = results_path(request, 'xml')
    return construct_response(message_data["provenance"], output)


def retrieve_graph(message_data):
    """Retrieve named graph from Graph Store."""
    storage = GraphStore()
    named_graph = message_data["payload"]["graphManagerInput"]["namedGraph"]
    request = storage.retrieve_graph(named_graph)
    output = results_path(request, 'ttl')
    return construct_response(message_data["provenance"], output)


def replace_graph(message_data):
    """Store data in the Graph Store."""
    startTime = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    storage = GraphStore()
    named_graph = message_data["payload"]["graphManagerInput"]["namedGraph"]
    content_type = message_data["payload"]["graphManagerInput"]["contentType"]
    data = retrieve_data(message_data["payload"]["graphManagerInput"]["inputType"],
                         message_data["payload"]["graphManagerInput"]["input"])
    PUBLISHER = Publisher(broker['host'], broker['user'], broker['pass'], broker['provqueue'])
    try:
        request = storage.graph_replace(named_graph, data, content_type)
        endTime = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        PUBLISHER.push(json.dumps(construct_prov(message_data, "success", startTime, endTime)))
        app_logger.info('Stored graph data in: {0} graph'.format(named_graph))
        return construct_response(message_data["provenance"], request)
    except Exception as error:
        endTime = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        PUBLISHER.push(json.dumps(construct_prov(message_data, "error", startTime, endTime)))
        app_logger.error('Something is wrong: {0}'.format(error))
        raise error


def retrieve_data(inputType, input_data):
    """Retrieve data from a specific URI."""
    s = requests.Session()
    allowed = ('http', 'https', 'ftp')
    local = ('file')
    if inputType == "Data":
        return input_data
    elif inputType == "URI":
        try:
            if urlparse(input_data).scheme in allowed:
                request = s.get(input_data)
            elif urlparse(input_data).scheme in local:
                s.mount('file://', FileAdapter())
                request = s.get(input_data)
            return request.text
        except Exception as error:
            app_logger.error('Something is wrong: {0}'.format(error))
            raise error


def construct_prov(message_data, status, startTime, endTime):
    """Construct GM related provenance message."""
    message = dict()
    message["provenance"] = dict()
    message["provenance"]["agent"] = dict()
    message["provenance"]["agent"]["ID"] = artifact_id
    message["provenance"]["agent"]["role"] = agent_role

    activityID = message_data["provenance"]["context"]["activityID"]
    workflowID = message_data["provenance"]["context"]["workflowID"]

    prov_message = message["provenance"]

    prov_message["context"] = dict()
    prov_message["context"]["activityID"] = str(activityID)
    prov_message["context"]["workflowID"] = str(workflowID)
    if message_data["provenance"]["context"].get('stepID'):
        prov_message["context"]["stepID"] = message_data["provenance"]["context"]["stepID"]

    prov_message["activity"] = dict()
    prov_message["activity"]["type"] = "ServiceExecution"
    prov_message["activity"]["title"] = "Graph Manger Operations."
    prov_message["activity"]["status"] = status
    prov_message["activity"]["startTime"] = startTime
    prov_message["activity"]["endTime"] = endTime
    message["provenance"]["input"] = []
    message["provenance"]["output"] = []
    input_data = {
        "key": "inputGraphs",
        "role": "tempDataset"
    }
    output_data = {
        "key": "outputGraphs",
        "role": "Dataset"
    }
    if message_data["payload"]["graphManagerInput"]["inputType"] == "Data":
        message["payload"] = {
            "inputGraphs": "attx:tempDataset",
            "outputGraphs": message_data["payload"]["graphManagerInput"]["namedGraph"]
        }
    elif message_data["payload"]["graphManagerInput"]["inputType"] == "URI":
        message["payload"] = {
            "inputGraphs": message_data["payload"]["graphManagerInput"]["input"],
            "outputGraphs": message_data["payload"]["graphManagerInput"]["namedGraph"]
        }
    message["provenance"]["input"].append(input_data)
    message["provenance"]["output"].append(output_data)
    app_logger.info('Construct provenance metadata for Graph Manager.')
    return message


def construct_response(provenance_data, output):
    """Construct Graph Manager response."""
    message = dict()
    message["provenance"] = dict()
    message["provenance"]["agent"] = dict()
    message["provenance"]["agent"]["ID"] = artifact_id
    message["provenance"]["agent"]["role"] = agent_role

    activityID = provenance_data["context"]["activityID"]
    workflowID = provenance_data["context"]["workflowID"]

    prov_message = message["provenance"]

    prov_message["context"] = dict()
    prov_message["context"]["activityID"] = str(activityID)
    prov_message["context"]["workflowID"] = str(workflowID)
    if provenance_data["context"].get('stepID'):
        prov_message["context"]["stepID"] = provenance_data["context"]["stepID"]
    message["payload"] = dict()
    message["payload"]["graphManagerOutput"] = output
    return message
