import requests
from bs4 import BeautifulSoup
from datetime import datetime

def get_menu():
    url = "https://www.kopo.ac.kr/gangseo/content.do?menu=2625"
    try:
        # 1. 페이지 데이터 가져오기
        res = requests.get(url, timeout=15)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 2. 오늘 날짜 준비 (다양한 형식 대응)
        now = datetime.now()
        date_formats = [
            now.strftime("%Y-%m-%d"), # 2026-04-02
            now.strftime("%m.%d"),    # 04.02
            f"{now.month}/{now.day}"  # 4/2
        ]
        
        # 3. 식단표 테이블의 모든 행(tr) 추출
        rows = soup.select('table.board-list tbody tr')
        menu_content = ""

        for row in rows:
            cells = row.find_all('td')
            if not cells: continue
            
            # 첫 번째 또는 두 번째 칸에 날짜가 있는지 확인
            row_text = cells[0].get_text(strip=True) + cells[1].get_text(strip=True)
            
            if any(fmt in row_text for fmt in date_formats):
                # 식단은 보통 3번째 칸(index 2)에 있습니다.
                # get_text(separator="\n")를 써야 반찬 사이 줄바꿈이 유지됩니다.
                menu_content = cells[2].get_text(separator="\n").strip()
                break

        if not menu_content or "등록된 식단이" in menu_content:
            return "🍱 No menu uploaded on the website yet."
        
        return f"🍱 [{now.strftime('%Y-%m-%d')}] Menu:\n{menu_content}"

    except Exception as e:
        return f"⚠️ Error: {str(e)[:30]}"

def send_to_ntfy(message):
    url = "https://ntfy.sh/Polytech_Lunch"
    try:
        requests.post(
            url,
            data=message.encode('utf-8'),
            headers={
                "Title": "Lunch Menu Update",
                "Priority": "high",
                "Tags": "plate,fork_and_knife"
            }
        )
        print("Success")
    except:
        print("Failed")

if __name__ == "__main__":
    content = get_menu()
    send_to_ntfy(content)
