from redis_connection import get_redis_connection
import requests
from fastapi import HTTPException
from pydantic import BaseSettings
from typing import Optional


class UniversityMetaData(BaseSettings):
    """redis에 값을 넣기 위한 스키마"""
    domains: str
    alpha_two_code: str
    country: str
    web_pages: str
    name: str
    state_province: Optional[str] = ''

class UniversityMetaDataDecoded(BaseSettings):
    """redis스키마 디코딩"""
    domains: list
    alpha_two_code: str
    country: str
    web_pages: list
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
        university_names = [key for key in self.redis_conn.scan_iter(match=f"{country_name}*", count=100)]

        universities = []
        for name in university_names:
            response = self.redis_conn.hmget(name, "domains", "alpha_two_code", "country", "web_pages", "name", "state_province")
            university_metadata = UniversityMetaDataDecoded(
                domains=self.__redis_value_to_list_if_contains(response[0]),
                alpha_two_code=response[1],
                country=response[2],
                web_pages=self.__redis_value_to_list_if_contains(response[3]),
                name=response[4].replace("_", ""),
                state_province=response[5]
            )
            universities.append(university_metadata)

        return universities

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
            country_info = UniversityMetaData(
                domains=self.__list_to_string_for_redis_value(country["domains"]),
                alpha_two_code=country["alpha_two_code"],
                country=country["country"],
                web_pages= self.__list_to_string_for_redis_value(country["web_pages"]),
                name=country["name"],
                state_province=self.__is_value_none_return_emptystring(country["state-province"])
            )
            key = f"{country_info.country}:{country_info.name.replace(' ', '_')}"
            self.redis_conn.hmset(key, country_info.dict())

    def __list_to_string_for_redis_value(self, values: list):
        """list자료형을 redis에 저장하기 위해 문자열 변환"""
        return "@".join(values)

    def __redis_value_to_list_if_contains(self, value: str):
        """redis 응답에 @가 있으면 리스트로 변환"""
        if "@" in value:
            return value.split("@")

        return [value]

    def __is_value_none_return_emptystring(self, value):
        return value or ""
