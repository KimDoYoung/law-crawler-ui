"""
Database access utilities for FastAPI backend
"""

import pandas as pd
from sqlite3 import connect
from app.backend.core.logger import get_logger
from app.backend.core.config import config

logger = get_logger(__name__)


def get_summary_db_file():
    """Summary DB 파일 경로 반환"""
    logger.debug(f"DB_PATH: {config.DB_PATH}")
    return config.DB_PATH


def get_data_frame_summary(sql: str, params: tuple = ()) -> pd.DataFrame:
    """쿼리를 실행하고 Pandas DataFrame으로 반환"""
    summary_path = get_summary_db_file()
    conn = connect(summary_path)

    try:
        # SQL 쿼리 로깅
        logger.info(f"📊 SQL 실행: {sql}")
        if params:
            logger.info(f"📌 파라미터: {params}")

        df = pd.read_sql_query(sql, conn, params=params)
        logger.info(f"✅ SQL 결과: {len(df)} rows 반환")
        return df
    except Exception as e:
        logger.error(f"❌ DB 조회 오류: {e}")
        raise RuntimeError(f"DB 조회 오류: {e}")
    finally:
        conn.close()


def total_site_attach_counts(from_date):
    """
    특정 날짜 이후의 전체 사이트와 페이지 수를 반환합니다.
    """
    summary_path = get_summary_db_file()
    conn = connect(summary_path)
    cursor = conn.cursor()

    sql = """
        SELECT
            (SELECT COUNT(*) FROM law_summary WHERE upd_time >= ?) AS summary_count,
            (SELECT COUNT(*) FROM law_summary_attach WHERE upd_time >= ?) AS attach_count
    """

    logger.info(f"📊 SQL 실행 (total_site_attach_counts): {sql.strip()}")
    logger.info(f"📌 파라미터: from_date={from_date}")

    cursor.execute(sql, (from_date, from_date))

    summary_count, attach_count = cursor.fetchone()
    logger.info(f"✅ SQL 결과: summary_count={summary_count}, attach_count={attach_count}")
    conn.close()
    return summary_count, attach_count


def error_count_of_last_24h():
    """
    최근 24시간 이내의 에러 로그 수를 반환합니다.
    """
    summary_path = get_summary_db_file()
    conn = connect(summary_path)
    cursor = conn.cursor()

    sql = """
        SELECT COUNT(*)
        FROM law_summary
        WHERE category = 'LOG'
        AND DATE(upd_time) = (SELECT DATE(MAX(upd_time)) FROM law_summary)
    """

    logger.info(f"📊 SQL 실행 (error_count_of_last_24h): {sql.strip()}")
    cursor.execute(sql)

    error_count = cursor.fetchone()[0]
    logger.info(f"✅ SQL 결과: error_count={error_count}")
    conn.close()
    return error_count


def get_summary_list(from_date: str) -> pd.DataFrame:
    """특정 날짜 이후의 요약 목록 반환"""
    sql = """
        SELECT
            b.h_name as "사이트",
            b.desc as "페이지",
            a.title "제목",
            a.register_date as "등록일",
            a.upd_time as "수집일시",
            a.site_name,
            a.page_id,
            a.real_seq ,
            b.url as "site_url",
            b.detail_url as "detail_url",
            a.org_url as "org_url",
            a.summary

        FROM
            law_summary a
        INNER JOIN
            yaml_info b
        ON
            a.site_name = b.site_name AND a.page_id = b.page_id
        WHERE
            a.upd_time >= ?
        ORDER BY
            a.site_name, a.register_date DESC
    """
    summary_path = get_summary_db_file()
    conn = connect(summary_path)

    try:
        params = (from_date,)
        df = pd.read_sql_query(sql, conn, params=params)
        return df
    except Exception as e:
        raise RuntimeError(f"DB 조회 오류: {e}")
    finally:
        conn.close()


def attach_list(site_name: str, page_id: str, real_seq: str):
    """
    특정 사이트와 페이지의 첨부파일 목록을 반환합니다.
    """
    query = """
    SELECT id, parent_id, save_folder, save_file_name
    FROM law_summary_attach
    WHERE parent_id = (
        SELECT id FROM law_summary
        WHERE site_name = ? AND page_id = ? AND real_seq = ?
    )
    """
    return get_data_frame_summary(query, (site_name, page_id, real_seq))


def site_static():
    """
    전체 사이트의 통계 정보를 반환합니다.
    """
    query = """
        SELECT
            b.h_name as "사이트", count(*) as "게시글수"
        FROM
            law_summary a
        INNER JOIN
            yaml_info b
        ON
            a.site_name = b.site_name AND a.page_id = b.page_id
		GROUP BY b.h_name
    """
    return get_data_frame_summary(query)


def site_static_filecount():
    """
    전체 사이트의 첨부파일 통계 정보를 반환합니다.
    """
    query = """
        select
            c.h_name as "사이트",count(*) as "첨부파일수"
        from law_summary a
            inner join law_summary_attach b
            on a.id = b.parent_id
            inner join yaml_info c
            on a.site_name = c.site_name and a.page_id = c.page_id
        group by c.h_name
    """
    return get_data_frame_summary(query)


