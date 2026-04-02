import requests
from bs4 import BeautifulSoup
from datetime import datetime

def get_menu():
    url = "https://www.kopo.ac.kr/gangseo/content.do?menu=2625"
    try:
        # 브라우저처럼 보이게 해서 차단을 피합니다.
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        res = requests.get(url, headers=headers, timeout=20)
        res.encoding = 'utf-8'
        
        # HTML 통째로 가져오기
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 1. 요일 확인 (월:0 ~ 금:4)
        weekday = datetime.now().weekday()
        if weekday > 4:
            return None # 주말은 전송 안 함

        # 2. 클래스명 무시하고 모든 table 태그를 다 찾습니다.
        tables = soup.find_all('table')
        if not tables:
            return "⚠️ 페이지에서 표(table)를 아예 찾을 수 없습니다."

        # 3. 첫 번째 표의 행(tr)들을 가져옵니다.
        # 보통 식단표 페이지에는 식단표가 가장 메인 표입니다.
        rows = tables[0].find_all('tr')
        
        # 제목 줄(Header)이 있을 수 있으니 실제 데이터는 보통 1번째 인덱스부터 시작합니다.
        # 요일 인덱스(0~4)에 +1을 해서 실제 행을 맞춥니다.
        target_index = weekday + 1 
        
        if len(rows) > target_index:
            target_row = rows[target_index]
            cells = target_row.find_all(['td', 'th'])
            
            # 구조: [0]날짜/요일, [1]조식, [2]중식, [3]석식
            if len(cells) >= 3:
                # 중식은 3번째 칸(index 2)
                lunch_menu = cells[2].get_text(separator="\n").strip()
                
                if not lunch_menu or "등록된" in lunch_menu:
                    lunch_menu = "오늘 등록된 식단이 없습니다."
            else:
                lunch_menu = "표의 칸(Column) 개수가 부족합니다."
        else:
            lunch_menu = "표의 행(Row) 개수가 부족합니다."

        weekdays_ko = ["월요일", "화요일", "수요일", "목요일", "금요일"]
        return f"🍱 [{weekdays_ko[weekday]}] 중식:\n{lunch_menu}"

    except Exception as e:
        return f"⚠️ 시스템 오류: {str(e)[:30]}"

def send_to_ntfy(message):
    if not message: return
    url = "https://ntfy.sh/Polytech_Lunch"
    try:
        requests.post(url, data=message.encode('utf-8'), headers={"Title": "Lunch Menu"})
        print("Success")
    except:
        print("Failed")

if __name__ == "__main__":
    content = get_menu()
    send_to_ntfy(content)
