import requests
from bs4 import BeautifulSoup
from datetime import datetime

def get_menu():
    # 1. 학교 식단표 주소
    url = "https://www.kopo.ac.kr/gangseo/content.do?menu=2625"
    
    try:
        # 브라우저인 척 속이기 위한 헤더
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
        }
        res = requests.get(url, headers=headers, timeout=15)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 2. 오늘 요일 구하기 (월:0, 화:1, 수:2, 목:3, 금:4, 토:5, 일:6)
        now = datetime.now()
        weekday = now.weekday()
        
        # 주말(토, 일)이면 실행하지 않음
        if weekday > 4:
            print("주말입니다. 프로그램을 종료합니다.")
            return None

        # 3. 식단표 테이블의 모든 행(tr) 가져오기
        # 캡처본 기준 'tbl_table menu' 클래스 사용
        rows = soup.select('table.tbl_table.menu tbody tr')
        
        # 만약 tbody가 명확하지 않을 경우를 대비한 보조 로직
        if not rows:
            all_tr = soup.find_all('tr')
            # 첫 번째 줄(제목행)을 제외한 나머지 행들
            rows = [tr for tr in all_tr if tr.find('td')]

        # 4. 요일 번호에 맞는 행 선택 (월=0번째 줄, 화=1번째 줄...)
        if len(rows) > weekday:
            target_row = rows[weekday]
            cells = target_row.find_all('td')
            
            # 표 구조: [0]날짜/요일 | [1]조식 | [2]중식 | [3]석식
            # 중식은 3번째 칸(index 2)입니다.
            if len(cells) >= 3:
                # 내부의 span 태그나 텍스트를 줄바꿈 포함해서 추출
                lunch_menu = cells[2].get_text(separator="\n").strip()
                
                if not lunch_menu or "등록된" in lunch_menu:
                    lunch_menu = "오늘 등록된 식단이 없습니다."
            else:
                lunch_menu = "표의 칸(Column) 개수가 부족합니다."
        else:
            lunch_menu = f"표의 행(Row) 개수가 부족합니다. (현재 {len(rows)}행 발견)"

        weekdays_ko = ["월요일", "화요일", "수요일", "목요일", "금요일"]
        return f"🍱 [{weekdays_ko[weekday]}] 오늘의 중식:\n{lunch_menu}"

    except Exception as e:
        return f"⚠️ 오류 발생: {str(e)[:30]}"

def send_to_ntfy(message):
    if not message:
        return
        
    # ntfy 주소 (본인이 설정한 토픽명)
    url = "https://ntfy.sh/Polytech_Lunch"
    
    try:
        requests.post(
            url,
            data=message.encode('utf-8'),
            headers={
                "Title": "Lunch Menu Alarm",
                "Priority": "high",
                "Tags": "plate,fork_and_knife"
            }
        )
        print("알림 전송 성공!")
    except Exception as e:
        print(f"알림 전송 실패: {e}")

if __name__ == "__main__":
    content = get_menu()
    send_to_ntfy(content)
