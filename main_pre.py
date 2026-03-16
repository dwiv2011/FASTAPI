from fastapi   import FastAPI,Path,HTTPException,Query
import json
app=FastAPI()


with open('patients.json','r') as f:
    df=json.load(f)
    
@app.get("/view")
def data_view():
    return df
    
@app.get("/")
def hello():
    return {'message':'Hello World'}
# to kickoff use commands, uvicorn main:app --reload

@app.get('/about')
def hello():
    return {'message':'This is Deepak and keen to learn the Data Science object'}

# /docs : it lists all the end points 

@app.get('/patient/{patient_id}')
def view_patient(patient_id: str = Path(..., description='ID of the patient in the DB', example='P001')):
    # load all the patients

    if patient_id in df:
        return df[patient_id]
    else:
        raise HTTPException(status_code=404, detail='Patient Not found')
    #raise 'Patient not found' : This will give error but the HTTP code will still show as 200


@app.get('/sort')
def sort_patients(sort_by: str = Query(..., description='Sort on the basis of height, weight or bmi'), order: str = Query('asc', description='sort in asc or desc order')):

    valid_fields = ['height', 'weight', 'bmi']

    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail=f'Invalid field select from {valid_fields}')
    
    if order not in ['asc', 'desc']:
        raise HTTPException(status_code=400, detail='Invalid order select between asc and desc')
    

    sort_order = True if order=='desc' else False

    sorted_data = sorted(df.values(), key=lambda x: x.get(sort_by, 0), reverse=sort_order)

    return sorted_data