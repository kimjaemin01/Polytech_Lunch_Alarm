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
    weekday = datetime.now().weekday()
    if weekday > 4:
        print("🔕 주말 — 전송 건너뜀")
        return None

    days = ["월", "화", "수", "목", "금"]
    day_label = days[weekday]
    now = datetime.now()
    print(f"📅 오늘: {now.strftime('%Y-%m-%d')} ({day_label}요일, weekday={weekday})")

    session = requests.Session()

    # ── 방법 1: Ajax API 후보들 시도 ──────────────────────────────
    ajax_targets = [
        (
            "https://www.kopo.ac.kr/kangseo/prog/food/kangseo/sub02/list.do",
            {"searchYear": now.strftime("%Y"), "searchMonth": now.strftime("%m")},
        ),
        (
            "https://www.kopo.ac.kr/kangseo/ajax/foodMenuList.do",
            {"year": now.strftime("%Y"), "month": now.strftime("%m"), "menu": "262"},
        ),
        (
            "https://www.kopo.ac.kr/prog/food/kangseo/sub02/list.do",
            {"searchYear": now.strftime("%Y"), "searchMonth": now.strftime("%m")},
        ),
    ]

    for api_url, params in ajax_targets:
        print(f"\n🔍 Ajax 시도: {api_url}")
        try:
            r = session.get(api_url, headers=HEADERS, params=params, timeout=12)
            print(f"   상태코드: {r.status_code} / 응답길이: {len(r.text)}자")
            if r.status_code == 200 and len(r.text.strip()) > 100:
                print(f"   응답 앞 300자: {r.text[:300]}")
                result = _parse_html(r.text, weekday, day_label, now)
                if result:
                    print(f"✅ Ajax 파싱 성공!")
                    return result
                else:
                    print(f"   ❌ 파싱 실패 (td 없거나 식단 못 찾음)")
        except requests.RequestException as e:
            print(f"   ❌ 요청 실패: {e}")

    # ── 방법 2: 메인 페이지 직접 파싱 ────────────────────────────
    print(f"\n🔍 메인 페이지 직접 요청: {MEAL_URL}")
    try:
        r = session.get(MEAL_URL, headers=HEADERS, timeout=20)
        r.encoding = "utf-8"
        print(f"   상태코드: {r.status_code} / 응답길이: {len(r.text)}자")

        if r.status_code != 200:
            return f"⚠️ 접속 실패 (HTTP {r.status_code})"

        soup = BeautifulSoup(r.text, "html.parser")
        all_tds  = soup.find_all("td")
        all_tabs = soup.find_all("table")
        print(f"   table 개수: {len(all_tabs)} / td 개수: {len(all_tds)}")

        # 테이블 구조 출력 (디버깅용)
        for ti, table in enumerate(all_tabs):
            rows = table.find_all("tr")
            print(f"\n   [table {ti}] tr={len(rows)}행")
            for ri, row in enumerate(rows[:5]):  # 앞 5행만
                cells = row.find_all(["th", "td"])
                texts = [c.get_text(strip=True)[:20] for c in cells]
                print(f"      tr[{ri}]: {texts}")

        result = _parse_html(r.text, weekday, day_label, now)
        if result:
            print(f"✅ 메인 페이지 파싱 성공!")
            return result

        td_count = len(all_tds)
        return (
            f"⚠️ 식단 파싱 실패 (td {td_count}개)\n"
            f"→ JS 동적 렌더링 문제일 가능성 높음\n"
            f"직접 확인: {MEAL_URL}"
        )

    except requests.RequestException as e:
        return f"⚠️ 네트워크 오류: {e}"


def _parse_html(html, weekday, day_label, now):
    soup = BeautifulSoup(html, "html.parser")

    today_patterns = [
        now.strftime("%Y-%m-%d"),
        now.strftime("%m/%d"),
        now.strftime("%-m/%-d"),
        now.strftime("%m월%d일"),
        now.strftime("%-m월%-d일"),
    ]
    day_names = ["월", "화", "수", "목", "금"]

    # 전략 A: 날짜로 열 찾기
    for table in soup.find_all("table"):
        rows = table.find_all("tr")
        col_idx = -1

        for row in rows:
            cells = row.find_all(["th", "td"])
            for i, cell in enumerate(cells):
                text = cell.get_text(strip=True).replace(" ", "")
                if any(p.replace(" ", "") in text for p in today_patterns):
                    col_idx = i
                    break
            if col_idx >= 0:
                break

        if col_idx < 0:
            continue

        for row in rows:
            cells = row.find_all(["th", "td"])
            row_header = cells[0].get_text(strip=True) if cells else ""
            if "중식" in row_header or "점심" in row_header:
                if col_idx < len(cells):
                    menu = cells[col_idx].get_text("\n", strip=True)
                    if menu:
                        return _format(day_label, menu)

        # 인덱스 방식 폴백
        all_tds = table.find_all("td")
        target_idx = (weekday * 4) + 2
        if len(all_tds) > target_idx:
            menu = all_tds[target_idx].get_text("\n", strip=True)
            if menu and "등록된" not in menu:
                return _format(day_label, menu)

    # 전략 B: 요일 헤더로 열 찾기
    for table in soup.find_all("table"):
        rows = table.find_all("tr")
        col_idx = -1
        for row in rows:
            cells = row.find_all(["th", "td"])
            for i, cell in enumerate(cells):
                if cell.get_text(strip=True) == day_names[weekday]:
                    col_idx = i
                    break
            if col_idx >= 0:
                break

        if col_idx < 0:
            continue

        for row in rows:
            cells = row.find_all(["th", "td"])
            row_header = cells[0].get_text(strip=True) if cells else ""
            if "중식" in row_header or "점심" in row_header:
                if col_idx < len(cells):
                    menu = cells[col_idx].get_text("\n", strip=True)
                    if menu:
                        return _format(day_label, menu)

    return None


def _format(day_label, raw):
    clean = raw.replace("중식", "").replace("점심", "").strip()
    if not clean or "등록" in clean:
        return f"🍱 [{day_label}요일 중식]\n오늘 등록된 식단이 없습니다."
    return f"🍱 [{day_label}요일 중식]\n{clean}"


def send_to_ntfy(message):
    print(f"\n📤 ntfy 전송 중...")
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
    print("=" * 50)
    content = get_menu()
    print("\n" + "=" * 50)
    print("📋 최종 메시지:")
    print(content)
    print("=" * 50)

    if content is None:
        sys.exit(0)

    send_to_ntfy(content)