def detail_static():
    """사이트별 상세 통계 정보 반환"""
    sql1 = """
        SELECT
            b.h_name as "사이트",
			b.desc as "페이지",
			count(*) as '갯수'
        FROM
            law_summary a
        INNER JOIN
            yaml_info b
        ON
            a.site_name = b.site_name AND a.page_id = b.page_id
		GROUP BY b.h_name, b.page_id
		ORDER BY b.site_name, b.page_id
    """
    sql2 = """
        select
            c.h_name as '사이트',
            c.desc as '페이지',
            count(*) as '파일갯수'
        from law_summary a
            inner join law_summary_attach b
            on a.id = b.parent_id
            inner join yaml_info c
            on a.site_name = c.site_name and a.page_id = c.page_id
        group by c.site_name, c.page_id
        order by c.site_name, c.page_id
    """
    df1 = get_data_frame_summary(sql1)
    df2 = get_data_frame_summary(sql2)

    # 두 DataFrame을 합치기
    df = pd.merge(
        df1,
        df2,
        on=["사이트", "페이지"],
        how="outer",
        suffixes=("_게시글수", "_첨부파일수"),
    )

    # NaN 값을 0으로 대체
    df.fillna(0, inplace=True)

    return df


def yaml_info_to_html():
    """
    yaml_info 테이블의 데이터를 HTML 테이블로 변환합니다.
    """
    query = """
        SELECT
            site_name, page_id, h_name, "desc", url, detail_url
        FROM
            yaml_info
        ORDER BY
            site_name, page_id
    """
    df = get_data_frame_summary(query)

    if df.empty:
        return "<p>데이터가 없습니다.</p>"

    html = """
    <table border='1'>
        <thead style='background-color: #f2f2f2;'>
            <tr><th>사이트명</th><th>페이지ID</th><th>URL</th></tr>
        </thead>
        <tbody>
    """
    for _, row in df.iterrows():
        detail_url = row["detail_url"] if row["detail_url"] else "#"
        html += "<tr>"
        html += f"<td>{row['h_name']}</td>"
        html += f"<td>{row['desc']}</td>"
        html += f'<td><a href="{detail_url}" target="_blank">{detail_url}</a></td>'
        html += "</tr>"

    html += "</tbody></table>"
    return html


def get_site_and_code_dict():
    """사이트 코드와 이름 매핑 딕셔너리 반환"""
    sql = """
        select DISTINCT SITE_NAME, H_NAME from yaml_info ORDER BY H_NAME
    """
    df = get_data_frame_summary(sql)
    site_dict = {}
    for _, row in df.iterrows():
        site_name = row["site_name"]
        h_name = row["h_name"]
        if site_name not in site_dict:
            site_dict[site_name] = h_name
    return site_dict


def search_law_summary(site_names=None, keyword=None):
    """법령 요약 검색 함수"""
    try:
        # 검색 조건 로깅
        logger.info(f"🔍 검색 시작 - 사이트: {site_names}, 키워드: '{keyword}'")

        base_query = """
        SELECT
            b.h_name as "사이트",
            b.desc as "페이지",
            a.title as "제목",
            a.register_date as "등록일",
            a.upd_time as "수집일시",
            a.site_name,
            a.page_id,
            a.real_seq,
            b.url as "site_url",
            b.detail_url as "detail_url",
            a.org_url as "org_url",
            a.summary
        FROM
            law_summary a
        INNER JOIN
            yaml_info b
        ON
            a.site_name = b.site_name AND a.page_id = b.page_id
        WHERE 1=1
        """

        conditions = []
        params = []

        # 사이트명 조건 추가
        if site_names and len(site_names) > 0:
            placeholders = ",".join(["?" for _ in site_names])
            conditions.append(f"a.site_name in ({placeholders})")
            params.extend(site_names)
            logger.debug(f"📌 사이트 조건 추가: {site_names}")

        # 키워드 조건 추가
        if keyword and keyword.strip():
            conditions.append("(a.title like ? or a.summary like ?)")
            keyword_param = f"%{keyword.strip()}%"
            params.extend([keyword_param, keyword_param])
            logger.debug(f"📌 키워드 조건 추가: '{keyword}'")

        # 조건 추가
        if conditions:
            base_query += " AND " + " AND ".join(conditions)

        # 정렬 추가
        base_query += " ORDER BY a.site_name, a.page_id, a.register_date DESC"

        logger.debug(f"🔗 최종 쿼리: {base_query}")
        logger.debug(f"🔗 파라미터: {params}")

        df = get_data_frame_summary(base_query, tuple(params))
        if df.empty:
            logger.info("❌ 검색 결과가 없습니다.")
            return pd.DataFrame()

        logger.info(f"✅ 검색 완료: {len(df)}개 항목 반환")
        return df

    except Exception as e:
        logger.error(f"❌ 법령 요약 검색 쿼리 생성 오류: {e}")
        return pd.DataFrame()
