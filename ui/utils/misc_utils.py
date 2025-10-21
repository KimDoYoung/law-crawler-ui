import os
from st_aggrid import GridOptionsBuilder

from ui.utils.logger import setup_logger
from ui.utils.ui_settings import UiConfig

logger = setup_logger()

def wrap_with_div(html, style=""):
    """
    주어진 HTML 문자열을 div 태그로 감싸는 함수입니다.
    
    Args:
        html (str): HTML 문자열
    
    Returns:
        str: div 태그로 감싼 HTML 문자열
    """
    return f"<div style='{style}'>{html}</div>"


# AgGrid 설정 함수
def configure_aggrid(df, selection_mode='single'):
    gb = GridOptionsBuilder.from_dataframe(df)
    
    # 기본 설정
    gb.configure_pagination(paginationAutoPageSize=True)
    gb.configure_side_bar()
    gb.configure_default_column(
        groupable=True, 
        value=True, 
        enableRowGroup=True, 
        aggFunc='sum', 
        editable=False
    )
    
    # 선택 모드 설정
    if selection_mode == 'single':
        gb.configure_selection('single', use_checkbox=True, groupSelectsChildren=True)
    elif selection_mode == 'multiple':
        gb.configure_selection('multiple', use_checkbox=True, groupSelectsChildren=True)
    
    # 컬럼별 설정
    gb.configure_column('사이트', header_name='사이트', width=70, pinned='left')
    gb.configure_column('페이지', header_name='페이지', width=120, pinned='left')
    gb.configure_column('제목', header_name='제목', width=300)
    # gb.configure_column('등', header_name='급여', width=120, 
    #                    type=['numericColumn', 'numberColumnFilter', 'customNumericFormat'],
    #                    valueFormatter="function(params) { return '₩' + params.value.toLocaleString(); }")
    gb.configure_column('등록일', header_name='등록일', width=100)
    gb.configure_column('수집일시', header_name='수집일시', width=150)
    gb.configure_column('real_seq', header_name='페이지ID', width=50, hide=True)
    gb.configure_column('site_url', header_name='사이트url', width=50, hide=True)
    gb.configure_column('detail_url', header_name='게시판url', width=50, hide=True)
    gb.configure_column('org_url', header_name='상세url', width=50, hide=True)
    gb.configure_column('summary', header_name='요약', width=50, hide=True)
    gb.configure_column('site_name', header_name='site_name', width=50, hide=True)
    gb.configure_column('page_id', header_name='page_id', width=50, hide=True)
    return gb.build()

def get_log_data(log_date):
    """
    주어진 날짜의 로그 데이터를 가져오는 함수입니다.
    
    Args:
        log_date (str): 로그 날짜 (YYYY-MM-DD 형식)
    
    Returns:
        list: 해당 날짜의 로그 데이터 리스트
    """
    # 예시로 빈 리스트를 반환합니다. 실제 구현에서는 DB나 파일에서 데이터를 읽어와야 합니다.
    log_fullpath = UiConfig.get_crawler_log_file_path(log_date)
    if os.path.exists(log_fullpath):
        with open(log_fullpath, 'r', encoding='utf-8') as f:
            return f.readlines(), log_fullpath
    else:
        logger.warning(f"로그 파일이 존재하지 않습니다: {log_fullpath}")
    return [], log_fullpath



def configure_search_aggrid(df, selection_mode='single'):
    gb = GridOptionsBuilder.from_dataframe(df)
    
    # 기본 설정
    gb.configure_pagination(paginationAutoPageSize=True)
    gb.configure_side_bar()
    gb.configure_default_column(
        groupable=True, 
        value=True, 
        enableRowGroup=True, 
        aggFunc='sum', 
        editable=False
    )
    
    # 선택 모드 설정
    if selection_mode == 'single':
        gb.configure_selection('single', use_checkbox=True, groupSelectsChildren=True)
    elif selection_mode == 'multiple':
        gb.configure_selection('multiple', use_checkbox=True, groupSelectsChildren=True)
    
    # 컬럼별 설정
    gb.configure_column('사이트', header_name='사이트', width=70, pinned='left')
    gb.configure_column('site_name', header_name='사이트ID', width=50, hide=False)
    gb.configure_column('페이지', header_name='페이지', width=120, pinned='left')
    gb.configure_column('page_id', header_name='페이지ID', width=50, hide=False)
    gb.configure_column('제목', header_name='제목', width=300)
    # gb.configure_column('등', header_name='급여', width=120, 
    #                    type=['numericColumn', 'numberColumnFilter', 'customNumericFormat'],
    #                    valueFormatter="function(params) { return '₩' + params.value.toLocaleString(); }")
    gb.configure_column('등록일', header_name='등록일', width=100)
    gb.configure_column("수집일시", width=160, type=["dateColumnFilter", "customDateTimeFormat"], 
                       custom_format_string='yyyy-MM-dd HH:mm:ss')
    gb.configure_column('real_seq', header_name='real_seq', width=50, hide=True)
    gb.configure_column('site_url', header_name='site_url', width=50, hide=True)
    gb.configure_column('detail_url', header_name='detail_url', width=50, hide=True)
    gb.configure_column('org_url', header_name='org_url', width=50, hide=True)
    gb.configure_column('summary', header_name='summary', width=50, hide=True)
    # gb.configure_column('site_name', header_name='site_name', width=50, hide=True)
    # gb.configure_column('page_id', header_name='page_id', width=50, hide=True)
    return gb.build()