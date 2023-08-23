from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

class KankanRequest(BaseModel):
    tdfk: str
    query: str

class KankanAPI(FastAPI):
    def __init__(self):
        super().__init__()

        self.post("/api/search")(self.search)

    def search(self, req: KankanRequest):
        res = {
            'result': req.tdfk + '|||' + req.query
        }
        return res
    
def main():
    app = KankanAPI()
    uvicorn.run(
        app,
        port=21345,
        root_path='/app/kankan'
    )

if __name__ == '__main__':
    main()