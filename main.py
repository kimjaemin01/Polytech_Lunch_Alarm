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
    print(f"오늘 날짜: {today_str}")

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

    for row in rows[1:]:  # tr[0]은 헤더(구분/조식/중식/석식)
        cells = row.find_all(["th", "td"])
        if not cells:
            continue

        # get_text()로 읽으면 "2026-04-02\n목요일" → 줄바꿈 기준으로 split해서 첫줄만 사용
        date_raw = cells[0].get_text()          # strip 안 함
        date_only = date_raw.split("\n")[0].strip()  # 첫 줄 = "2026-04-02"
        print(f"  읽은 날짜: {repr(date_only)}")

        if date_only == today_str:
            if len(cells) >= 3:
                lunch = cells[2].get_text("\n", strip=True).strip()
                if not lunch or "등록" in lunch:
                    return f"🍱 [{day_label}요일 중식]\n오늘 등록된 식단이 없습니다."
                return f"🍱 [{day_label}요일 중식]\n{lunch}"

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
    print(f"\n최종 메시지:\n{content}")
    if content is None:
        sys.exit(0)
    send_to_ntfy(content)
