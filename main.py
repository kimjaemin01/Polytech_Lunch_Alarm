import requests
from bs4 import BeautifulSoup
from datetime import datetime

def get_menu():
    url = "https://www.kopo.ac.kr/gangseo/content.do?menu=2625"
    try:
        # 1. 오늘 요일 (월=0, 화=1, 수=2, 목=3, 금=4)
        weekday = datetime.now().weekday()
        if weekday > 4: return None # 주말은 패스

        # 2. 홈페이지 접속해서 표 읽기
        res = requests.get(url, timeout=10)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 3. '데이터가 들어있는 줄'들만 싹 모으기
        # (첫 번째 줄은 제목이니까 제외하고, 내용이 있는 줄만 선택)
        rows = [tr for tr in soup.find_all('tr') if tr.find('td')]
        
        # 오늘 요일에 맞는 줄에서 3번째 칸(중식) 가져오기
        today_row = rows[weekday]
        lunch = today_row.find_all('td')[2].get_text(separator="\n", strip=True)
        
        days = ["월", "화", "수", "목", "금"]
        return f"🍱 [{days[weekday]}요일 중식]\n{lunch}"

    except Exception:
        return "🍱 식단 정보를 가져오지 못했습니다."

def send_to_ntfy(message):
    if not message: return
    requests.post("https://ntfy.sh/Polytech_Lunch", data=message.encode('utf-8'))

if __name__ == "__main__":
    send_to_ntfy(get_menu())
