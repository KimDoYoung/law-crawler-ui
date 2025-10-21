# main.py
# -*- coding: utf-8 -*-
import os
from st_aggrid import AgGrid, DataReturnMode, GridUpdateMode
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from ui.utils.logger import get_ui_log_contents, setup_logger
from ui.utils.misc_utils import configure_aggrid, configure_search_aggrid, get_log_data
from ui.utils.db_util import attach_list, detail_static, error_count_of_last_24h, get_site_and_code_dict, get_summary_list, search_law_summary, site_static, site_static_filecount, total_site_attach_counts, yaml_info_to_html
from ui.utils.db_manager import DbManager
from ui.utils.ui_settings import UiConfig

logger = setup_logger()

dbManager = DbManager(UiConfig)
dbManager.create_yaml_table()
dbManager.fill_yaml()
# 페이지 설정
st.set_page_config(
    page_title="법규관련 데이터수집 시스템",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 사이드바 설정
st.sidebar.title("⚖️ Law-Crawling")
st.sidebar.markdown("### 법규관련사이트 데이터수집")
st.sidebar.markdown("---")

# 메뉴 선택
menu = st.sidebar.selectbox(
    "📋 메뉴 선택",
    [
        "📊 대시보드",
        "🔍 데이터 조회", 
        "📈 통계 분석",
        "📋 로그 관리",
        "⚙️ 설정"
    ]
)

# 상태 정보
st.sidebar.markdown("---")
st.sidebar.markdown("### 🔄 시스템 상태")
st.sidebar.success("크롤러 상태: 정상")
st.sidebar.info(f"마지막 수집: {dbManager.last_crawling_time()}")

# =============================================================================
# 페이지별 콘텐츠
# =============================================================================
today = datetime.now().strftime("%Y-%m-%d")
three_days_ago = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")
seven_days_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
first_days_age = '1900-01-01'  # 초기 데이터 수집 시작일
if menu == "📊 대시보드":
    st.title("📊 대시보드")
    st.markdown("### 법규관련 데이터수집 현황")

    # 주요 지표
    col1, col2, col3, col4, col5, col_error = st.columns(6)
    site_and_page_count = f"{dbManager.site_count} ({dbManager.page_count})"
    today_site_count, today_attach_count = total_site_attach_counts(today)
    three_site_count, three_attach_count = total_site_attach_counts(three_days_ago)
    seven_site_count, seven_attach_count = total_site_attach_counts(seven_days_ago)
    first_site_count, first_attach_count = total_site_attach_counts(first_days_age)
    error_count = error_count_of_last_24h()
    with col1:
        st.metric(
            label="수집 사이트(pages)",
            value=site_and_page_count,
            delta="정상"
        )
    
    with col2:
        st.metric(
            label="오늘 수집 (첨부파일)",
            value=f"{today_site_count} ({today_attach_count})",
        )
    
    with col3:
        st.metric(
            label="3일 전 (첨부파일)",
            value=f"{three_site_count} ({three_attach_count})",
        )
    
    with col4:
        st.metric(
            label="7일 전 (첨부파일)",
            value=f"{seven_site_count} ({seven_attach_count})",
        )

    with col5:
        st.metric(
            label="전체 (첨부파일)",
            value=f"{first_site_count} ({first_attach_count})",
        )
    with col_error:
        st.metric(
            label="오류 발생",
            value=f"{error_count}",
            delta="최근 수집시"
        )

    st.markdown("---")
    st.subheader("수집된 데이터 조회")
    date_option = st.radio(
        "기간 선택",
        options=["오늘", "3일", "7일"],
        horizontal=True,
        index=0
    ) 
    if date_option == "오늘":
        df = get_summary_list(today)
    elif date_option == "3일":
        df = get_summary_list(three_days_ago)
    elif date_option == "7일":
        df = get_summary_list(seven_days_ago)
    
    grid_options = configure_aggrid(df, selection_mode='single')
    grid_response = AgGrid(
        df,
        gridOptions=grid_options,
        data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        fit_columns_on_grid_load=False,
        theme='streamlit',
        height=300,
        width='100%'
    )
    selected_rows = grid_response['selected_rows']
    if selected_rows is not None:
        selected_row = selected_rows.iloc[0]
        # site_name = f"<a href='{selected_row['site_url']}' target='_blank'>{selected_row['사이트']}</a>"
        site_name = f"[{selected_row['사이트']}]({selected_row['site_url']})"
        page_link = f"[{selected_row['페이지']}]({selected_row['detail_url']})"
        title = f"[{selected_row['제목']}]({selected_row['org_url']})"
        st.markdown(f"**사이트:** {site_name} **페이지:** {page_link}")
        st.markdown(f"**제목:** {title}")
        if selected_row['등록일']:
            st.markdown(f"**등록일:** {selected_row['등록일']} **수집일시:** {selected_row['수집일시']}")
        else:
            st.markdown(f"**수집일시:** {selected_row['수집일시']}")
        # st.markdown("---")
        # st.markdown("**📎 첨부파일 목록:**")
        # attach_df = attach_list(selected_row['site_name'], selected_row['page_id'], selected_row['real_seq'])
        # if attach_df.empty:
        #     st.markdown("<p style='color:blue'>첨부파일이 없습니다.</p>", unsafe_allow_html=True)
        # else:
        #     for _, row in attach_df.iterrows():
        #         physical_path = UiConfig.get_physical_path(selected_row['site_name'], selected_row['page_id'],row['save_file_name'])
        #         # st.markdown(f"Pysical Path: {physical_path}")
        #         if os.path.exists(physical_path):
        #             with open(physical_path, "rb") as f:
        #                 st.download_button(
        #                     label=f"📥 {row['save_file_name']}",
        #                     data=f,
        #                     file_name=row['save_file_name'],
        #                     mime="application/octet-stream"
        #                 )                    
        #             # attach_link = f"[{row['save_file_name']}]({UiConfig.get_attach_url(row['save_folder'], row['save_file_name'])})"
        #             # st.markdown(f"{attach_link}")
        #         else:
        #             st.markdown(f"<p style='color:red'>첨부파일 '{row['save_file_name']}'이(가) 존재하지 않습니다.</p>", unsafe_allow_html=True)
        # st.markdown("---")
        # Summary 요약 
        attach_df = attach_list(selected_row['site_name'], selected_row['page_id'], selected_row['real_seq'])
        attach_len = len(attach_df)
        html_content = selected_row["summary"]
        tab1, tab2, tab3 = st.tabs(["📄 렌더링 보기", "🧾 HTML 코드 보기", f"📥 첨부파일({attach_len})"])

        with tab1:
            st.markdown(html_content, unsafe_allow_html=True)

        with tab2:
            st.code(html_content, language="html")        

        with tab3:
            st.markdown("**📎 첨부파일 목록:**")
            # attach_df = attach_list(selected_row['site_name'], selected_row['page_id'], selected_row['real_seq'])
            # st.markdown(f"첨부파일 갯수: {len(attach_df)}")
            if attach_df.empty:
                st.markdown("<p style='color:blue'>첨부파일이 없습니다.</p>", unsafe_allow_html=True)
            else:
                for _, row in attach_df.iterrows():
                    physical_path = UiConfig.get_physical_path(selected_row['site_name'], selected_row['page_id'],row['save_file_name'])
                    if os.path.exists(physical_path):
                        with open(physical_path, "rb") as f:
                            st.download_button(
                                label=f"📥 {row['save_file_name']}",
                                data=f,
                                file_name=row['save_file_name'],
                                mime="application/octet-stream"
                            )                    
                    else:
                        st.markdown(f"<p style='color:red'>첨부파일 '{row['save_file_name']}'이(가) 존재하지 않습니다.</p>", unsafe_allow_html=True)    

elif menu == "🔍 데이터 조회":
    st.title("🔍 데이터 조회")
    # session_state 초기화 (가장 먼저 실행)
    if 'search_results' not in st.session_state:
        st.session_state.search_results = None
    if 'search_performed' not in st.session_state:
        st.session_state.search_performed = False

    SITE_INFO = get_site_and_code_dict()
    # 검색 옵션
    col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
    
    with col1:
        # 사이트 선택 (멀티 선택 가능)
        site_options = [{"label": "전체", "value": ""}] + [
            {"label": f"{name} ({code})", "value": code} 
            for code, name in SITE_INFO.items()
        ]
        
        selected_sites = st.multiselect(
            "사이트 선택",
            options=[opt["value"] for opt in site_options[1:]],  # 전체 제외
            placeholder="사이트 선택,선택하지 않으면 `전체`사이트에서 검색합니다.",
            format_func=lambda x: f"{SITE_INFO[x]} ({x})" if x in SITE_INFO else x,
            help="여러 사이트를 선택할 수 있습니다. 선택하지 않으면 전체 사이트에서 검색합니다."
        )
    
    with col2:
        # 키워드 입력
        keyword = st.text_input(
            "검색 키워드", 
            placeholder="제목이나 내용에서 검색할 키워드를 입력하세요",
            help="제목과 요약 내용에서 검색됩니다"
        )
    
    with col3:
        # 검색 버튼
        st.markdown('<div style="width:24px; height:24px;"><div>', unsafe_allow_html=True) 
        search_button = st.button("🔍 검색", type="primary", use_container_width=True)

    with col4:
        # 초기화 버튼
        st.markdown('<div style="height:24px;"></div>', unsafe_allow_html=True)
        reset_button = st.button("🔄 초기화", type="secondary", use_container_width=True)

   # 초기화 버튼 클릭 시
    if reset_button:
        # session_state 초기화
        st.session_state.search_results = None
        st.session_state.search_performed = False
        if 'selected_sites' in st.session_state:
            del st.session_state.selected_sites
        if 'keyword' in st.session_state:
            del st.session_state.keyword
        st.session_state.selected_sites = []
        st.session_state.keyword = ""            
        st.rerun()  # 페이지 새로고침

    # 검색 결과
    if search_button:
        st.session_state.search_results = search_law_summary(site_names=selected_sites, keyword=keyword)
        st.session_state.search_performed = True
        st.session_state.selected_sites = selected_sites
        st.session_state.keyword = keyword    
    if st.session_state.search_performed and st.session_state.search_results is not None:
        # st.subheader("📋 검색 결과")
        df = st.session_state.search_results
        if df.empty:
            st.markdown("<p style='color:blue'>검색 결과가 없습니다.</p>", unsafe_allow_html=True)
        else:
            # grid_response = configure_search_aggrid(df, selection_mode='single')
            search_grid_options = configure_search_aggrid(df, selection_mode='single')
            search_response = AgGrid(
                df,
                gridOptions=search_grid_options,
                data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
                update_mode=GridUpdateMode.SELECTION_CHANGED,
                fit_columns_on_grid_load=False,
                theme='streamlit',
                height=400,
                width='100%',
                key='search_grid'  # 고유 키 추가
            )
            selected_rows = search_response['selected_rows']
            if selected_rows is not None and len(selected_rows) > 0:
                # st.write("---")
                st.subheader("📄 선택된 항목 상세 정보")
                selected_row = selected_rows.iloc[0]
                # selected_row = selected_rows.iloc[0]
                site_name = f"[{selected_row['사이트']}]({selected_row['site_url']})"
                page_link = f"[{selected_row['페이지']}]({selected_row['detail_url']})"
                title = f"[{selected_row['제목']}]({selected_row['org_url']})"
                st.markdown(f"**사이트:** {site_name} **페이지:** {page_link}")
                st.markdown(f"**제목:** {title}")
                if selected_row['등록일']:
                    st.markdown(f"**등록일:** {selected_row['등록일']} **수집일시:** {selected_row['수집일시']}")
                else:
                    st.markdown(f"**수집일시:** {selected_row['수집일시']}")
                st.markdown("---")
                st.markdown("**📎 첨부파일 목록:**")
                attach_df = attach_list(selected_row['site_name'], selected_row['page_id'], selected_row['real_seq'])
                if attach_df.empty:
                    st.markdown("<p style='color:blue'>첨부파일이 없습니다.</p>", unsafe_allow_html=True)
                else:
                    for _, row in attach_df.iterrows():
                        physical_path = UiConfig.get_physical_path(selected_row['site_name'], selected_row['page_id'],row['save_file_name'])
                        # st.markdown(f"Pysical Path: {physical_path}")
                        if os.path.exists(physical_path):
                            with open(physical_path, "rb") as f:
                                st.download_button(
                                    label=f"📥 {row['save_file_name']}",
                                    data=f,
                                    file_name=row['save_file_name'],
                                    mime="application/octet-stream"
                                )                    
                            # attach_link = f"[{row['save_file_name']}]({UiConfig.get_attach_url(row['save_folder'], row['save_file_name'])})"
                            # st.markdown(f"{attach_link}")
                        else:
                            st.markdown(f"<p style='color:red'>첨부파일 '{row['save_file_name']}'이(가) 존재하지 않습니다.</p>", unsafe_allow_html=True)
                st.markdown("---")                
                # Summary 요약 
                html_content = selected_row["summary"]
                tab1, tab2 = st.tabs(["📄 렌더링 보기", "🧾 HTML 코드 보기"])

                with tab1:
                    st.markdown(html_content, unsafe_allow_html=True)

                with tab2:
                    st.code(html_content, language="html")

elif menu == "📈 통계 분석":
    st.title("📈 통계 분석")
    
    tab1, tab2 = st.tabs(["📈 수집 통계", "🏢 상세통계표"])
    
    with tab1:
        st.subheader("📊 사이트별 수집 통계")
        # 막대그래프
        static_df = site_static()
        st.bar_chart(static_df.set_index("사이트"))
        df_files = site_static_filecount()
        # 테이블
        df_summary = pd.merge(static_df, df_files, on="사이트", how="outer").fillna(0)
        df_summary[["게시글수", "첨부파일수"]] = df_summary[["게시글수", "첨부파일수"]].astype(int)        
        st.dataframe(df_summary, use_container_width=True)
    with tab2:
        st.subheader("📈 상세통계표 ")
        col1, col2, col3, col4 = st.columns(4)
        today_site_count, today_attach_count = total_site_attach_counts(today)
        first_site_count, first_attach_count = total_site_attach_counts('1900-01-01')
        with col1:
            st.metric(
                label="전체 수집 사이트",
                value=f"{dbManager.site_count}",
                delta="정상"
            )
        with col2:
            st.metric(
                label="오늘 수집 페이지",
                value=f"{dbManager.page_count}",
            )
        with col3:
            st.metric(
                label="전체 수집 사이트(게시글수)",
                value=f"{first_site_count}", 
            )   
        with col4:
            st.metric(
                label="전체 첨부파일수",
                value=f"{first_attach_count}",
            )
        st.subheader("📊 사이트·페이지별 게시글 수 및 첨부파일 수")
        detail_static_df = detail_static()
        st.dataframe(detail_static_df, use_container_width=True)            
        

elif menu == "📋 로그 관리":
    st.title("📋 로그 관리")
    
    tab1, tab2 = st.tabs(["📋 수집(Crawler) 로그", "🔍 UI(웹페이지) 로그"])
    
    with tab1:
        st.subheader("📋 수집-Crawer 로그 목록")
        
        # 로그 날짜 선택
        log_date = st.date_input("📅 로그 날짜", datetime.now(), format="YYYY-MM-DD")
        log_content, log_fullpath = get_log_data(log_date)
        if log_content is None or len(log_content) == 0:
            st.error("해당 날짜의 로그가 없습니다.")
        else:
            log_text = "\n".join(line.rstrip('\n') for line in log_content)
            # st.text_area("내용", log_text, height=500)
            st.markdown(f"**로그 파일 경로:** {log_fullpath}")
            st.markdown(f"""
            <textarea 
                spellcheck="false" 
                style="width: 100%; height: 500px; font-family: 맑은고딕;"
            >{log_text}</textarea>
            """, unsafe_allow_html=True)
            log_file_name = os.path.basename(log_fullpath)
            st.download_button(
                label="📥 로그 파일 다운로드",
                data=log_text,
                file_name=log_file_name,
                mime="text/plain"
            )

    with tab2:
        st.subheader("🔍 UI(웹페이지) 로그 보기")
        ui_log_contents, ui_log_fullpath = get_ui_log_contents(logger)
        log_text = "\n".join(line.rstrip('\n') for line in ui_log_contents)
        # UI 로그 파일 경로       
        st.markdown(f"**로그 파일 경로:** {ui_log_fullpath}")
        st.markdown(f"""
        <textarea
            id="ui-log-area" 
            spellcheck="false" readonly 
            style="width: 100%; height: 500px; font-family: 맑은고딕;"
        >{log_text}</textarea>
        """, unsafe_allow_html=True)
        # 스크립트 별도로 렌더링
        st.markdown("""
        <script>
        function moveToEnd() {
            const textarea = document.getElementById("ui-log-area");
            if (textarea) {
                textarea.focus();
                const textLength = textarea.value.length;
                textarea.setSelectionRange(textLength, textLength);
                textarea.scrollTop = textarea.scrollHeight;
                textarea.blur();
            }
        }

        setTimeout(moveToEnd, 100);
        setTimeout(moveToEnd, 300);
        </script>
        """, unsafe_allow_html=True)        
        log_file_name = os.path.basename(ui_log_fullpath)
        st.download_button(
            label="📥 로그 파일 다운로드",
            data=log_text,
            file_name=log_file_name,
            mime="text/plain"
        )          

elif menu == "⚙️ 설정":
    st.title("⚙️ 시스템 설정")
    
    tab1, tab2, tab3 = st.tabs(["🔧 시스템 소개", "🖥️ 시스템 정보", "📜시스템 History"])
    
    with tab1:
        st.subheader("🔧 설명")
        # info.md 파일 읽어서 출력
        try:
            with open("ui/data/info.md", "r", encoding="utf-8") as f:
                info_content = f.read()
                st.markdown(info_content, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"info.md 파일을 불러올 수 없습니다: {e}")
        
        with st.expander("🏢 대상 사이트 및 리스트"):
            html = yaml_info_to_html()
            st.markdown(html, unsafe_allow_html=True)
    
    with tab2:
        st.subheader("🖥️ 시스템 정보")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Python 버전:** 3.9.7")
            st.write("**Streamlit 버전:** 1.28.0")
            st.write("**데이터베이스:** SQLite")
        
        with col2:
            st.write(f"**수집기(law-crawler)폴더:** {UiConfig.REPOSITORY_DIR}")
            st.write(f"**DB폴더:** {UiConfig.DB_BASE_DIR}")
            st.write(f"**첨부파일폴더:** {UiConfig.FILE_BASE_DIR}")
            st.write(f"**로그파일:** {UiConfig.LOG_DIR}")

    with tab3:
        st.subheader("📜 시스템 History")
        # history.md 파일 읽어서 출력
        try:
            with open("ui/data/history.md", "r", encoding="utf-8") as f:
                history_content = f.read()
                st.markdown(history_content, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"history.md 파일을 불러올 수 없습니다: {e}")
# 푸터
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "ⓒ 2025 Copyright  Korea Fund Service Co., Ltd All Rights Reserved."
    "</div>", 
    unsafe_allow_html=True
)
