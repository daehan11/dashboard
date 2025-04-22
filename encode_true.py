import base64

# true.csv 파일을 Base64로 인코딩
with open('true.csv', 'rb') as file:
    encoded_data = base64.b64encode(file.read()).decode('utf-8')
    print("\n=== Base64 인코딩된 데이터 ===")
    print(encoded_data)
    print("\n=== Streamlit Secrets 설정 형식 ===")
    print(f'ground_truth_data = "{encoded_data}"') 