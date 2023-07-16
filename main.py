import argparse

from OJ import OJBe
from OJ.app.settings import HOST, PORT
from OJ.middleware import users

parser = argparse.ArgumentParser()
parser.add_argument('--host', type=str, default=HOST)
parser.add_argument('--port', type=int, default=PORT)
parser.add_argument('--no-cors', action='store_false')

args = parser.parse_args()
# example application
if __name__ == '__main__':
    server = OJBe(
        args.host, args.port, args.no_cors
    )
    # add custom middleware
    # server.add_middleware(...)
    # You can also add other routes here
    # server.add_route(...)
    server.start()
