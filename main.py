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
    weekday = datetime.now().weekday()  # 월=0, 화=1, 수=2, 목=3, 금=4
    if weekday > 4:
        print("주말 — 전송 건너뜀")
        return None

    days = ["월", "화", "수", "목", "금"]
    day_label = days[weekday]

    # 테이블 구조:
    # tr[0] = 헤더 (구분 / 조식 / 중식 / 석식)
    # tr[1] = 월요일
    # tr[2] = 화요일
    # tr[3] = 수요일
    # tr[4] = 목요일
    # tr[5] = 금요일
    # tr[6] = 토요일
    # tr[7] = 일요일
    target_row = weekday + 1  # 월=1, 화=2, 수=3, 목=4, 금=5

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
    print(f"전체 tr 개수: {len(rows)}, 오늘({day_label}요일) → tr[{target_row}] 사용")

    if len(rows) <= target_row:
        return f"⚠️ 행 부족 (전체 {len(rows)}행, 필요 {target_row+1}행)"

    cells = rows[target_row].find_all(["th", "td"])
    print(f"tr[{target_row}] 셀 개수: {len(cells)}")

    if len(cells) < 3:
        return f"⚠️ 셀 부족 (전체 {len(cells)}개)"

    lunch = cells[2].get_text("\n", strip=True).strip()
    print(f"중식 raw: {repr(lunch[:100])}")

    if not lunch or "등록" in lunch:
        return f"🍱 [{day_label}요일 중식]\n오늘 등록된 식단이 없습니다."

    # 콤마 제거 후 줄바꿈으로 분리, 빈 줄 제거
    items = [line.strip().strip(",").strip() for line in lunch.split("\n")]
    items = [item for item in items if item]
    clean_lunch = "\n".join(items)

    return f"🍱 [{day_label}요일 중식]\n{clean_lunch}"


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
