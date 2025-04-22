import base64
import os

try:
    # 현재 작업 디렉토리 출력
    print(f"현재 작업 디렉토리: {os.getcwd()}")
    print(f"true.csv 파일 존재 여부: {os.path.exists('true.csv')}")
    
    # true.csv 파일을 Base64로 인코딩
    with open('true.csv', 'rb') as file:
        encoded_data = base64.b64encode(file.read()).decode('utf-8')
        print("\n=== Base64 인코딩된 데이터 ===")
        print(encoded_data)
        print("\n=== Streamlit Secrets 설정 형식 ===")
        print(f'ground_truth_data = "{encoded_data}"')
except Exception as e:
    print(f"오류 발생: {str(e)}") 