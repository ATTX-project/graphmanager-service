import json
import unittest
import httpretty
from rdflib import Graph
from graph_manager.applib.construct_message import replace_message, add_message, retrieve_message, query_message
from mock import patch
from graph_manager.applib.graph_store import GraphStore
from amqpstorm import AMQPConnectionError


class ConstructGraphTestCase(unittest.TestCase):
    """Test for Provenance function."""

    def setUp(self):
        """Set up test fixtures."""
        self.graph = Graph()
        self.request_address = "http://localhost:3030/ds"
        pass

    @patch.object(GraphStore, 'graph_retrieve')
    def test_retrieve_called(self, mock):
        """Test if retrieve graph data was called."""
        with open('tests/resources/graph_strategy.ttl') as datafile:
            graph_data = datafile.read()
        with open('tests/resources/message_data_retrieve.json') as datafile:
            message = json.load(datafile)
        mock.return_value = graph_data
        retrieve_message(message)
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
        url1 = "http://data.hulib.helsinki.fi/attx/strategy"
        request_url1 = "{0}/query?default-graph-uri=%s&query={1}&output=xml&results=xml&format=xml".format(self.request_address, url1, list_query)
        httpretty.register_uri(httpretty.GET, request_url1, graph_data, status=200, content_type="application/sparql-results+xml")
        url2 = "http://data.hulib.helsinki.fi/attx/attx-onto"
        request_url2 = "{0}/query?default-graph-uri=%s&query={1}&output=xml&results=xml&format=xml".format(self.request_address, url2, list_query)
        httpretty.register_uri(httpretty.GET, request_url2, graph_data, status=200, content_type="application/sparql-results+xml")
        mock.return_value = graph_data
        query_message(message)
        self.assertTrue(mock.called)

    @patch('graph_manager.applib.construct_message.Publisher.push')
    # @patch.object(GraphStore, 'graph_add')
    @patch.object(GraphStore, 'graph_replace')
    def test_replace_called(self, mock1, publish_mock):
        """Test if replace graph data was called."""
        with open('tests/resources/message_data.json') as datafile:
            message = json.load(datafile)
        replace_message(message)
        self.assertTrue(mock1.called)
        # self.assertTrue(mock2.called)

    @patch('graph_manager.applib.construct_message.Publisher.push')
    @patch.object(GraphStore, 'graph_add')
    @patch.object(GraphStore, 'graph_replace')
    def test_replace_called_file_fail(self, mock1, mock2, publish_mock):
        """Test if replace graph data was called."""
        with open('tests/resources/message_data_file.json') as datafile:
            message = json.load(datafile)
        with self.assertRaises(IOError):
            replace_message(message)

    @patch.object(GraphStore, 'graph_replace')
    def test_replace_error(self, mock):
        """Test if replace raises an error was called."""
        with open('tests/resources/message_data.json') as datafile:
            message = json.load(datafile)
        with self.assertRaises(AMQPConnectionError):
            replace_message(message)

    @patch('graph_manager.applib.construct_message.Publisher.push')
    @patch.object(GraphStore, 'graph_add')
    def test_store_called(self, mock, publish_mock):
        """Test if store graph data was called."""
        with open('tests/resources/message_data_add.json') as datafile:
            message = json.load(datafile)
        add_message(message)
        self.assertTrue(mock.called)

    @patch.object(GraphStore, 'graph_add')
    def test_store_error(self, mock):
        """Test if store raises an error was called."""
        with open('tests/resources/message_data_add.json') as datafile:
            message = json.load(datafile)
        with self.assertRaises(AMQPConnectionError):
            add_message(message)


if __name__ == "__main__":
    unittest.main()
