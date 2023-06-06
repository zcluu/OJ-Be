1. Ensure support for Python
```shell
sudo apt update
sudo apt install python3.8
```
check Python3 is available
```shell
python3.8 --version
```
2. Initialize environment
```shell
python3 -m venv your_venv_name
source your_venv_name/bin/activate
pip3 install -r requirements.txt
```
check fastapi is available
```shell
python3 -c "import fastapi;print('Support FastAPI:',fastapi.__version__)"
```
2. Start OJ-Be service
```shell
source your_venv_name/bin/activate
python3 -m uvicorn main:app --reload --port 8000
```
3. Visit the OJ-Be api page

Use your browser to open http://127.0.0.1:8000/docs