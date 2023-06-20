from OJ import app
from OJ.app.settings import *
import uvicorn

if __name__ == '__main__':
    uvicorn.run(app, host=HOST, port=PORT, reload=DEBUG)
