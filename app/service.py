from redis_connection import get_redis_connection
import requests
from fastapi import HTTPException
from pydantic import BaseSettings
from typing import Optional


class CountryInfo(BaseSettings):
    domains: str
    alpha_two_code: str
    country: str
    web_pages: str
    name: str
    state_province: Optional[str] = ''


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
        # scan 0 MATCH Turkey* count 300
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
        for country in countries:
            country_info = CountryInfo(
                domains="@".join(country["domains"]),
                alpha_two_code=country["alpha_two_code"],
                country=country["country"],
                web_pages="@".join(country["web_pages"]),
                name=country["name"],
                state_province=self.__is_value_none_return_emptystring(country["state-province"])
            )
            key = f"{country_info.country}:{country_info.name.replace(' ', '_')}"
            self.redis_conn.hmset(key, country_info.dict())

    def __is_value_none_return_emptystring(self, value):
        return value or ""