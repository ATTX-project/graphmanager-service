import uuid
import os
from graph_manager.utils.logs import app_logger

data = {'directory': os.environ['DATADIR'] if 'DATADIR' in os.environ else "/attx-sb-shared"}


def file_extension(mime_type):
    """Naming convention for activity status."""
    return {
        'text/turtle': "ttl",
        'application/n-triples': "nt",
        'text/n3': "n3",
        'application/trig': "trig",
        'application/rdf+xml': "xml",
        'application/sparql-results+xml': 'xml',
        'application/sparql-results+json': 'json',
    }[str(mime_type)]


def results_path(content, extension):
    """Write results to specific file."""
    try:
        path = "{0}/graphmanager/{1}".format(data["directory"], uuid.uuid4().hex)
        if not os.path.exists(path):
            os.makedirs(path)
        full_path = "{0}/{1}.{2}".format(path, uuid.uuid1().hex, extension)
        f = open(full_path, "w+")
        f.write(content)
        app_logger.info('Content available in path: {0}'.format(full_path))
        return full_path
    except Exception as error:
        app_logger.error('Something is wrong: {0}'.format(error))
        raise
    finally:
        f.close()
