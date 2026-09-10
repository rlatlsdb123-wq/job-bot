import requests
from datetime import datetime

# 아까 복사해 둔 구글 웹 앱 URL 주소를 아래 따옴표 사이에 붙여넣으세요
GOOGLE_WEB_APP_URL = "https://script.google.com/macros/s/AKfycbyltEpJ167e0ZUH-LaaGpI_c-iI1hHZXlabZ_TpKo_nlNQ2lvB-847E3jJz15L65Rvs/exec"

def collect_jobs():
    # 사람인, 잡코리아, 원티드 등 주요 플랫폼에서 조건(경기, 세무/회계/재경, 세무사사무실/7년이상 제외)에 맞는 공고 수집
    # (현재는 정상 연동 테스트용 샘플 공고 데이터가 들어갑니다)
    sample_jobs = [
        {
            "platform": "사람인",
            "company": "(주)경기세무테크",
            "title": "재경팀 결산 및 세무 담당자 채용",
            "location": "경기 성남시 분당구",
            "career": "경력 3~6년",
            "salary": "4,200만원",
            "deadline": "~09/25",
            "link": "https://www.saramin.co.kr"
        },
        {
            "platform": "원티드",
            "company": "OO바이오",
            "title": "회계팀 대리/과장급 자체기장 담당",
            "location": "경기 수원시 영통구",
            "career": "경력 4~6년",
            "salary": "회사내규",
            "deadline": "채용시",
            "link": "https://www.wanted.co.kr"
        }
    ]
    return sample_jobs

def send_to_google_sheet(job, today):
    payload = {
        "date": today,
        "platform": job["platform"],
        "company": job["company"],
        "title": job["title"],
        "location": job["location"],
        "career": job["career"],
        "salary": job["salary"],
        "deadline": job["deadline"],
        "link": job["link"]
    }
    try:
        response = requests.post(GOOGLE_WEB_APP_URL, json=payload)
        print(f"전송 성공: {job['company']}")
    except Exception as e:
        print(f"전송 실패: {e}")

def main():
    today = datetime.now().strftime("%Y-%m-%d")
    jobs = collect_jobs()
    
    if not jobs:
        print("오늘 조건에 맞는 신규 공고가 없습니다.")
        return

    for job in jobs:
        send_to_google_sheet(job, today)

if __name__ == "__main__":
    main()
