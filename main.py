import requests
from bs4 import BeautifulSoup
from datetime import datetime

def get_menu():
    url = "https://www.kopo.ac.kr/gangseo/content.do?menu=2625"
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=15)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 1. 오늘 요일 인덱스 (월:0, 화:1, 수:2, 목:3, 금:4)
        weekday = datetime.now().weekday()
        
        # 주말 제외
        if weekday > 4:
            return None

        # 2. 캡처본에서 본 'tbl_table menu' 테이블 찾기
        table = soup.select_one('table.tbl_table.menu')
        if not table:
            return "⚠️ Table not found."

        # 3. tbody 안의 행(tr)들 가져오기
        rows = table.select('tbody > tr')
        
        # 요일 인덱스에 맞춰 행 선택 (월요일=rows[0], 화요일=rows[1]...)
        if len(rows) > weekday:
            target_row = rows[weekday]
            tds = target_row.find_all('td')
            
            # 캡처본 구조: [0]날짜/요일 | [1]조식 | [2]중식 | [3]석식
            # 중식은 3번째 칸인 tds[2]에 들어있습니다.
            if len(tds) >= 3:
                # span 태그 안의 텍스트를 가져오고 줄바꿈 정리
                lunch_menu = tds[2].get_text(separator="\n").strip()
                
                if not lunch_menu or "등록된" in lunch_menu:
                    lunch_menu = "오늘 등록된 식단이 없습니다."
            else:
                lunch_menu = "중식 칸을 찾을 수 없습니다."
        else:
            lunch_menu = "해당 요일의 행을 찾을 수 없습니다."

        days = ["월요일", "화요일", "수요일", "목요일", "금요일"]
        return f"🍱 [{days[weekday]}] 중식 메뉴:\n{lunch_menu}"

    except Exception as e:
        return f"⚠️ 에러 발생: {str(e)[:30]}"

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
