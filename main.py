# app.py
import streamlit as st
import os
from googleapiclient.discovery import build
from wordcloud import WordCloud
import matplotlib.pyplot as plt

st.set_page_config(page_title="유튜브 댓글 워드클라우드", layout="wide")
st.title("📺 유튜브 댓글 워드클라우드 분석기")

# Streamlit secrets 또는 환경 변수에서 API 키 가져오기
api_key = st.secrets.get("YOUTUBE_API_KEY", os.environ.get("YOUTUBE_API_KEY", ""))

if not api_key:
    st.error("YOUTUBE_API_KEY가 설정되지 않았습니다. 스트림릿 클라우드 시크릿을 확인해주세요.")
    st.stop()

video_url = st.text_input("유튜브 영상 URL 또는 비디오 ID를 입력하세요:")

if st.button("댓글 분석 및 워드클라우드 생성"):
    if video_url:
        with st.spinner("댓글을 수집하고 분석하는 중입니다..."):
            try:
                # 비디오 ID 추출
                video_id = video_url.split("v=")[-1].split("&")[0] if "v=" in video_url else video_url.split("/")[-1].split("?")[0]
                
                # 유튜브 API 클라이언트 빌드
                youtube = build('youtube', 'v3', developerKey=api_key)
                
                # 댓글 가져오기
                comments = []
                request = youtube.commentThreads().list(
                    part="snippet",
                    videoId=video_id,
                    maxResults=100, # 필요시 100개 이상 가져오도록 페이지네이션 추가 가능
                    textFormat="plainText"
                )
                response = request.execute()
                
                for item in response.get("items", []):
                    comment = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
                    comments.append(comment)
                
                if comments:
                    text_data = " ".join(comments)
                    
                    # 워드클라우드 생성 (한글 지원을 위해 폰트 경로 설정이 필요할 수 있으나 기본 설정으로 진행)
                    wordcloud = WordCloud(
                        width=1000, 
                        height=500, 
                        background_color='white', 
                        colormap='viridis',
                        max_words=150
                    ).generate(text_data)
                    
                    # 화면 출력
                    st.success(f"총 {len(comments)}개의 댓글을 성공적으로 분석했습니다!")
                    
                    fig, ax = plt.subplots(figsize=(15, 8))
                    ax.imshow(wordcloud, interpolation='bilinear')
                    ax.axis('off')
                    st.pyplot(fig)
                    
                    with st.expander("수집된 원본 댓글 보기"):
                        for i, c in enumerate(comments, 1):
                            st.write(f"{i}. {c}")
                else:
                    st.warning("이 영상에는 댓글이 없거나 수집할 수 없습니다.")
                    
            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")
    else:
        st.warning("유튜브 URL이나 비디오 ID를 입력해주세요.")
