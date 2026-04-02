import requests
from bs4 import BeautifulSoup
from datetime import datetime

def get_menu():
    # 강서폴리텍 식단표 주소
    url = "https://www.kopo.ac.kr/kangseo/content.do?menu=262"
    
    try:
        res = requests.get(url)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')

        # 오늘 날짜
        today_date = datetime.now().strftime("%Y-%m-%d")
        
        # 식단표 테이블 찾기
        table = soup.select_one('.t_type01')
        if not table:
            return "❌ 식단표 테이블을 찾을 수 없습니다."

        rows = table.find_all('tr')
        today_menu = ""
        
        # 각 행을 돌며 오늘 날짜 확인
        for row in rows:
            cells = row.find_all(['th', 'td'])
            if len(cells) >= 3:
                date_area = cells[0].get_text(strip=True)
                
                # 행의 첫 번째 칸에 오늘 날짜가 포함되어 있다면
                if today_date in date_area:
                    # 세 번째 칸(중식)의 텍스트를 가져옴
                    today_menu = cells[2].get_text(separator="\n").strip()
                    break
        
        if not today_menu:
            return f"🍱 {today_date} 식단이 아직 등록되지 않았습니다."

        return f"🍴 오늘의 강서폴리텍 식단\n📅 날짜: {today_date}\n\n{today_menu}"

    except Exception as e:
        return f"❌ 오류 발생: {str(e)}"

def send_to_ntfy(message):
    # 주소창에 입력해서 성공했던 그 주소 그대로 사용합니다.
    url = "https://ntfy.sh/Polytech_Lunch"
    
    try:
        # 가장 단순한 방식으로 한글 데이터를 보냅니다.
        response = requests.post(
            url,
            data=message.encode('utf-8'),
            headers={
                "Title": "🍱 오늘 점심 메뉴",
                "Priority": "4", # 높은 우선순위
                "Tags": "plate"
            }
        )
        
        if response.status_code == 200:
            print("✅ 파이썬에서도 전송 성공!")
        else:
            print(f"❌ 전송 실패 (에러코드: {response.status_code})")
            
    except Exception as e:
        print(f"❌ 파이썬 오류: {e}")

if __name__ == "__main__":
    result_menu = get_menu()
    send_to_ntfy(result_menu)
