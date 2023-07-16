## Pre work

### Ensure support for Python

```shell
sudo apt update
sudo apt install python3.8
```

check Python3 is available

```shell
python3.8 --version
```

### Initialize environment

```shell
python3 -m venv your_venv_name
source your_venv_name/bin/activate
```

### Run this application as a package

```shell
pip3 install -e .
``` 

```python
from OJ import OJBe

server = OJBe(host, port, no_cors)  # server-host,server-port,no-cors required
server.start()
```

### Visit the OJ-Be api page

Use your browser to open http://127.0.0.1:8000/docs

### Customize exclusive features

In main.py we provide three parameters, namely host/port/no-cors. You can use command-line parameters to modify host and
port during startup.

```shell
python3 main.py --host 0.0.0.0 --port 16808 --no_cors
```

If use no-cors, the frontend and the backend must be in the same domain.

In the OJ package, we only provide basic functions. We also provide an open interface to add custom functions.

For example, you can customize a new route function named CFunction using APIRouter. Then you can add route using
server.add_route(CFunction).

```python
...
server = OJBe()
server.add_route(CFunction)
...
```

You can also use BaseHTTPMiddleware to customize middleware.

```python
class YourMiddleware(BaseHTTPMiddleware):
    def __init__(self):
        ...

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        ...


...
server = OJBe()
server.add_middleware(YourMiddleware)
...
```