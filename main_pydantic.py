from fastapi   import FastAPI,Path,HTTPException,Query
from pydantic import BaseModel,Field,computed_field
from typing import Annotated,Literal,Optional
from fastapi.responses import JSONResponse
import json
app=FastAPI()


class Patients(BaseModel):
    #Annotated will show in API call 
    id:Annotated[str,Field(...,description='ID of the Patient',examples=['P001'])]
    name:Annotated[str,Field(...,description ='name of the patient')]
    city:Annotated[str,Field(...,description='City of the Patient')]
    age:Annotated[int,Field(gt=0,lt=120)]
    gender:Annotated[Literal['male','female','Others'],Field(...,description='Gender of the patient')]
    height:Annotated[float,Field(...,description='Height of the Patients',gt=0)]
    weight:Annotated[float,Field(...,gt=0,description='weight of the Patients')]

    @computed_field
    @property
    def bmi(self)->float:
        bmi=round(self.weight/(self.height**2),2)
        return bmi
    
    @computed_field
    @property
    def verdict(self)->str:
        if self.bmi<18.5:
            return 'Under Weight'
        elif self.bmi <30:
            return 'Normal'
        else:
            return 'Obese'

# all the field marked as optional because update can happen on any field and user may not provide all variable
class PatientUpdate(BaseModel):
    name: Annotated[Optional[str], Field(default=None)]
    city: Annotated[Optional[str], Field(default=None)]
    age: Annotated[Optional[int], Field(default=None, gt=0)]
    gender: Annotated[Optional[Literal['male', 'female']], Field(default=None)]
    height: Annotated[Optional[float], Field(default=None, gt=0)]
    weight: Annotated[Optional[float], Field(default=None, gt=0)]



with open('patients.json','r') as f:
    df=json.load(f)

def save_data(data):
    with open('patients.json','w') as f:
        json.dump(data,f)

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

@app.post('/create')
def create_patient(patient:Patients):
    if patient.id in df:
        raise HTTPException(status_code=400,detail='Patient already exist')
    else:
        df[patient.id]=patient.model_dump(exclude=['id'])

    #save into json file 
    save_data(df)
    return JSONResponse(status_code=200,content={'message':'Patient created Successfully'})

@app.put('/edit/{patient_id}')
def update_patient(patient_id:str,patient:PatientUpdate):
    if patient_id not in df:
        raise HTTPException(status_code='404',content={'message':'There is no Patient as {patient_id}'})
    
    else:
        fetch_data=df[patient_id]
        #reason for exclude_unset
        dct=patient.model_dump(exclude_unset=True)

        for key,value in dct.items():
            fetch_data[key]=value
            print(key,value)
        #we have to calculate the BMI and verdict, 
        # to do this simplest way we can convert the updated dictionary to pydantic object
        fetch_data['id']=patient_id
        patient_pydantic_obj=Patients(**fetch_data)
        fetch_data=patient_pydantic_obj.model_dump(exclude='id')
        df[patient_id]=fetch_data
        # save data 
        save_data(df)

        return JSONResponse(status_code=200,content={'message':'update the patients details'})
    
@app.delete('/delete/{patient_id}')
def delete_patient(patient_id: str):

 
    if patient_id not in df:
        raise HTTPException(status_code=404, detail='Patient not found')
    
    del df[patient_id]

    save_data(df)

    return JSONResponse(status_code=200, content={'message':'patient deleted'})

        


