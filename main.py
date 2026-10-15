from fastapi import FastAPI
from pydentic import BaseModel
from typing import List


app=FastAPI()

class Doc(BaseModel):
	id: int
	name: str
	
class symptom(BaseModel):
	s
docs: List[Doc] = []
symp: List[symptom] = []

@app.get("/")
def read_root():
	return {"message": "Welcome"}
	
@app.get("/docs")
def det_docs():
	return docs
	
@app.post("/docs")
def add_symp(symptoms):
	
