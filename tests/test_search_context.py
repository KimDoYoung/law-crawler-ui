"""
search_context.py 모듈에 대한 단위 테스트
"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch, MagicMock

from app.backend.page_contexts.search_context import (
    get_sites_list,
    search_data,
)


class TestGetSitesList:
    """get_sites_list 함수 테스트"""

    @patch("app.backend.page_contexts.search_context.get_site_and_code_dict")
    def test_get_sites_list_success(self, mock_get_site_dict):
        """정상적으로 사이트 목록 반환"""
        # Arrange
        mock_get_site_dict.return_value = {
            "site3": "사이트3",
            "site1": "사이트1",
            "site2": "사이트2",
        }

        # Act
        result = get_sites_list()

        # Assert
        assert len(result) == 3
        # 이름순으로 정렬되어야 함
        assert result[0] == {"code": "site1", "name": "사이트1"}
        assert result[1] == {"code": "site2", "name": "사이트2"}
        assert result[2] == {"code": "site3", "name": "사이트3"}

    @patch("app.backend.page_contexts.search_context.get_site_and_code_dict")
    def test_get_sites_list_empty(self, mock_get_site_dict):
        """사이트가 없는 경우"""
        # Arrange
        mock_get_site_dict.return_value = {}

        # Act
        result = get_sites_list()

        # Assert
        assert result == []

    @patch("app.backend.page_contexts.search_context.get_site_and_code_dict")
    def test_get_sites_list_exception(self, mock_get_site_dict):
        """예외 발생 시 빈 리스트 반환"""
        # Arrange
        mock_get_site_dict.side_effect = Exception("Database error")

        # Act
        result = get_sites_list()

        # Assert
        assert result == []

    @patch("app.backend.page_contexts.search_context.get_site_and_code_dict")
    def test_get_sites_list_single_site(self, mock_get_site_dict):
        """단일 사이트"""
        # Arrange
        mock_get_site_dict.return_value = {"site1": "사이트1"}

        # Act
        result = get_sites_list()

        # Assert
        assert len(result) == 1
        assert result[0] == {"code": "site1", "name": "사이트1"}


class TestSearchData:
    """search_data 함수 테스트"""

    @patch("app.backend.page_contexts.search_context.search_law_summary")
    def test_search_data_with_keyword_and_sites(self, mock_search, sample_dataframe):
        """키워드와 사이트 선택으로 검색"""
        # Arrange
        mock_search.return_value = sample_dataframe

        # Act
        result = search_data(
            site_names=["site1", "site2"],
            keyword="검색어",
            page=1,
            pagesize=30
        )

        # Assert
        assert result["total"] == 3
        assert result["page"] == 1
        assert result["pagesize"] == 30
        assert result["total_pages"] == 1
        assert len(result["items"]) == 3
        assert result["items"][0]["site_name"] == "사이트1"
        assert result["items"][0]["title"] == "제목1"

        # search_law_summary가 올바른 파라미터로 호출되었는지 확인
        mock_search.assert_called_once_with(
            site_names=["site1", "site2"],
            keyword="검색어"
        )

    @patch("app.backend.page_contexts.search_context.search_law_summary")
    def test_search_data_keyword_only(self, mock_search, sample_dataframe):
        """키워드만으로 검색 (전체 사이트)"""
        # Arrange
        mock_search.return_value = sample_dataframe

        # Act
        result = search_data(
            site_names=None,
            keyword="검색어",
            page=1,
            pagesize=30
        )

        # Assert
        assert result["total"] == 3
        assert len(result["items"]) == 3
        mock_search.assert_called_once_with(site_names=[], keyword="검색어")

    @patch("app.backend.page_contexts.search_context.search_law_summary")
    def test_search_data_sites_only(self, mock_search, sample_dataframe):
        """사이트 선택만으로 검색 (키워드 없음)"""
        # Arrange
        mock_search.return_value = sample_dataframe

        # Act
        result = search_data(
            site_names=["site1"],
            keyword="",
            page=1,
            pagesize=30
        )

        # Assert
        assert result["total"] == 3
        mock_search.assert_called_once_with(site_names=["site1"], keyword="")

    def test_search_data_no_criteria(self):
        """키워드도 사이트도 없으면 빈 결과"""
        # Act
        result = search_data(
            site_names=None,
            keyword="",
            page=1,
            pagesize=30
        )

        # Assert
        assert result["total"] == 0
        assert result["items"] == []
        assert result["page"] == 1
        assert result["total_pages"] == 0

    def test_search_data_empty_site_list_and_no_keyword(self):
        """빈 사이트 리스트와 빈 키워드"""
        # Act
        result = search_data(
            site_names=[],
            keyword="   ",  # 공백만
            page=1,
            pagesize=30
        )

        # Assert
        assert result["total"] == 0
        assert result["items"] == []

    @patch("app.backend.page_contexts.search_context.search_law_summary")
    def test_search_data_pagination_page1(self, mock_search):
        """페이징 테스트 - 첫 페이지"""
        # Arrange
        # 100개 데이터 생성
        large_df = pd.DataFrame({
            "site_name": [f"site{i}" for i in range(100)],
            "page_id": [f"page{i}" for i in range(100)],
            "사이트": [f"사이트{i}" for i in range(100)],
            "페이지": [f"페이지{i}" for i in range(100)],
            "제목": [f"제목{i}" for i in range(100)],
            "등록일": ["2025-01-01"] * 100,
            "수집일시": ["2025-01-01 10:00:00"] * 100,
            "site_url": [f"http://site{i}.com" for i in range(100)],
            "detail_url": [f"http://site{i}.com/detail" for i in range(100)],
            "org_url": [f"http://site{i}.com/org" for i in range(100)],
            "summary": [f"요약{i}" for i in range(100)],
            "real_seq": list(range(100)),
        })
        mock_search.return_value = large_df

        # Act
        result = search_data(
            site_names=["site1"],
            keyword="test",
            page=1,
            pagesize=30
        )

        # Assert
        assert result["total"] == 100
        assert result["total_pages"] == 4  # ceil(100/30) = 4
        assert result["page"] == 1
        assert len(result["items"]) == 30
        assert result["items"][0]["site_name"] == "사이트0"
        assert result["items"][29]["site_name"] == "사이트29"

    @patch("app.backend.page_contexts.search_context.search_law_summary")
    def test_search_data_pagination_page2(self, mock_search):
        """페이징 테스트 - 두 번째 페이지"""
        # Arrange
        large_df = pd.DataFrame({
            "site_name": [f"site{i}" for i in range(100)],
            "page_id": [f"page{i}" for i in range(100)],
            "사이트": [f"사이트{i}" for i in range(100)],
            "페이지": [f"페이지{i}" for i in range(100)],
            "제목": [f"제목{i}" for i in range(100)],
            "등록일": ["2025-01-01"] * 100,
            "수집일시": ["2025-01-01 10:00:00"] * 100,
            "site_url": [f"http://site{i}.com" for i in range(100)],
            "detail_url": [f"http://site{i}.com/detail" for i in range(100)],
            "org_url": [f"http://site{i}.com/org" for i in range(100)],
            "summary": [f"요약{i}" for i in range(100)],
            "real_seq": list(range(100)),
        })
        mock_search.return_value = large_df

        # Act
        result = search_data(
            site_names=["site1"],
            keyword="test",
            page=2,
            pagesize=30
        )

        # Assert
        assert result["page"] == 2
        assert len(result["items"]) == 30
        assert result["items"][0]["site_name"] == "사이트30"
        assert result["items"][29]["site_name"] == "사이트59"

    @patch("app.backend.page_contexts.search_context.search_law_summary")
    def test_search_data_pagination_last_page(self, mock_search):
        """페이징 테스트 - 마지막 페이지 (부분)"""
        # Arrange
        large_df = pd.DataFrame({
            "site_name": [f"site{i}" for i in range(100)],
            "page_id": [f"page{i}" for i in range(100)],
            "사이트": [f"사이트{i}" for i in range(100)],
            "페이지": [f"페이지{i}" for i in range(100)],
            "제목": [f"제목{i}" for i in range(100)],
            "등록일": ["2025-01-01"] * 100,
            "수집일시": ["2025-01-01 10:00:00"] * 100,
            "site_url": [f"http://site{i}.com" for i in range(100)],
            "detail_url": [f"http://site{i}.com/detail" for i in range(100)],
            "org_url": [f"http://site{i}.com/org" for i in range(100)],
            "summary": [f"요약{i}" for i in range(100)],
            "real_seq": list(range(100)),
        })
        mock_search.return_value = large_df

        # Act
        result = search_data(
            site_names=["site1"],
            keyword="test",
            page=4,
            pagesize=30
        )

        # Assert
        assert result["page"] == 4
        assert len(result["items"]) == 10  # 마지막 페이지는 10개만
        assert result["items"][0]["site_name"] == "사이트90"
        assert result["items"][9]["site_name"] == "사이트99"

    @patch("app.backend.page_contexts.search_context.search_law_summary")
    def test_search_data_custom_pagesize(self, mock_search, sample_dataframe):
        """커스텀 페이지 크기"""
        # Arrange
        mock_search.return_value = sample_dataframe

        # Act
        result = search_data(
            site_names=["site1"],
            keyword="test",
            page=1,
            pagesize=2
        )

        # Assert
        assert result["total"] == 3
        assert result["total_pages"] == 2  # ceil(3/2) = 2
        assert len(result["items"]) == 2

    @patch("app.backend.page_contexts.search_context.search_law_summary")
    def test_search_data_empty_result(self, mock_search):
        """검색 결과가 없는 경우"""
        # Arrange
        mock_search.return_value = pd.DataFrame()

        # Act
        result = search_data(
            site_names=["site1"],
            keyword="nonexistent",
            page=1,
            pagesize=30
        )

        # Assert
        assert result["total"] == 0
        assert result["items"] == []
        assert result["total_pages"] == 0

    @patch("app.backend.page_contexts.search_context.search_law_summary")
    def test_search_data_exception(self, mock_search):
        """예외 발생 시 빈 결과 반환"""
        # Arrange
        mock_search.side_effect = Exception("Database error")

        # Act
        result = search_data(
            site_names=["site1"],
            keyword="test",
            page=1,
            pagesize=30
        )

        # Assert
        assert result["total"] == 0
        assert result["items"] == []
        assert result["page"] == 1
        assert result["total_pages"] == 0

    @patch("app.backend.page_contexts.search_context.search_law_summary")
    def test_search_data_missing_columns(self, mock_search):
        """일부 컬럼이 없는 DataFrame"""
        # Arrange
        partial_df = pd.DataFrame({
            "site_name": ["site1"],
            "사이트": ["사이트1"],
            "제목": ["제목1"],
        })
        mock_search.return_value = partial_df

        # Act
        result = search_data(
            site_names=["site1"],
            keyword="test",
            page=1,
            pagesize=30
        )

        # Assert
        assert len(result["items"]) == 1
        assert result["items"][0]["site_name"] == "사이트1"
        assert result["items"][0]["title"] == "제목1"
        # 없는 컬럼은 빈 문자열로 처리
        assert result["items"][0]["page_id"] == ""
        assert result["items"][0]["site_code"] == "site1"
