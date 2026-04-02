import requests
from bs4 import BeautifulSoup
from datetime import datetime
import sys

NTFY_URL = "https://ntfy.sh/Polytech_Lunch"
MEAL_URL = "https://www.kopo.ac.kr/kangseo/content.do?menu=262"

HEADERS = {
    "User-Agent":      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept":          "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ko-KR,ko;q=0.9",
    "Referer":         "https://www.kopo.ac.kr/kangseo/index.do",
}

def get_menu():
    weekday = datetime.now().weekday()  # 월=0 ~ 금=4
    if weekday > 4:
        print("주말 — 전송 건너뜀")
        return None

    days = ["월", "화", "수", "목", "금"]
    day_label = days[weekday]
    today_str = datetime.now().strftime("%Y-%m-%d")  # 예) 2026-04-02

    try:
        r = requests.get(MEAL_URL, headers=HEADERS, timeout=20)
        r.encoding = "utf-8"
        if r.status_code != 200:
            return f"⚠️ 접속 실패 (HTTP {r.status_code})"
    except requests.RequestException as e:
        return f"⚠️ 네트워크 오류: {e}"

    soup = BeautifulSoup(r.text, "html.parser")
    table = soup.find("table")
    if not table:
        return "⚠️ 테이블을 찾을 수 없습니다."

    rows = table.find_all("tr")

    # tr[0] = 헤더(구분/조식/중식/석식), tr[1~] = 날짜별 데이터
    # 각 행의 첫 번째 셀: "2026-04-02\n목요일" 형태
    # 중식은 인덱스 2번 열
    for row in rows[1:]:  # 헤더 행 건너뜀
        cells = row.find_all(["th", "td"])
        if not cells:
            continue

        date_cell = cells[0].get_text(strip=True)  # "2026-04-02목요일" (strip하면 \n 제거됨)

        # 날짜 앞 10자리만 비교 (YYYY-MM-DD)
        if date_cell[:10] == today_str:
            if len(cells) >= 3:
                lunch = cells[2].get_text("\n", strip=True)
                lunch = lunch.strip()
                if not lunch or "등록" in lunch:
                    return f"🍱 [{day_label}요일 중식]\n오늘 등록된 식단이 없습니다."
                return f"🍱 [{day_label}요일 중식]\n{lunch}"
            else:
                return f"⚠️ 중식 열을 찾을 수 없습니다. (셀 수: {len(cells)})"

    return f"⚠️ 오늘 날짜({today_str}) 행을 찾지 못했습니다."


def send_to_ntfy(message):
    try:
        resp = requests.post(
            NTFY_URL,
            data=message.encode("utf-8"),
            headers={
                "Title":    "폴리텍 강서 점심 식단 🍽".encode("utf-8"),
                "Priority": "default",
                "Tags":     "fork_and_knife",
            },
            timeout=10,
        )
        resp.raise_for_status()
        print(f"✅ 전송 완료 (HTTP {resp.status_code})")
    except requests.RequestException as e:
        print(f"❌ ntfy 전송 실패: {e}")
        sys.exit(1)


if __name__ == "__main__":
    content = get_menu()
    print(content)
    if content is None:
        sys.exit(0)
    send_to_ntfy(content)
