import unittest
from urllib import quote
from urllib2 import URLError
import responses
# import requests
from requests.exceptions import ConnectionError
import json
import httpretty
from falcon import testing
from graph_manager.app import init_api
from graph_manager.applib.graph_store import GraphStore


class GraphStoreTest(testing.TestCase):
    """Testing Graph Store and initialize the app for that.."""

    def setUp(self):
        """Setting the app up."""
        self.app = init_api()

    def tearDown(self):
        """Tearing down the app up."""
        pass


class GraphTestCase(GraphStoreTest):
    """Test for Graph Store operations."""

    def test_create(self):
        """Test GET health message."""
        self.app
        pass

    def setUp(self):
        """Set up test fixtures."""
        self.server_address = "http://localhost:3030/$/"
        self.request_address = "http://localhost:3030/ds"
        self.api = "http://localhost:4032/"
        self.version = "0.2"

    @responses.activate
    def test_ping(self):
        """Test_ping on graph endpoint."""
        responses.add(responses.GET, "http://localhost:3030/{0}/ping".format("$"), "2017-09-18T11:41:19.915+00:00", status=200)
        fuseki = GraphStore()
        result = fuseki._graph_health()
        self.assertTrue(result)

    @responses.activate
    def test_graph_list(self):
        """Test graph list on graph endpoint."""
        list_query = quote("select ?g (count(*) as ?count) {graph ?g {?s ?p ?o}} group by ?g")
        with open('tests/resources/graph_list_request.json') as datafile1:
            graph_data = json.load(datafile1)
        with open('tests/resources/graph_list_response.json') as datafile2:
            graph_list = json.load(datafile2)
        responses.add(responses.GET, "{0}/sparql?query={1}".format(self.request_address, list_query), json=graph_data, status=200)
        fuseki = GraphStore()
        result = fuseki._graph_list()
        assert(result == graph_list)

    @responses.activate
    def test_graph_list_bad(self):
        """Test ConnectionError graph list on graph endpoint."""
        fuseki = GraphStore()
        with self.assertRaises(ConnectionError):
            fuseki._graph_list()

    @responses.activate
    def test_graph_stats(self):
        """Test graph list on graph endpoint."""
        list_query = quote("select ?g (count(*) as ?count) {graph ?g {?s ?p ?o}} group by ?g")
        with open('tests/resources/graph_stats_request.json') as datafile1:
            graph_data = json.load(datafile1)
        with open('tests/resources/graph_stats_response.json') as datafile2:
            graph_stats = json.load(datafile2)
        with open('tests/resources/graph_list_request.json') as datafile3:
            graph_list = json.load(datafile3)
        responses.add(responses.GET, "{0}stats/{1}".format(self.server_address, "ds"), json=graph_data, status=200)
        responses.add(responses.GET, "{0}/sparql?query={1}".format(self.request_address, list_query), json=graph_list, status=200)
        fuseki = GraphStore()
        result = fuseki._graph_statistics()
        assert(result == graph_stats)

    @responses.activate
    def test_graph_stats_bad(self):
        """Test ConnectionError graph stats on graph endpoint."""
        fuseki = GraphStore()
        with self.assertRaises(ConnectionError):
            fuseki._graph_statistics()

    @responses.activate
    def test_graph_retrieve_None(self):
        """Test graph retrieve non-existent graph."""
        responses.add(responses.GET, "{0}/data?graph={1}".format(self.request_address, "http://test.com"), status=404)
        fuseki = GraphStore()
        result = fuseki._graph_retrieve("default")
        self.assertIsNone(result)

    @responses.activate
    def test_graph_retrieve_ttl(self):
        """Test graph retrieve a specific graph."""
        with open('tests/resources/graph_strategy.ttl') as datafile:
            graph_data = datafile.read()
        url = "http://data.hulib.helsinki.fi/attx/strategy"
        responses.add(responses.GET, "{0}/data?graph={1}".format(self.request_address, url), body=graph_data, status=200)
        fuseki = GraphStore()
        result = fuseki._graph_retrieve("http://data.hulib.helsinki.fi/attx/strategy")
        assert(result == graph_data)

    @responses.activate
    def test_graph_retrieve_bad(self):
        """Test ConnectionError graph retrieve on graph endpoint."""
        fuseki = GraphStore()
        with self.assertRaises(ConnectionError):
            fuseki._graph_retrieve("default")

    @responses.activate
    def test_graph_add(self):
        """Test update graph."""
        url = "http://data.hulib.helsinki.fi/attx/strategy"
        graph_data = "<http://example/egbook3> <http://purl.org/dc/elements/1.1/title>  \"This is an example title\""
        with open('tests/resources/graph_add_response.json') as datafile:
            response_data = json.load(datafile)

        def request_callback(request):
            """Request callback for drop graph."""
            headers = {'content-type': "application/json",
                       'cache-control': "no-cache"}
            return (200, headers, json.dumps(response_data))

        responses.add_callback(
            responses.POST, "{0}/data?graph={1}".format(self.request_address, url),
            callback=request_callback,
            content_type='text/turtle',
        )
        fuseki = GraphStore()
        result = fuseki._graph_add(url, graph_data, "text/turtle")
        assert(result == response_data)

    @responses.activate
    def test_graph_add_bad(self):
        """Test ConnectionError graph update on graph endpoint."""
        fuseki = GraphStore()
        with self.assertRaises(ConnectionError):
            fuseki._graph_add("default", "", "text/turtle")

    @responses.activate
    def test_graph_replace(self):
        """Test replace graph."""
        url = "http://data.hulib.helsinki.fi/attx/strategy"
        graph_data = "<http://example/egbook3> <http://purl.org/dc/elements/1.1/title>  \"This is an example title\""
        with open('tests/resources/graph_add_response.json') as datafile:
            response_data = json.load(datafile)

        responses.add(
            responses.PUT, "{0}?graph={1}".format(self.request_address, url),
            json=response_data, status=200
        )
        fuseki = GraphStore()
        result = fuseki._graph_replace(url, graph_data, "text/turtle")
        assert(result == response_data)

    @responses.activate
    def test_graph_replace_bad(self):
        """Test ConnectionError graph replace on graph endpoint."""
        fuseki = GraphStore()
        with self.assertRaises(ConnectionError):
            fuseki._graph_replace("default", "", "text/turtle")

    @responses.activate
    def test_graph_drop(self):
        """Test drop graph."""
        url = "http://data.hulib.helsinki.fi/attx/strategy"
        with open('tests/resources/graph_drop.txt') as datafile:
            graph_data = datafile.read()

        def request_callback(request):
            """Request callback for drop graph."""
            headers = {'content-type': 'text/html',
                       'cache-control': "no-cache"}
            return (200, headers, graph_data)

        responses.add_callback(
            responses.POST, "{0}/update".format(self.request_address),
            callback=request_callback,
            content_type="application/x-www-form-urlencoded",
        )
        fuseki = GraphStore()
        result = fuseki._drop_graph(url)
        assert(result == graph_data)

    @responses.activate
    def test_graph_drop_bad(self):
        """Test ConnectionError graph drop on graph endpoint."""
        fuseki = GraphStore()
        with self.assertRaises(ConnectionError):
            fuseki._drop_graph("default")

    @httpretty.activate
    def test_graph_sparql(self):
        """Test update graph."""
        with open('tests/resources/graph_sparql.xml') as datafile:
            graph_data = datafile.read()
        list_query = "select ?g (count(*) as ?count) {graph ?g {?s ?p ?o}} group by ?g"
        url = "http://data.hulib.helsinki.fi/attx/strategy"
        request_url = "{0}/query?default-graph-uri=%s&query={1}&output=xml&results=xml&format=xml".format(self.request_address, url, list_query)
        httpretty.register_uri(httpretty.GET, request_url, graph_data, status=200, content_type="application/sparql-results+xml")
        fuseki = GraphStore()
        result = fuseki._graph_sparql(url, list_query, 'application/sparql-results+xml')
        assert(result == graph_data)
        httpretty.disable()
        httpretty.reset()

    @responses.activate
    def test_graph_sparql_bad(self):
        """Test ConnectionError SPARQL on graph endpoint."""
        list_query = quote("select ?g (count(*) as ?count) {graph ?g {?s ?p ?o}} group by ?g")
        fuseki = GraphStore()
        with self.assertRaises(URLError):
            fuseki._graph_sparql("default", list_query, 'application/sparql-results+xml')


if __name__ == "__main__":
    unittest.main()
