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
        
        # 1. 오늘 요일 구하기 (월:0, 화:1, 수:2, 목:3, 금:4, 토:5, 일:6)
        weekday = datetime.now().weekday()
        
        # 2. 주말(토, 일)이면 실행 종료
        if weekday > 4:
            print("주말입니다. 식단을 보내지 않습니다.")
            return None

        # 3. 식단표 테이블 찾기
        table = soup.select_one('.tbl_table.menu') or soup.find('table')
        if not table:
            return "⚠️ 식단표 테이블을 찾을 수 없습니다."

        # 4. 데이터 행(tr)들 가져오기
        rows = table.select('tbody tr')
        
        # 월요일이 rows[0]부터 시작한다고 가정할 때 오늘 요일에 맞는 행 선택
        if len(rows) > weekday:
            target_row = rows[weekday]
            cells = target_row.find_all(['td', 'th'])
            
            # 표 구조 분석 (보여주신 사진 기준):
            # [0] 날짜/요일 | [1] 조식 | [2] 중식 | [3] 석식
            # 따라서 '중식'은 인덱스 2번입니다.
            if len(cells) >= 3:
                lunch_menu = cells[2].get_text(separator="\n").strip()
                
                # 내용이 비어있거나 "등록된 식단이 없습니다"인 경우 처리
                if len(lunch_menu) < 3 or "등록된" in lunch_menu:
                    lunch_menu = "오늘 등록된 식단이 없습니다."
            else:
                lunch_menu = "표 구조가 예상과 다릅니다. (열 부족)"
        else:
            lunch_menu = "표의 행 개수가 요일 정보보다 적습니다."

        weekdays_ko = ["월요일", "화요일", "수요일", "목요일", "금요일"]
        return f"🍱 [{weekdays_ko[weekday]}] 오늘의 중식 메뉴:\n{lunch_menu}"

    except Exception as e:
        return f"⚠️ 오류 발생: {str(e)[:30]}"

def send_to_ntfy(message):
    # 메시지가 없으면(주말 등) 전송하지 않음
    if not message:
        return
        
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
        print("전송 성공!")
    except:
        print("전송 실패")

if __name__ == "__main__":
    content = get_menu()
    send_to_ntfy(content)
