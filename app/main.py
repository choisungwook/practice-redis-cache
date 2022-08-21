from fastapi import FastAPI
from service import CountryService
app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/search")
def get_university(country: str):
    """country 검색"""
    country_service = CountryService()
    university = country_service.get_university(country_name=country)

    return {
        "university": university
    }
