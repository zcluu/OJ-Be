from OJ import OJBe

if __name__ == '__main__':
    server = OJBe(
        'config.yaml'
    )
    # add custom middleware
    # server.add_middleware(...)
    # You can also add other routes here
    # server.add_route(...)
    server.start()
