import time
from functools import lru_cache
import requests
from bs4 import BeautifulSoup

from src.util.logger import Logger


class CompanyWise:
    """유통주식수 관련 정보를 처리하는 클래스"""

    URL_COMPANY_STATE = 'https://comp.wisereport.co.kr/company/c1010001.aspx?cn=&cmp_cd='

    @staticmethod
    def _get_url_company_state(stock_code):
        return f'{CompanyWise.URL_COMPANY_STATE}{stock_code}'

    @classmethod
    @lru_cache(maxsize=128)
    def get_floating_stock_count(cls, stock_code, sleep_sec_after_request=0):
        """유통주식 수를 가져오고 캐시"""
        try:
            floating_stock_count = cls._fetch_floating_stock_count(stock_code)
        except Exception as e:
            Logger.write_error(e)
            floating_stock_count = 0

        if sleep_sec_after_request:
            time.sleep(sleep_sec_after_request)

        return floating_stock_count

    @classmethod
    def _fetch_floating_stock_count(cls, stock_code):
        """실제 유통주식 수 조회 로직"""
        soup = cls._get_soup(stock_code)
        cls._validate_stock_code(stock_code, soup)
        return cls._extract_floating_stock_count(stock_code, soup)

    @staticmethod
    def _get_soup(stock_code):
        """웹 페이지 내용을 파싱하여 BeautifulSoup 객체 반환"""
        url = CompanyWise._get_url_company_state(stock_code)
        html = requests.get(url, timeout=3)
        return BeautifulSoup(html.content, 'html.parser', from_encoding='utf-8')

    @staticmethod
    def _validate_stock_code(requested_code, soup):
        """응답에서 종목 코드 확인"""
        response_code = CompanyWise._get_stock_code_from_response(soup)
        if requested_code != response_code:
            Logger.write(f'유동주식수 확인 실패(종목코드 불일치) - '
                         f'조회 요청 종목코드 : {requested_code}, '
                         f'검색된 종목코드 : {response_code}')
            raise ValueError("종목코드 불일치")

    @staticmethod
    def _extract_floating_stock_count(stock_code, soup):
        """HTML에서 유통주식 수 추출"""
        element = soup.find(id="cTB11")
        row = element.find_all('tbody')[0].find_all('tr')[6]
        cell = row.find_all('td')[0]
        issued_shares, float_ratio = cell.text.strip().split('/')

        issued_shares = int(issued_shares.replace('주', '').replace(',', ''))
        float_ratio = float(float_ratio.replace('%', ''))
        floating_stock_count = int(issued_shares * (float_ratio / 100))

        Logger.write(f'유동주식수 확인 - '
                     f'종목코드 : {stock_code}, '
                     f'발행주식수 : {issued_shares:,}, '
                     f'유동주식비율 : {float_ratio}%, '
                     f'유동주식수 : {floating_stock_count:,}')

        return floating_stock_count

    @staticmethod
    def _get_stock_code_from_response(soup):
        """응답에서 종목 코드 추출"""
        element = soup.find(id="comInfo")
        return element.find_all('td')[0].find_all('span')[1].text.strip()