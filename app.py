import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

# Flask 앱 초기화
app = Flask(__name__)
# 다른 출처(HTML 파일)에서의 요청을 허용 (CORS 설정)
CORS(app)

# .env 파일에서 DB 접속 정보 가져오기
db_config = {
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_DATABASE')
}

# 데이터 수집 API 엔드포인트 생성
@app.route('/api/collect', methods=['POST'])
def collect_data():
    # 프론트엔드에서 보낸 JSON 데이터 가져오기
    data = request.get_json()
    job = data.get('job')
    problem = data.get('problem')

    # 필수 데이터가 없는 경우 오류 응답
    if not job or not problem:
        return jsonify({'message': '직무와 문제점 데이터가 필요합니다.'}), 400

    conn = None
    cursor = None
    try:
        # 데이터베이스에 연결
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # SQL 쿼리문 (SQL Injection 방지)
        sql = "INSERT INTO problem_gov (job_title, problem_description) VALUES (%s, %s)"
        values = (job, problem)
        
        # 쿼리 실행
        cursor.execute(sql, values)
        # 변경사항 최종 저장
        conn.commit()

        # 성공 로그 및 응답
        insert_id = cursor.lastrowid
        print(f"데이터 저장 성공! ID: {insert_id}, 직무: {job}")
        return jsonify({'message': '데이터가 성공적으로 저장되었습니다.', 'dataId': insert_id}), 201

    except mysql.connector.Error as err:
        # 오류 발생 시 로그 및 오류 응답
        print(f"DB 저장 오류: {err}")
        return jsonify({'message': '서버에서 데이터를 저장하는 데 실패했습니다.'}), 500
    
    finally:
        # 사용한 DB 연결 자원 반납 (매우 중요)
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

# 이 파일이 직접 실행될 때만 서버를 가동
if __name__ == '__main__':
    # 외부에서 접속 가능하도록 host='0.0.0.0' 으로 설정
    app.run(host='0.0.0.0', port=5000)