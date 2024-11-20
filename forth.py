import requests
import pandas as pd
from datetime import datetime
import schedule
import time

# YouTube Data API 키 설정
API_KEY = "AIzaSyCtIyJ2wML0ZrMIgvYZmDWCi0cIrKxOpWo"

# 채널 ID 목록
CHANNEL_IDS = ["UCsJ6RuBiTVWRX156FVbeaGg", "UCJo6G1u0e_-wS-JQn3T-zEw"]

# 요청 URL 템플릿
BASE_URL = "https://www.googleapis.com/youtube/v3"

# 데이터 저장 함수
def fetch_youtube_data():
    all_videos = []
    for channel_id in CHANNEL_IDS:
        # 채널의 업로드된 비디오 재생목록 ID 가져오기
        url = f"{BASE_URL}/channels?part=contentDetails&id={channel_id}&key={API_KEY}"
        response = requests.get(url).json()
        
        try:
            upload_playlist_id = response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
        except KeyError:
            print(f"Error fetching data for channel: {channel_id}")
            continue

        # 업로드된 비디오 정보 가져오기
        playlist_url = f"{BASE_URL}/playlistItems?part=snippet,contentDetails&playlistId={upload_playlist_id}&maxResults=10&key={API_KEY}"
        video_response = requests.get(playlist_url).json()

        for video in video_response.get("items", []):
            video_id = video["contentDetails"]["videoId"]
            video_details_url = f"{BASE_URL}/videos?part=snippet,statistics&id={video_id}&key={API_KEY}"
            video_details = requests.get(video_details_url).json()

            if "items" in video_details and video_details["items"]:
                video_info = video_details["items"][0]
                title = video_info["snippet"]["title"]
                view_count = video_info["statistics"].get("viewCount", 0)
                published_time = video_info["snippet"]["publishedAt"]

                # 데이터 저장
                all_videos.append({
                    "Channel ID": channel_id,
                    "Title": title,
                    "Views": view_count,
                    "Published Time": published_time
                })

    # 데이터를 CSV 파일로 저장
    df = pd.DataFrame(all_videos)
    filename = f"youtube_data_{datetime.now().strftime('%Y%m%d')}.csv"
    df.to_csv(filename, index=False, encoding="utf-8-sig")
    print(f"Data saved to {filename}")

# 스케줄 설정 (매일 1회 실행)
schedule.every().day.at("09:00").do(fetch_youtube_data)

print("YouTube data fetcher is running...")
# while True:
#     schedule.run_pending()
#     time.sleep(1)

fetch_youtube_data()
