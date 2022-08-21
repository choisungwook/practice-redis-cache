from redis_connection import get_redis_connection
import requests
from fastapi import HTTPException

class CountryService:
    def __init__(self):
        self.redis_conn = get_redis_connection()

    def get_university(self, country_name: str):
        """university 조회"""
        redis_value = self.__get_university_from_redis(country_name=country_name)
        if redis_value:
            return redis_value

        countries = self.__get_university_from_restapi(country_name=country_name)
        self.__add_university_to_redis(countries=countries)

        return countries

    def __get_university_from_redis(self, country_name: str):
        """redis에 university가 있는지 확인"""
        return None

    def __get_university_from_restapi(self, country_name: str) -> list:
        """restapi로 university 조회"""
        url = "http://universities.hipolabs.com/search"
        params = {
            "country": country_name
        }

        response = requests.get(url, params=params)
        if not response.ok:
            raise HTTPException(status_code=500, detail="rest api is failed")

        return response.json()

    def __add_university_to_redis(self, countries: list):
        """redis에 university 추가"""
        pass