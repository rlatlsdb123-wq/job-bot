import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import urllib.parse

# 1. 아까 발급받은 구글 웹 앱 URL을 여기에 붙여넣으세요.
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbyltEpJ167e0ZUH-LaaGpI_c-iI1hHZXlabZ_TpKo_nlNQ2lvB-847E3jJz15L65Rvs/exec"

def scrape_saramin():
    """
    사람인에서 실제 공고를 검색해 스크래핑합니다.
    - 검색어: 세무 회계 재경
    - 지역: 경기 (사람인 지역코드 102000)
    - 제외: 세무사사무실, 세무법인, 회계법인, 7년 이상 경력
    """
    base_url = "https://www.saramin.co.kr/zf_user/search/recruit"
    params = {
        'search_area': 'loc',
        'loc_cd': '102000',       # 경기도 코드
        'searchword': '세무 회계 재경',
        'recruitSort': 'relation',
        'recruitPageCount': '40'
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    exclude_keywords = [
        "세무사사무", "세무법인", "세무회계사무", "회계법인", 
        "세무사", "7년", "8년", "9년", "10년", "팀장", "부장", "차장"
    ]

    collected = []
    
    try:
        res = requests.get(base_url, params=params, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        job_listings = soup.select('.item_recruit')
        
        for item in job_listings:
            # 제목 및 링크
            title_elem = item.select_one('.job_tit a')
            if not title_elem:
                continue
            title = title_elem.get_text(strip=True)
            href = title_elem.get('href', '')
            link = "https://www.saramin.co.kr" + href if href.startswith('/') else href
            
            # 회사명
            corp_elem = item.select_one('.corp_name a')
            company = corp_elem.get_text(strip=True) if corp_elem else "회사명 미표기"
            
            # 근무조건 정보 (지역, 경력, 학력 등)
            conditions = item.select('.job_condition span')
            location = conditions[0].get_text(strip=True) if len(conditions) > 0 else "경기"
            career = conditions[1].get_text(strip=True) if len(conditions) > 1 else "경력무관"
            
            # 연봉 및 마감일
            badge = item.select_one('.area_badge')
            salary = badge.get_text(strip=True) if badge else "회사내규"
            
            date_elem = item.select_one('.job_date .date')
            deadline = date_elem.get_text(strip=True) if date_elem else "채용시"

            # 제외 키워드 필터링 (회사명 또는 제목에 제외 단어가 들어가면 탈락)
            check_text = f"{company} {title}"
            if any(k in check_text for k in exclude_keywords):
                continue
                
            collected.append({
                "platform": "사람인",
                "company": company,
                "title": title,
                "location": location,
                "career": career,
                "salary": salary,
                "deadline": deadline,
                "link": link
            })
            
            # 하루 수집량 상한 (시트 과부하 방지: 최대 15개 선별)
            if len(collected) >= 15:
                break
                
    except Exception as e:
        print(f"스크래핑 오류 발생: {e}")
        
    return collected

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
    try:
        requests.post(GOOGLE_SCRIPT_URL, json=payload, timeout=5)
    except Exception as e:
        print(f"시트 전송 실패: {e}")

def main():
    print("채용공고 스크래핑 시작...")
    jobs = scrape_saramin()
    
    if not jobs:
        print("조건에 맞는 신규 공고를 찾지 못했습니다.")
        return

    print(f"총 {len(jobs)}건의 실제 공고를 찾았습니다. 구글 시트로 전송합니다...")
    for job in jobs:
        send_to_google_sheet(job)
        
    print("전송 완료.")

if __name__ == "__main__":
    main()
