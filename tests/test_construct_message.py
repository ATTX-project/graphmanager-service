import json
import unittest
import httpretty
from rdflib import Graph
from graph_manager.applib.construct_message import retrieve_graph, query_graph, replace_graph, store_graph
from mock import patch
from graph_manager.utils.graph_store import GraphStore
from amqpstorm import AMQPConnectionError


class ConstructGraphTestCase(unittest.TestCase):
    """Test for Provenance function."""

    def setUp(self):
        """Set up test fixtures."""
        self.graph = Graph()
        self.request_address = "http://localhost:3030/ds"
        pass

    @patch('graph_manager.applib.construct_message.results_path')
    @patch.object(GraphStore, 'retrieve_graph')
    def test_retrieve_called(self, mock, file_mock):
        """Test if retrieve graph data was called."""
        with open('tests/resources/message_data.json') as datafile:
            message = json.load(datafile)
        retrieve_graph(message)
        self.assertTrue(mock.called)

    @patch('graph_manager.applib.construct_message.results_path')
    @patch.object(GraphStore, 'graph_sparql')
    @httpretty.activate
    def test_query_called(self, mock, file_mock):
        """Test if query graph data was called."""
        with open('tests/resources/graph_sparql.xml') as datafile:
            graph_data = datafile.read()
        with open('tests/resources/message_data_query.json') as datafile:
            message = json.load(datafile)
        list_query = "select ?g (count(*) as ?count) {graph ?g {?s ?p ?o}} group by ?g"
        url = "http://data.hulib.helsinki.fi/attx/strategy"
        request_url = "{0}/query?default-graph-uri=%s&query={1}&output=xml&results=xml&format=xml".format(self.request_address, url, list_query)
        httpretty.register_uri(httpretty.GET, request_url, graph_data, status=200, content_type="application/sparql-results+xml")
        query_graph(message)
        self.assertTrue(mock.called)

    @patch('graph_manager.applib.construct_message.Publisher.push')
    @patch.object(GraphStore, 'graph_replace')
    def test_replace_called(self, mock, publish_mock):
        """Test if replace graph data was called."""
        with open('tests/resources/message_data.json') as datafile:
            message = json.load(datafile)
        replace_graph(message)
        self.assertTrue(mock.called)

    @patch.object(GraphStore, 'graph_replace')
    def test_replace_error(self, mock):
        """Test if replace raises an error was called."""
        with open('tests/resources/message_data.json') as datafile:
            message = json.load(datafile)
        with self.assertRaises(AMQPConnectionError):
            replace_graph(message)

    @patch('graph_manager.applib.construct_message.Publisher.push')
    @patch.object(GraphStore, 'graph_add')
    def test_store_called(self, mock, publish_mock):
        """Test if store graph data was called."""
        with open('tests/resources/message_data.json') as datafile:
            message = json.load(datafile)
        store_graph(message)
        self.assertTrue(mock.called)

    @patch.object(GraphStore, 'graph_add')
    def test_store_error(self, mock):
        """Test if store raises an error was called."""
        with open('tests/resources/message_data.json') as datafile:
            message = json.load(datafile)
        with self.assertRaises(AMQPConnectionError):
            store_graph(message)

    # @patch('prov.applib.construct_prov.store_provenance')
    # def test_store_prov_bad(self, mock):
    #     """Test KeyError was raised."""
    #     with open('tests/resources/prov_request_bad.json') as datafile:
    #         graph_data = json.load(datafile)
    #     with self.assertRaises(KeyError):
    #         construct_provenance(graph_data["provenance"], graph_data["payload"])
    #
    # @patch('prov.applib.construct_prov.store_provenance')
    # def test_prov_data_stored(self, mock):
    #     """Test the resulting provenance graph."""
    #     with open('tests/resources/prov_request.json') as datafile:
    #         graph_data = json.load(datafile)
    #     with open('tests/resources/prov_output.ttl') as datafile1:
    #         graph_output = datafile1.read()
    #     construct_provenance(graph_data["provenance"], graph_data["payload"])
    #     mock.assert_called_with(graph_output)
    #
    # @patch('prov.applib.construct_prov.store_provenance')
    # def test_prov_describe_data_stored(self, mock):
    #     """Test the resulting provenance describe dataset."""
    #     with open('tests/resources/prov_request_describe.json') as datafile:
    #         graph_data = json.load(datafile)
    #     with open('tests/resources/prov_output_describe.ttl') as datafile1:
    #         graph_output = datafile1.read()
    #     construct_provenance(graph_data["provenance"], graph_data["payload"])
    #     mock.assert_called_with(graph_output)
    #
    # @patch('prov.applib.construct_prov.store_provenance')
    # def test_prov_communication_data_stored(self, mock):
    #     """Test the resulting provenance describe dataset."""
    #     with open('tests/resources/prov_request_communication.json') as datafile:
    #         graph_data = json.load(datafile)
    #     with open('tests/resources/prov_output_communication.ttl') as datafile1:
    #         graph_output = datafile1.read()
    #     construct_provenance(graph_data["provenance"], graph_data["payload"])
    #     mock.assert_called_with(graph_output)
    #
    # @patch('prov.applib.construct_prov.store_provenance')
    # def test_prov_workflow_data_stored(self, mock):
    #     """Test the resulting provenance describe dataset."""
    #     with open('tests/resources/prov_request_workflow.json') as datafile:
    #         graph_data = json.load(datafile)
    #     with open('tests/resources/prov_output_workflow.ttl') as datafile1:
    #         graph_output = datafile1.read()
    #     construct_provenance(graph_data["provenance"], graph_data["payload"])
    #     mock.assert_called_with(graph_output)


if __name__ == "__main__":
    unittest.main()
