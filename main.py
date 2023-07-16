from OJ import OJBe
from OJ.middleware import users

# example application
if __name__ == '__main__':
    server = OJBe()
    # add custom middleware
    server.add_middleware(users.CheckLogin)
    # You can also add other routes here
    # server.add_route(...)
    server.start()
