import falcon
from graph_manager.api.healthcheck import HealthCheck
from graph_manager.utils.logs import main_logger
from graph_manager.api.graph_endpoint import GraphStatistics, GraphList
from graph_manager.api.graph_endpoint import GraphResource, GraphSPARQL
from graph_manager.api.graph_endpoint import GraphUpdate

api_version = "0.2"  # TO DO: Figure out a better way to do versioning


def init_api():
    """Create the API endpoint."""
    gm_app = falcon.API()

    gm_app.add_route('/health', HealthCheck())

    gm_app.add_route('/%s/graph/query' % (api_version), GraphSPARQL())
    gm_app.add_route('/%s/graph/update' % (api_version), GraphUpdate())
    gm_app.add_route('/%s/graph/list' % (api_version), GraphList())
    gm_app.add_route('/%s/graph/statistics' % (api_version), GraphStatistics())
    gm_app.add_route('/%s/graph' % (api_version), GraphResource())

    main_logger.info('GM API is running.')
    return gm_app


# if __name__ == '__main__':
#     init_api()
