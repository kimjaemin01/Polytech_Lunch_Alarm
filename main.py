import requests
from bs4 import BeautifulSoup
from datetime import datetime

def get_menu():
    url = "https://www.kopo.ac.kr/gangseo/content.do?menu=2625"
    try:
        # 헤더를 추가해서 "나 사람이야"라고 속여야 잘 줍니다.
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=15)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        
        now = datetime.now()
        # 오늘 날짜 (예: 2026-04-02 또는 04.02)
        today_full = now.strftime("%Y-%m-%d")
        today_short = now.strftime("%m.%d")
        
        # 1. 특정 클래스 대신 모든 table을 다 뒤집니다. (안전빵)
        tables = soup.find_all('table')
        lunch_menu = ""

        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                row_text = row.get_text(strip=True)
                
                # 오늘 날짜가 포함된 줄을 찾으면
                if today_full in row_text or today_short in row_text:
                    tds = row.find_all('td')
                    # 사진 구조상: [0]날짜/구분, [1]조식, [2]중식, [3]석식
                    # 또는 [0]날짜/구분, [1]중식 (조식이 없는 경우 대비)
                    
                    # 중식 칸을 안전하게 선택 (보통 뒤에서 2번째나 3번째)
                    if len(tds) >= 3: # 구분, 조식, 중식, 석식 다 있는 경우
                        lunch_menu = tds[1].get_text(separator="\n").strip()
                    elif len(tds) == 2: # 날짜, 중식만 있는 경우
                        lunch_menu = tds[0].get_text(separator="\n").strip()
                    break
            if lunch_menu: break

        if not lunch_menu:
            return f"🍱 [{today_full}] No menu found on page."
        
        return f"🍱 [{today_full}] Lunch:\n{lunch_menu}"

    except Exception as e:
        return f"⚠️ Error: {str(e)[:30]}"

def send_to_ntfy(message):
    url = "https://ntfy.sh/Polytech_Lunch"
    try:
        requests.post(
            url,
            data=message.encode('utf-8'),
            headers={
                "Title": "Lunch Menu",
                "Priority": "high"
            }
        )
    except:
        pass

if __name__ == "__main__":
    content = get_menu()
    send_to_ntfy(content)
