import requests
from bs4 import BeautifulSoup
from datetime import datetime

def get_menu():
    url = "https://www.kopo.ac.kr/gangseo/content.do?menu=2625"
    try:
        # 1. 오늘 요일 (월:0, 화:1, 수:2, 목:3, 금:4)
        weekday = datetime.now().weekday()
        if weekday > 4: return None 

        res = requests.get(url, timeout=15)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 2. 모든 데이터 칸(td)을 다 찾습니다.
        # 캡처본 기준: 한 요일당 4개의 칸이 있습니다 (날짜, 조식, 중식, 석식)
        all_tds = soup.find_all('td')
        
        if len(all_tds) < 20: # 월~금 데이터가 최소 20개는 있어야 함 (5일 * 4칸)
            return "⚠️ 표 데이터를 읽어오지 못했습니다. (칸 부족)"

        # 3. 인덱스 계산 (매우 중요!)
        # 월요일 중식: index 2
        # 화요일 중식: index 6 (2 + 4)
        # 수요일 중식: index 10 (6 + 4)
        # 공식: (오늘요일숫자 * 4) + 2
        target_index = (weekday * 4) + 2
        
        lunch_menu = all_tds[target_index].get_text(separator="\n", strip=True)
        
        if not lunch_menu or "등록된" in lunch_menu:
            lunch_menu = "오늘 등록된 식단이 없습니다."

        days = ["월", "화", "수", "목", "금"]
        return f"🍱 [{days[weekday]}요일 중식]\n{lunch_menu}"

    except Exception as e:
        # 에러 발생 시 구체적인 이유를 포함합니다.
        return f"⚠️ 에러 발생: {str(e)}"

def send_to_ntfy(message):
    if not message: return
    url = "https://ntfy.sh/Polytech_Lunch"
    requests.post(url, data=message.encode('utf-8'))

if __name__ == "__main__":
    content = get_menu()
    send_to_ntfy(content)
