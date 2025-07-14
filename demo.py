from fastapi import FastAPI

app = FastAPI()

@app.get("/papers/{paper_id}/list-assignment")
def get_paper_assignments(paper_id: str):
    return {"msg": f"paper_id={paper_id} list-assignment OK"}
