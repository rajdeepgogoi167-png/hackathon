from fastapi import FastAPI
from pydentic import BaseModel
from typing import List


app=FastAPI()

class Doc(BaseModel):
	id: int
	name: str
	
class patient(BaseModel):
	patient_id: int
	patient_name: str
	symptom: str
	
	
doctors: List[Doc] = []
symp: List[patient] = []

@app.get("/")
def read_root():
	return {"message": "Welcome"}
	
@app.get("/doctors")
def det_docs():
	return docs
	
@app.post("/doctors")
def add_symp(patient):
	
