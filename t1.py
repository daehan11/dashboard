import streamlit as st
import pandas as pd
import numpy as np
from sklearn.metrics import f1_score
import json
import os
from datetime import datetime
import seaborn as sns
import matplotlib.pyplot as plt

# 페이지 설정
st.set_page_config(
    page_title="데이터 분석 경진대회 리더보드",
    page_icon="📊",
    layout="wide"
)

# 세션 상태 초기화
if 'submissions' not in st.session_state:
    st.session_state.submissions = []

# 정답 데이터 로드 (예시)
def load_ground_truth():
    try:
        ground_truth = pd.read_csv('true.csv')
        if 'target' not in ground_truth.columns:
            st.error("정답 파일에 'target' 컬럼이 필요합니다.")
            return None
        return ground_truth
    except FileNotFoundError:
        st.error("정답 파일(true.csv)을 찾을 수 없습니다.")
        return None
    except Exception as e:
        st.error(f"정답 파일 로드 중 오류 발생: {str(e)}")
        return None

# 제출 파일 검증
def validate_submission(file):
    try:
        df = pd.read_csv(file)
        if 'prediction' not in df.columns:
            return False, "제출 파일에 'prediction' 컬럼이 필요합니다."
        return True, df
    except Exception as e:
        return False, f"파일 로드 중 오류 발생: {str(e)}"

# F1 점수 계산
def calculate_score(predictions, ground_truth):
    return f1_score(ground_truth['target'], predictions['prediction'])

# 메인 UI
st.title("📊 데이터 분석 경진대회 리더보드")

# 사이드바 - 제출 섹션
with st.sidebar:
    st.header("제출하기")
    team_name = st.text_input("팀 이름")
    submission_file = st.file_uploader("예측 결과 파일 업로드", type=['csv'])
    
    if st.button("제출"):
        if not team_name:
            st.error("팀 이름을 입력해주세요.")
        elif submission_file is None:
            st.error("파일을 업로드해주세요.")
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
                
                st.session_state.submissions.append(submission)
                st.success(f"제출 완료! F1 점수: {score:.4f}")
            else:
                st.error(result)

# 메인 영역 - 리더보드
st.header("리더보드")

if st.session_state.submissions:
    # 점수 기준으로 정렬
    sorted_submissions = sorted(
        st.session_state.submissions,
        key=lambda x: x['score'],
        reverse=True
    )
    
    # 리더보드 표시
    leaderboard_data = []
    for idx, submission in enumerate(sorted_submissions, 1):
        leaderboard_data.append({
            '순위': idx,
            '팀명': submission['team_name'],
            'F1 점수': f"{submission['score']:.4f}",
            '제출 시간': submission['timestamp']
        })
    
    df_leaderboard = pd.DataFrame(leaderboard_data)
    st.dataframe(df_leaderboard, use_container_width=True)
    
    # 차트로 시각화
    st.subheader("점수 분포")
    scores = [s['score'] for s in sorted_submissions]
    
    # 가우시안 분포 그래프 생성
    fig, ax = plt.subplots(figsize=(8, 1))
    sns.kdeplot(data=scores, ax=ax)
    ax.set_xlabel('Distribution')
    ax.set_ylabel('Density')
    
    # Streamlit에 플롯 표시
    st.pyplot(fig)
else:
    st.info("아직 제출된 결과가 없습니다.")