import json
import requests
from graph_manager.utils.logs import app_logger
from datetime import datetime
from graph_manager.applib.graph_store import GraphStore
from graph_manager.utils.broker import broker
from graph_manager.applib.messaging_publish import Publisher
from graph_manager.utils.file import results_path, file_extension
from urlparse import urlparse
from requests_file import FileAdapter
from rdflib.graph import Graph

artifact_id = "GraphManager"  # Define the GraphManager agent
agent_role = "storage"  # Define Agent type
output_key = "graphManagerOutput"


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
            storage._graph_add(target_graph, data, content_type)
        endTime = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        PUBLISHER.push(prov_message(message_data, "success", startTime, endTime))
        app_logger.info('Stored graph data in: {0} graph'.format(target_graph))
        return json.dumps(response_message(message_data["provenance"], "success"), indent=4, separators=(',', ': '))
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
    content_type = message_data["payload"]["graphManagerInput"]["outputContentType"]
    request = storage._graph_sparql(source_graphs, query, content_type)
    if output_type == "URI":
        output = results_path(request, file_extension(content_type))
    elif output_type == "Data":
        output = request
    return json.dumps(response_message(message_data["provenance"], status="success", output=output), sort_keys=True, indent=4, separators=(',', ': '))


def construct_message(message_data):
    """Query named graph in Graph Store."""
    storage = GraphStore()
    source_graphs = message_data["payload"]["graphManagerInput"]["sourceGraphs"]
    query = message_data["payload"]["graphManagerInput"]["input"]
    output_type = message_data["payload"]["graphManagerInput"]["outputType"]
    content_type = message_data["payload"]["graphManagerInput"]["outputContentType"]
    request = storage._graph_construct(source_graphs, query, content_type)
    if output_type == "URI":
        output = results_path(request, file_extension(content_type))
    elif output_type == "Data":
        output = request
    return json.dumps(response_message(message_data["provenance"], status="success", output=output), sort_keys=True, indent=4, separators=(',', ': '))


def retrieve_message(message_data):
    """Retrieve named graph from Graph Store."""
    storage = GraphStore()
    result_graph = Graph()
    source_graphs = message_data["payload"]["graphManagerInput"]["sourceGraphs"]
    output_type = message_data["payload"]["graphManagerInput"]["outputType"]
    content_type = message_data["payload"]["graphManagerInput"]["outputContentType"]
    for graph in source_graphs:
        result_graph.parse(data=storage._graph_retrieve(graph), format="turtle")
    if output_type == "URI":
        output = results_path(result_graph.serialize(format=content_type), file_extension(content_type))
    elif output_type == "Data":
        output = result_graph.serialize(format=content_type)
    return json.dumps(response_message(message_data["provenance"], status="success", output=output), indent=4, separators=(',', ': '))


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
        print(first_graph_data)
        storage._graph_replace(target_graph, first_graph_data, first_graph_content_type)
        for graph in source_graphs[1:]:
            content_type = graph["contentType"]
            data = retrieve_data(graph["inputType"], graph["input"])
            print(data)
            storage._graph_add(target_graph, data, content_type)
        endTime = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        PUBLISHER.push(prov_message(message_data, "success", startTime, endTime))
        app_logger.info('Replaced graph data in: {0} graph'.format(target_graph))
        return json.dumps(response_message(message_data["provenance"], status="success"), indent=4, separators=(',', ': '))
    except Exception as error:
        endTime = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        PUBLISHER.push(prov_message(message_data, "error", startTime, endTime))
        app_logger.error('Something is wrong: {0}'.format(error))
        raise


def handle_file_adapter(request, input_data):
    """Handle file adapter response."""
    if request.status_code == 404:
        raise IOError("Something went wrong with retrieving the file: {0}. It does not exist!".format(input_data))
    elif request.status_code == 403:
        raise IOError("Something went wrong with retrieving the file: {0}. Accessing it is not permitted!".format(input_data))
    elif request.status_code == 400:
        raise IOError("Something went wrong with retrieving the file: {0}. General IOError!".format(input_data))
    elif request.status_code == 200:
        return request.text


def retrieve_data(input_type, input_data):
    """Retrieve data from a specific URI."""
    s = requests.Session()
    allowed = ('http', 'https', 'ftp')
    local = ('file')
    if input_type == "Data":
        return input_data
    elif input_type == "URI":
        try:
            if urlparse(input_data).scheme in allowed:
                request = s.get(input_data, timeout=1)
                return request.text
            elif urlparse(input_data).scheme in local:
                s.mount('file://', FileAdapter())
                request = s.get(input_data)
                return handle_file_adapter(request, input_data)
        except Exception as error:
            app_logger.error('Something is wrong: {0}'.format(error))
            raise


def prov_message(message_data, status, start_time, end_time):
    """Construct GM related provenance message."""
    message = dict()
    message["provenance"] = dict()
    message["provenance"]["agent"] = dict()
    message["provenance"]["agent"]["ID"] = artifact_id
    message["provenance"]["agent"]["role"] = agent_role

    activity_id = message_data["provenance"]["context"]["activityID"]
    workflow_id = message_data["provenance"]["context"]["workflowID"]

    prov_message = message["provenance"]

    prov_message["context"] = dict()
    prov_message["context"]["activityID"] = str(activity_id)
    prov_message["context"]["workflowID"] = str(workflow_id)
    if message_data["provenance"]["context"].get('stepID'):
        prov_message["context"]["stepID"] = message_data["provenance"]["context"]["stepID"]

    prov_message["activity"] = dict()
    prov_message["activity"]["type"] = "ServiceExecution"
    prov_message["activity"]["title"] = "Graph Manager Operations."
    prov_message["activity"]["status"] = status
    prov_message["activity"]["startTime"] = start_time
    prov_message["activity"]["endTime"] = end_time
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
    return json.dumps(message)


def response_message(provenance_data, status, status_messsage=None, output=None):
    """Construct Graph Manager response."""
    message = dict()
    message["provenance"] = dict()
    message["provenance"]["agent"] = dict()
    message["provenance"]["agent"]["ID"] = artifact_id
    message["provenance"]["agent"]["role"] = agent_role

    activity_id = provenance_data["context"]["activityID"]
    workflow_id = provenance_data["context"]["workflowID"]

    prov_message = message["provenance"]

    prov_message["context"] = dict()
    prov_message["context"]["activityID"] = str(activity_id)
    prov_message["context"]["workflowID"] = str(workflow_id)
    if provenance_data["context"].get('stepID'):
        prov_message["context"]["stepID"] = provenance_data["context"]["stepID"]
    message["payload"] = dict()
    message["payload"]["status"] = status
    if status_messsage:
        message["payload"]["statusMessage"] = status_messsage
    if output:
        message["payload"][output_key] = output
    return message
