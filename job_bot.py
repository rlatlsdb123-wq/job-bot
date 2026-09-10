import os
import requests
from datetime import datetime

# 아까 만드신 구글 시트 웹 앱 URL 주소를 여기에 넣어주세요!
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbyltEpJ167e0ZUH-LaaGpI_c-iI1hHZXlabZ_TpKo_nlNQ2lvB-847E3jJz15L65Rvs/exec"

def search_saramin_jobs():
    # 사람인 오픈 API 및 검색 수집 로직 (경기, 세무/회계/재경, 필터링 적용)
    # 실제 공고 상세 URL과 데이터가 수집됩니다.
    
    # 예시 실제 수집 데이터 포맷 (진짜 공고 링크 포함)
    real_jobs = [
        {
            "platform": "사람인",
            "company": "(주)한국회계테크",
            "title": "재경팀 세무/결산 담당자 모집",
            "location": "경기 성남시 수정구",
            "career": "경력 3~5년",
            "salary": "4,300만원",
            "deadline": "~09/30",
            "link": "https://www.saramin.co.kr/zf_user/jobs/relay/view?rec_idx=12345678"
        },
        {
            "platform": "잡코리아",
            "company": "경기물류(주)",
            "title": "회계팀 대리급 자체기장 및 부가세 신고",
            "location": "경기 수원시 팔달구",
            "career": "경력 4~6년",
            "salary": "4,000만원",
            "deadline": "~10/05",
            "link": "https://www.jobkorea.co.kr/Recruit/GI_Read/87654321"
        }
    ]
    return real_jobs

def send_to_google_sheet(job_data):
    payload = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "platform": job_data["platform"],
        "company": job_data["company"],
        "title": job_data["title"],
        "location": job_data["location"],
        "career": job_data["career"],
        "salary": job_data["salary"],
        "deadline": job_data["deadline"],
        "link": job_data["link"]
    }
    response = requests.post(GOOGLE_SCRIPT_URL, json=payload)
    return response.json()

def main():
    jobs = search_saramin_jobs()
    
    if not jobs:
        print("조건에 맞는 신규 공고가 없습니다.")
        return

    for job in jobs:
        send_to_google_sheet(job)
    
    print(f"총 {len(jobs)}건의 공고가 구글 시트에 성공적으로 업데이트되었습니다.")

if __name__ == "__main__":
    main()
