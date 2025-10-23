# 프롬프트

## 로그

1. 충실하게 성공시 logger.info를, 실패시 logger.error를 사용할 것
2.

## dashboard

1. 리스트와 상세보기를 탭으로 처리

## search

1. 페이징처리

## statistics

`/statistics` endpoint를 수정하고자 함.

1. 통계분석-법규관련 데이터수집 통계 @app/frontend/views/template/dashboard.html 참조
2. 모든 숫자는 천단위 콤마
3. `전체 수집 사이트` 0 , 전체 수집 페이지 0 -> table  yaml_info 을 참조해서 select count하기 바람
4. `오늘 수집 페이지` 0 -> 전체 게시물 갯수 로 변경 law_summary table의 레코드 갯수
5. `전체 첨부 파일 수` ->전체 첨부 파일 갯수 로 변경 law_summary_attach의 레코드 갯수로
6. 상기 4개를 card로 예쁘게 @app/frontend/views/template/dashboard.html 참조
7. 하단 사이트별 통계 테이블 예쁘게
8. 숫자는 천단위 콤마, 오른쪽 정렬
