import requests
from bs4 import BeautifulSoup
from datetime import datetime

def get_menu():
    url = "https://www.kopo.ac.kr/gangseo/content.do?menu=2625"
    try:
        res = requests.get(url, timeout=15)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 1. 오늘 날짜 준비 (형식: 2026-04-02)
        now = datetime.now()
        today_str = now.strftime("%Y-%m-%d")
        
        # 2. 캡처본에서 확인한 테이블 클래스 'tbl_table.menu' 사용
        table = soup.select_one('table.tbl_table.menu')
        if not table:
            return "⚠️ Table not found."

        rows = table.select('tbody tr')
        lunch_menu = ""

        for row in rows:
            # 첫 번째 칸(th 또는 td)에 날짜가 들어있음
            date_cell = row.select_one('th, td')
            if not date_cell: continue
            
            # 오늘 날짜가 포함된 행인지 확인
            if today_str in date_cell.get_text(strip=True):
                tds = row.select('td')
                # 캡처본 기준: 구분(th), 조식(td1), 중식(td2), 석식(td3)
                # 즉, 중식은 tds[1] 위치에 있습니다.
                if len(tds) >= 2:
                    lunch_menu = tds[1].get_text(separator="\n").strip()
                    break

        if not lunch_menu or "등록된" in lunch_menu:
            return f"🍱 [{today_str}] No lunch menu today."
        
        return f"🍱 [{today_str}] 오늘의 중식:\n{lunch_menu}"

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
                "Priority": "high",
                "Tags": "plate"
            }
        )
        print("Success")
    except:
        print("Failed")

if __name__ == "__main__":
    content = get_menu()
    send_to_ntfy(content)
