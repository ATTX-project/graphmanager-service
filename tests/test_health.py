import falcon
import unittest
import httpretty
import json
from falcon import testing
from graph_manager.app import init_api
from graph_manager.applib.graph_store import GraphStore
from graph_manager.api.healthcheck import healthcheck_response


class appHealthTest(testing.TestCase):
    """Testing GM health API."""

    def setUp(self):
        """Setting the app up."""
        self.app = init_api()

    def tearDown(self):
        """Tearing down the app up."""
        pass


class TestGM(appHealthTest):
    """Testing if there is a health endoint available."""

    def test_create(self):
        """Test GET health message."""
        self.app
        pass

    @httpretty.activate
    def test_health_ok(self):
        """Test GET health is ok."""
        httpretty.register_uri(httpretty.GET, "http://localhost:4302/health", status=200)
        result = self.simulate_get('/health')
        assert(result.status == falcon.HTTP_200)
        httpretty.disable()
        httpretty.reset()

    @httpretty.activate
    def test_health_response(self):
        """Response to healthcheck endpoint."""
        httpretty.register_uri(httpretty.GET, "http://localhost:3030/$/ping", body="2017-09-18T11:41:19.915+00:00", status=200)
        fuseki = GraphStore()
        httpretty.register_uri(httpretty.GET, "http://user:password@localhost:15672/api/aliveness-test/%2F", body='{"status": "ok"}', status=200)
        httpretty.register_uri(httpretty.GET, "http://localhost:4302/health", status=200)
        response = healthcheck_response("Running", fuseki)
        result = self.simulate_get('/health')
        json_response = {"graphManagerService": "Running", "messageBroker": "Running", "graphStore": "Running"}
        assert(json_response == json.loads(response))
        assert(result.content == response)
        httpretty.disable()
        httpretty.reset()


if __name__ == "__main__":
    unittest.main()
