import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# 구글 웹 앱 URL을 여기에 입력하세요.
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbyltEpJ167e0ZUH-LaaGpI_c-iI1hHZXlabZ_TpKo_nlNQ2lvB-847E3jJz15L65Rvs/exec"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

exclude_keywords = [
    "세무사사무", "세무법인", "세무회계사무", "회계법인", 
    "세무사", "7년", "8년", "9년", "10년", "팀장", "부장", "차장"
]

def scrape_saramin():
    """사람인 공고 수집"""
    print("사람인 공고 수집 중...")
    base_url = "https://www.saramin.co.kr/zf_user/search/recruit"
    params = {
        'search_area': 'loc',
        'loc_cd': '102000',       # 경기
        'searchword': '세무 회계 재경',
        'recruitSort': 'relation',
        'recruitPageCount': '20'
    }
    
    collected = []
    try:
        res = requests.get(base_url, params=params, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        job_listings = soup.select('.item_recruit')
        
        for item in job_listings:
            title_elem = item.select_one('.job_tit a')
            if not title_elem:
                continue
            title = title_elem.get_text(strip=True)
            href = title_elem.get('href', '')
            # 상세 링크 완성
            link = "https://www.saramin.co.kr" + href if href.startswith('/') else href
            
            corp_elem = item.select_one('.corp_name a')
            company = corp_elem.get_text(strip=True) if corp_elem else "회사명 미표기"
            
            conditions = item.select('.job_condition span')
            location = conditions[0].get_text(strip=True) if len(conditions) > 0 else "경기"
            career = conditions[1].get_text(strip=True) if len(conditions) > 1 else "경력무관"
            
            badge = item.select_one('.area_badge')
            salary = badge.get_text(strip=True) if badge else "회사내규"
            
            date_elem = item.select_one('.job_date .date')
            deadline = date_elem.get_text(strip=True) if date_elem else "채용시"

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
            if len(collected) >= 10:
                break
    except Exception as e:
        print(f"사람인 스크래핑 오류: {e}")
        
    return collected

def scrape_jobkorea():
    """잡코리아 공고 수집"""
    print("잡코리아 공고 수집 중...")
    # 잡코리아 통합검색 URL (경기 지역, 세무 회계 재경 키워드)
    base_url = "https://www.jobkorea.co.kr/Search/"
    params = {
        'stext': '세무 회계 재경',
        'local': 'I000' # 경기도 지역 코드 예시
    }
    
    collected = []
    try:
        res = requests.get(base_url, params=params, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        # 잡코리아 개별 공고 아이템 선택자 (사이트 개편에 따라 다를 수 있음)
        job_listings = soup.select('.list-item')
        
        for item in job_listings:
            title_elem = item.select_one('.information-title-link')
            if not title_elem:
                continue
            title = title_elem.get_text(strip=True)
            href = title_elem.get('href', '')
            link = "https://www.jobkorea.co.kr" + href if href.startswith('/') else href
            
            corp_elem = item.select_one('.name')
            company = corp_elem.get_text(strip=True) if corp_elem else "회사명 미표기"
            
            options = item.select('.option span')
            location = options[0].get_text(strip=True) if len(options) > 0 else "경기"
            career = options[1].get_text(strip=True) if len(options) > 1 else "경력무관"
            
            check_text = f"{company} {title}"
            if any(k in check_text for k in exclude_keywords):
                continue
                
            collected.append({
                "platform": "잡코리아",
                "company": company,
                "title": title,
                "location": location,
                "career": career,
                "salary": "회사내규",
                "deadline": "채용시",
                "link": link
            })
            if len(collected) >= 10:
                break
    except Exception as e:
        print(f"잡코리아 스크래핑 오류: {e}")
        
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
    print("채용공고 통합 스크래핑 시작...")
    
    all_jobs = []
    all_jobs.extend(scrape_saramin())
    all_jobs.extend(scrape_jobkorea())
    
    if not all_jobs:
        print("조건에 맞는 신규 공고를 찾지 못했습니다.")
        return

    print(f"총 {len(all_jobs)}건의 공고를 찾았습니다. 구글 시트로 전송합니다...")
    for job in all_jobs:
        send_to_google_sheet(job)
        
    print("전송 완료.")

if __name__ == "__main__":
    main()
