import requests
from bs4 import BeautifulSoup
from datetime import datetime

def get_menu():
    # 강서폴리텍 식단 페이지
    url = "https://www.kopo.ac.kr/gangseo/content.do?menu=2625"
    try:
        response = requests.get(url)
        # 웹페이지 인코딩 설정 (한글 깨짐 방지)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 오늘 날짜 (YYYY-MM-DD)
        today = datetime.now().strftime("%Y-%m-%d")
        
        # 기본 메시지 (영어/이모지 위주)
        menu_text = "No menu data found yet."
        
        # 식단표에서 오늘 날짜 데이터 찾기
        menu_items = soup.select('table.board-list td')
        for item in menu_items:
            if today in item.text:
                # 다음 칸(td)에 있는 식단 텍스트 가져오기
                menu_text = item.find_next_sibling('td').text.strip()
                break
        
        return f"🍱 [{today}] Menu:\n{menu_text}"
    except Exception as e:
        return f"🍱 Error fetching menu: {str(e)[:20]}"

def send_to_ntfy(message):
    # ntfy 주소
    url = "https://ntfy.sh/Polytech_Lunch"
    
    try:
        # 헤더에서 한글을 모두 제거했습니다.
        res = requests.post(
            url,
            data=message.encode('utf-8'),
            headers={
                "Title": "Lunch Alarm",
                "Priority": "high",
                "Tags": "plate,fork_and_knife"
            }
        )
        print(f"Result: {res.status_code}, Text: {res.text}")
    except Exception as e:
        print(f"Network Error: {e}")

if __name__ == "__main__":
    content = get_menu()
    send_to_ntfy(content)
