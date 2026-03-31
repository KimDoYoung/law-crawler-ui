#!/bin/bash

# 설정 정보
DB_HOST="kfscokr.cafe24.com"
DB_USER="kfscokr"
DB_PASS="kfs8100!!"
DB_NAME="kfscokr"
OUTPUT_FILE="/home/kdy987/law-crawler/ui/homepage-contact-unread.json"

# SQL 실행 및 결과 저장 (헤더 제외, 무음 모드)
# --ssl=0 옵션을 함께 사용하면 MariaDB 클라이언트에서 더 확실하게 SSL을 무시합니다.
CNT=$(mysql -h "$DB_HOST" -u "$DB_USER" -p"$DB_PASS" -D "$DB_NAME" --skip-ssl --ssl=0 -N -e "select count(*) as cnt from contacts where status='unread';")

# 쿼리 실행 성공 여부 확인
if [ $? -eq 0 ]; then
    # JSON 형식으로 파일 작성 (Overwrite)
    echo "{" > "$OUTPUT_FILE"
    echo " \"contact-unread-count\" : ${CNT:-0}" >> "$OUTPUT_FILE"
    echo "}" >> "$OUTPUT_FILE"
    
    echo "✅ 파일 생성 완료: $OUTPUT_FILE (Count: $CNT)"
else
    echo "❌ MySQL 접속 또는 쿼리 실행 실패"
    exit 1
fi