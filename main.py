import requests
from bs4 import BeautifulSoup
from datetime import datetime

def get_menu():
    # 강서폴리텍 식단 페이지 (실제 학교 주소로 확인 필요)
    url = "https://www.kopo.ac.kr/gangseo/content.do?menu=2625"
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 오늘 날짜 (예: 2026-04-02)
        today = datetime.now().strftime("%Y-%m-%d")
        
        # 실제 식단표 테이블에서 오늘 날짜 찾기 (기본 로직)
        menu_items = soup.select('table.board-list td')
        
        # 테스트를 위해 일단 "식단 확인 시도 중"이라는 기본 메시지 설정
        menu_text = "오늘의 메뉴를 확인하고 있습니다."
        
        for item in menu_items:
            if today in item.text:
                menu_text = item.find_next_sibling('td').text.strip()
                break
        
        return f"🍱 [{today}] 식단 안내\n{menu_text}"
    except:
        return "🍱 식단 페이지 접속에 실패했지만 알람 테스트 중입니다!"

def send_to_ntfy(message):
    # 아까 성공했던 그 주소
    url = "https://ntfy.sh/Polytech_Lunch"
    
    try:
        # 헤더와 데이터를 가장 확실한 방식으로 전송
        res = requests.post(
            url,
            data=message.encode('utf-8'),
            headers={
                "Title": "점심 알리미",
                "Priority": "high",
                "Tags": "loudspeaker,fork_knife"
            }
        )
        print(f"결과: {res.status_code}, 내용: {res.text}")
    except Exception as e:
        print(f"오류: {e}")

if __name__ == "__main__":
    content = get_menu()
    send_to_ntfy(content)
