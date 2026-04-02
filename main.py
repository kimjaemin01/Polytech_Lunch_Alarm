import requests
import re
from datetime import datetime

def get_menu():
    url = "https://www.kopo.ac.kr/gangseo/content.do?menu=2625"
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        res = requests.get(url, headers=headers, timeout=15)
        res.encoding = 'utf-8'
        html = res.text

        # 오늘 요일 인덱스 (월:0, 화:1, 수:2, 목:3, 금:4)
        weekday = datetime.now().weekday()
        if weekday > 4: return None

        # 1. HTML 태그 싹 제거하고 순수 텍스트만 남기기
        clean_text = re.sub('<[^<]+?>', '\n', html) 
        lines = [line.strip() for line in clean_text.split('\n') if line.strip()]
        
        # 2. '중식'이라는 글자가 들어간 행들만 다 모으기
        # 학교 소스 특성상 식단은 보통 특정 패턴 뒤에 몰려있습니다.
        menu_items = []
        for i, line in enumerate(lines):
            if "백미밥" in line or "김치" in line or "국" in line:
                menu_items.append(line)
        
        # 3. 오늘 요일에 해당하는 식단 뭉치 가져오기 (월요일=첫번째 뭉치...)
        # 식단이 뭉쳐있으므로, 중복 제거 후 요일별로 나눕니다.
        unique_menus = []
        for m in menu_items:
            if m not in unique_menus:
                unique_menus.append(m)
        
        if len(unique_menus) > weekday:
            today_menu = unique_menus[weekday]
        else:
            today_menu = "식단 데이터를 찾았으나 요일 매칭에 실패했습니다."

        days = ["월요일", "화요일", "수요일", "목요일", "금요일"]
        return f"🍱 [{days[weekday]}] 중식:\n{today_menu}"

    except Exception as e:
        return f"⚠️ 접속 실패: {str(e)[:30]}"

def send_to_ntfy(message):
    if not message: return
    url = "https://ntfy.sh/Polytech_Lunch"
    requests.post(url, data=message.encode('utf-8'), headers={"Title": "Lunch Menu"})

if __name__ == "__main__":
    content = get_menu()
    send_to_ntfy(content)
    
