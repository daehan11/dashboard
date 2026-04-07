import streamlit as st
import pandas as pd
import numpy as np
from sklearn.metrics import f1_score
import json
import os
from datetime import datetime
import seaborn as sns
import matplotlib.pyplot as plt
import base64
import io
from sklearn.metrics import mean_squared_error, r2_score

# 페이지 설정
st.set_page_config(
    page_title="Leaderboard",
    page_icon="📊",
    layout="wide"
)

# 정답 데이터 로드
def load_ground_truth():
    try:
        # Streamlit Secrets에서 정답 데이터 로드
        if 'ground_truth_data' not in st.secrets:
            st.error("Target dataset is not loaded")
            return None
            
        # Base64로 인코딩된 데이터를 디코딩
        decoded_data = base64.b64decode(st.secrets['ground_truth_data'])
        
        # CSV 데이터를 DataFrame으로 변환
        ground_truth = pd.read_csv(io.StringIO(decoded_data.decode('utf-8')))
        
        if 'target' not in ground_truth.columns:
            st.error("dataset does not contain target feature.")
            return None
        return ground_truth
    except Exception as e:
        st.error(f"Error: load target dataset: {str(e)}")
        return None

# 제출 파일 검증
def validate_submission(file):
    try:
        df = pd.read_csv(file)
        if 'prediction' not in df.columns:
            return False, "'prediction', the column name, is needed in your file."
        return True, df
    except Exception as e:
        return False, f"Error: Load file: {str(e)}"

# 점수 계산
def calculate_score(predictions, ground_truth):
    if len(predictions) != len(ground_truth):
        st.error("Your file does not match the size of the target data.")
        return None
    return f1_score(ground_truth['target'], predictions['prediction'], average='macro')

# CSV 파일에서 리더보드 데이터 읽기
def load_leaderboard():
    if not os.path.exists('res.csv'):
        return pd.DataFrame(columns=['team_name', 'score', 'timestamp'])
    return pd.read_csv('res.csv')

# CSV 파일에 제출 결과 저장
def save_submission(submission):
    df = load_leaderboard()
    new_row = pd.DataFrame([submission])
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv('res.csv', index=False)

# 메인 UI
st.title("📊 Leaderboard: Week 6")

# 사이드바 - 제출 섹션
with st.sidebar:
    st.header("Submit")
    team_name = st.text_input("Team name")
    submission_file = st.file_uploader("Upload your answer", type=['csv'])
    
    if st.button("Submit"):
        if not team_name:
            st.error("Please put your team name.")
        elif submission_file is None:
            st.error("PLease upload your answer file.")
        else:
            is_valid, result = validate_submission(submission_file)
            if is_valid:
                ground_truth = load_ground_truth()
                score = calculate_score(result, ground_truth)
                
                submission = {
                    'team_name': team_name,
                    'score': score,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                save_submission(submission)
                st.success(f"Submission Completed! Score: {score:.4f}")
            else:
                st.error(result)

# 메인 영역 - 리더보드
st.header("Rankings")

# res.csv에서 데이터 읽기
df_leaderboard = load_leaderboard()

if not df_leaderboard.empty:
    # 점수 기준으로 내림차순 정렬
    df_leaderboard = df_leaderboard.sort_values('score', ascending=False)
    
    # 순위 추가
    df_leaderboard['Ranking'] = range(1, len(df_leaderboard) + 1)
    
    # 컬럼 이름 변경 및 재정렬
    df_display = df_leaderboard.rename(columns={
        'team_name': 'Team',
        'score': 'Score',
        'timestamp': 'Timestamp'
    })[['Ranking', 'Team', 'Score', 'Timestamp']]
    
    # 점수를 소수점 4자리까지 표시
    df_display['Score'] = df_display['Score'].apply(lambda x: f"{x:.4f}")
    
    st.dataframe(df_display, use_container_width=True)
    
    # 차트로 시각화
    st.subheader("Distribution")
    scores = df_leaderboard['score'].values
    
    fig, ax = plt.subplots(figsize=(8, 1))
    sns.kdeplot(data=scores, ax=ax)
    ax.set_xlabel('Distribution')
    ax.set_ylabel('Density')
    
    st.pyplot(fig)
else:
    st.info("No results have beed submitted yet.")