import json
import requests
from graph_manager.utils.logs import app_logger
from datetime import datetime
from graph_manager.utils.graph_store import GraphStore
from graph_manager.utils.broker import broker
from graph_manager.utils.messaging_publish import Publisher
from graph_manager.utils.file import results_path, file_extension
from urlparse import urlparse
from requests_file import FileAdapter
from rdflib.graph import Graph

artifact_id = 'GraphManager'  # Define the GraphManager agent
agent_role = 'storage'  # Define Agent type


def add_message(message_data):
    """Store data in the Graph Store."""
    startTime = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    storage = GraphStore()
    target_graph = message_data["payload"]["graphManagerInput"]["targetGraph"]
    source_graphs = message_data["payload"]["graphManagerInput"]["sourceData"]
    PUBLISHER = Publisher(broker['host'], broker['user'], broker['pass'], broker['provqueue'])
    try:
        for graph in source_graphs:
            content_type = graph["contentType"]
            data = retrieve_data(graph["inputType"], graph["input"])
            storage.graph_add(target_graph, data, content_type)
        endTime = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        PUBLISHER.push(prov_message(message_data, "success", startTime, endTime))
        app_logger.info('Stored graph data in: {0} graph'.format(target_graph))
        return response_message(message_data["provenance"], "success")
    except Exception as error:
        endTime = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        PUBLISHER.push(prov_message(message_data, "error", startTime, endTime))
        app_logger.error('Something is wrong: {0}'.format(error))
        raise


def query_message(message_data):
    """Query named graph in Graph Store."""
    storage = GraphStore()
    source_graphs = message_data["payload"]["graphManagerInput"]["sourceGraphs"]
    query = message_data["payload"]["graphManagerInput"]["input"]
    output_type = message_data["payload"]["graphManagerInput"]["outputType"]
    content_type = message_data["payload"]["graphManagerInput"]["contentType"]
    request = storage.graph_sparql(source_graphs, query, content_type)
    if output_type == "URI":
        output = results_path(request, file_extension(content_type))
    elif output_type == "Data":
        output = request
    output_obj = {"contentType": content_type,
                  "outputType": output_type,
                  "output": output}
    return response_message(message_data["provenance"], json.dumps(output_obj))


def retrieve_message(message_data):
    """Retrieve named graph from Graph Store."""
    storage = GraphStore()
    result_graph = Graph()
    source_graphs = message_data["payload"]["graphManagerInput"]["sourceGraphs"]
    output_type = message_data["payload"]["graphManagerInput"]["outputType"]
    content_type = message_data["payload"]["graphManagerInput"]["contentType"]
    for graph in source_graphs:
        result_graph.parse(data=storage.graph_retrieve(graph), format="turtle")
    if output_type == "URI":
        output = results_path(result_graph.serialize(format=content_type), file_extension(content_type))
    elif output_type == "Data":
        output = result_graph.serialize(format=content_type)
    output_obj = {"contentType": content_type,
                  "outputType": output_type,
                  "output": output}
    return response_message(message_data["provenance"], json.dumps(output_obj))


def replace_message(message_data):
    """Store data in the Graph Store."""
    startTime = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    storage = GraphStore()
    target_graph = message_data["payload"]["graphManagerInput"]["targetGraph"]
    source_graphs = message_data["payload"]["graphManagerInput"]["sourceData"]
    PUBLISHER = Publisher(broker['host'], broker['user'], broker['pass'], broker['provqueue'])
    try:
        first_graph = next(iter(source_graphs or []), None)
        first_graph_content_type = first_graph["contentType"]
        first_graph_data = retrieve_data(first_graph["inputType"], first_graph["input"])
        storage.graph_replace(target_graph, first_graph_data, first_graph_content_type)
        for graph in source_graphs[1:]:
            content_type = graph["contentType"]
            data = retrieve_data(graph["inputType"], graph["input"])
            storage.graph_add(target_graph, data, content_type)
        endTime = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        PUBLISHER.push(prov_message(message_data, "success", startTime, endTime))
        app_logger.info('Replaced graph data in: {0} graph'.format(target_graph))
        return response_message(message_data["provenance"], "success")
    except Exception as error:
        endTime = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        PUBLISHER.push(prov_message(message_data, "error", startTime, endTime))
        app_logger.error('Something is wrong: {0}'.format(error))
        raise


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
            raise


def prov_message(message_data, status, startTime, endTime):
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
    prov_message["activity"]["title"] = "Graph Manager Operations."
    prov_message["activity"]["status"] = status
    prov_message["activity"]["startTime"] = startTime
    prov_message["activity"]["endTime"] = endTime
    message["provenance"]["input"] = []
    message["provenance"]["output"] = []
    message["payload"] = {}
    output_data = {
        "key": "outputGraph",
        "role": "Dataset"
    }
    source_graphs = message_data["payload"]["graphManagerInput"]["sourceData"]

    for graph in source_graphs:
        input_data = {
            "key": "inputGraphs_{0}".format(source_graphs.index(graph)),
            "role": "tempDataset"
        }
        key = "inputGraphs_{0}".format(source_graphs.index(graph))
        if graph["inputType"] == "Data":
            message["payload"][key] = "attx:tempDataset"
        if graph["inputType"] == "URI":
            message["payload"][key] = graph["input"]
        message["provenance"]["input"].append(input_data)
    message["payload"]["outputGraph"] = message_data["payload"]["graphManagerInput"]["targetGraph"]
    message["provenance"]["output"].append(output_data)
    app_logger.info('Construct provenance metadata for Graph Manager.')
    return str(message)


def response_message(provenance_data, output):
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
