# law=crawler의 sqlite tables

## law_summary.db

```sql
-- 법규사이트의 게시판의 내용을 가져온 내용을 저장한다.
CREATE TABLE law_summary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL DEFAULT 'DATA',
            site_name TEXT NOT NULL,
            page_id TEXT NOT NULL,
            real_seq TEXT,
            title TEXT,
            register_date TEXT,
            org_url TEXT,
            summary TEXT,
            upd_time DATETIME DEFAULT CURRENT_TIMESTAMP
        )
  
-- 법규사이트의 게시판의 게시물에 대한 다운로드한 첨부파일의 정보
-- parent_id는 law_summary의 id임
CREATE TABLE law_summary_attach (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            parent_id INTEGER NOT NULL,
            save_folder TEXT,
            save_file_name TEXT,
            upd_time DATETIME DEFAULT CURRENT_TIMESTAMP
        )
-- 법규사이트의 목록  
CREATE TABLE yaml_info (
                    site_name TEXT NOT NULL,
                    page_id TEXT NOT NULL,
                    h_name TEXT,
                    desc TEXT,
                    url TEXT,
                    detail_url TEXT,
                    PRIMARY KEY (site_name, page_id)
                )  
```
