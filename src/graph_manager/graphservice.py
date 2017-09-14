import click
import multiprocessing
import gunicorn.app.base
from graph_manager.app import init_api
from graph_manager.utils.messaging import ScalableRpcServer
from graph_manager.utils.broker import broker
from gunicorn.six import iteritems


@click.group()
def cli():
    """Run cli tool."""
    pass


@cli.command('server')
@click.option('--host', default='127.0.0.1', help='gmAPI host.')
@click.option('--port', default=4302, help='gmAPI server port.')
@click.option('--workers', default=2, help='gmAPI server workers.')
@click.option('--log', default='logs/server.log', help='log file for app.')
def server(host, port, log, workers):
    """Run the server with options."""
    options = {
        'bind': '{0}:{1}'.format(host, port),
        'workers': workers,
        'daemon': 'True',
        'errorlog': log
    }
    GMApplication(init_api(), options).run()


@cli.command('rpc')
def rpc():
    """RPC server."""
    RPC_SERVER = ScalableRpcServer(broker['host'], broker['user'], broker['pass'])
    RPC_SERVER.start_server()


class GMApplication(gunicorn.app.base.BaseApplication):
    """Create Standalone Application GM-API."""

    def __init__(self, app, options=None):
        """The init."""
        self.options = options or {}
        self.application = app
        super(GMApplication, self).__init__()

    def load_config(self):
        """Load configuration."""
        config = dict([(key, value) for key, value in iteritems(self.options)
                       if key in self.cfg.settings and value is not None])
        for key, value in iteritems(config):
            self.cfg.set(key.lower(), value)

    def load(self):
        """Load configuration."""
        return self.application


# Unless really needed to scale use this function. Otherwise 2 workers suffice.
def number_of_workers():
    """Establish the numberb or workers based on cpu_count."""
    return (multiprocessing.cpu_count() * 2) + 1


def main():
    """Main function."""
    cli()


if __name__ == '__main__':
    main()
