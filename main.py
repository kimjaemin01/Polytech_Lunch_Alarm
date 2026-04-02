import requests
from bs4 import BeautifulSoup
from datetime import datetime

def get_menu():
    url = "https://www.kopo.ac.kr/gangseo/content.do?menu=2625"
    try:
        # 1. 브라우저인 척 속이는 헤더 (매우 중요)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Referer': 'https://www.kopo.ac.kr/'
        }
        
        # 2. 오늘 요일 (월:0 ~ 금:4)
        weekday = datetime.now().weekday()
        if weekday > 4: return None 

        # 3. 페이지 요청
        res = requests.get(url, headers=headers, timeout=20)
        res.encoding = 'utf-8'
        
        # 만약 접속 자체가 막혔다면
        if res.status_code != 200:
            return f"⚠️ 접속 차단됨 (Status: {res.status_code})"

        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 4. 모든 td 찾기
        all_tds = soup.find_all('td')
        
        # 디버깅: td가 왜 없는지 확인하기 위해 전체 텍스트 길이를 봅니다.
        if not all_tds:
            text_len = len(res.text.strip())
            return f"⚠️ 표를 찾을 수 없음 (응답 길이: {text_len}자)"

        # 5. 인덱스로 중식 가져오기 (날짜, 조식, 중식, 석식 순서)
        # 캡처본 구조상 한 요일은 4개의 td를 차지함
        target_index = (weekday * 4) + 2
        
        if len(all_tds) > target_index:
            lunch_menu = all_tds[target_index].get_text(separator="\n", strip=True)
            
            # 불필요한 글자 정리
            lunch_menu = lunch_menu.replace("중식", "").strip()
            
            if not lunch_menu or "등록된" in lunch_menu:
                lunch_menu = "오늘 등록된 식단이 없습니다."
        else:
            lunch_menu = f"데이터 부족 (발견된 칸: {len(all_tds)}개)"

        days = ["월", "화", "수", "목", "금"]
        return f"🍱 [{days[weekday]}요일 중식]\n{lunch_menu}"

    except Exception as e:
        return f"⚠️ 시스템 오류: {str(e)[:30]}"

def send_to_ntfy(message):
    if not message: return
    url = "https://ntfy.sh/Polytech_Lunch"
    requests.post(url, data=message.encode('utf-8'))

if __name__ == "__main__":
    content = get_menu()
    send_to_ntfy(content)
