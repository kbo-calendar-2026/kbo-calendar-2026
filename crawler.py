import requests
from bs4 import BeautifulSoup
import os
import re

# 1. 데이터를 저장할 딕셔너리 초기화 (모든 구단)
teams = ["삼성", "KIA", "LG", "두산", "KT", "SSG", "롯데", "한화", "NC", "키움"]
schedule_data = {team: [] for team in teams}

def clean_html(raw_html):
    if not raw_html:
        return ""
    return BeautifulSoup(raw_html, "html.parser").get_text().strip()

def scrap_kbo_schedule(year):
    api_url = "https://www.koreabaseball.com/ws/Schedule.asmx/GetScheduleList"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
    
    # 2. 월별 순회
    # 정규 시즌이 주로 열리는 3월부터 10월까지 순회
    for month in range(3, 11): 
        month_str = f"{month:02d}"
        
        # API Payload
        payload = {
            'leId': '1',
            'srIdList': '0,9', # 0: 정규시즌, 9: 시범경기 등
            'seasonId': str(year),
            'gameMonth': month_str,
            'teamId': ''
        }
        
        print(f"{year}년 {month_str}월 데이터를 수집 중입니다...")
        
        try:
            response = requests.post(api_url, data=payload, headers=headers)
            
            if response.status_code != 200:
                print(f"API 요청 실패: {response.status_code}")
                continue
                
            try:
                data = response.json()
            except ValueError:
                print("JSON 파싱 실패")
                continue
                
            rows = data.get('rows', [])
            current_date_str = ""
            
            for row_data in rows:
                cols = row_data.get('row', [])
                if not cols:
                    continue
                
                # Check for row class or text to identify if date is present
                # JSON row items: dict with 'Text', 'Class', 'RowSpan' etc.
                
                # Logic to determine if first column is Date or Time
                # Typically if len(cols) == 9, it's a full row with Date. 
                # If len(cols) == 8, it inherits Date.
                
                has_date = False
                if len(cols) >= 9 and cols[0].get('Class') == 'day':
                    has_date = True
                
                if has_date:
                    date_html = cols[0]['Text']
                    # Clean date: "03.28(토)" -> "03.28"
                    date_text = clean_html(date_html)
                    # Extract roughly "MM.DD"
                    match = re.search(r'(\d{2}\.\d{2})', date_text)
                    if match:
                        current_date_str = match.group(1)
                    
                    time_idx = 1
                    play_idx = 2
                    stadium_idx = 7
                else:
                    # Inherit date
                    time_idx = 0
                    play_idx = 1
                    stadium_idx = 6
                
                # Validation of index range
                if len(cols) <= stadium_idx:
                    continue
                    
                time_html = cols[time_idx]['Text']
                play_html = cols[play_idx]['Text']
                stadium_html = cols[stadium_idx]['Text']
                
                time_text = clean_html(time_html)
                stadium_text = clean_html(stadium_html)
                
                # Check for "vs" structure in play_html
                # <span>KT</span><em><span>vs</span></em><span>LG</span>
                play_soup = BeautifulSoup(play_html, 'html.parser')
                spans = play_soup.find_all('span')
                
                if len(spans) >= 2:
                    # Usually span[0] is Away, span[1] is Home?
                    # In HTML: KT vs LG -> Text shows KT vs LG.
                    # spans[0].text is KT, spans[1].text is LG
                    away_team = spans[0].get_text(strip=True)
                    # The second span might be inside 'em' sometimes or after 'vs', but usually structure is span-em-span
                    # Let's blindly grab first 2 non-empty spans or just text split by 'vs'
                    
                    # Safer: get all text, split by vs
                    full_play_text = play_soup.get_text(strip=True)
                    if 'vs' in full_play_text:
                        parts = full_play_text.split('vs')
                        if len(parts) == 2:
                            away_team = parts[0].strip()
                            home_team = parts[1].strip()
                        else:
                             # Fallback to spans if 'vs' split fails or complex
                             if len(spans) >= 2:
                                away_team = spans[0].get_text(strip=True)
                                home_team = spans[-1].get_text(strip=True)
                    else:
                        continue # No vs found
                else:
                    # Maybe just text "취소" or something
                    continue

                full_date = f"{year}.{current_date_str}"
                
                # 3. 양쪽 구단 리스트에 모두 추가
                # (Away 팀 입장)
                if away_team in schedule_data:
                    schedule_data[away_team].append(
                        f"[{full_date} {time_text}] vs {home_team} (원정) @{stadium_text}"
                    )
                
                # (Home 팀 입장)
                if home_team in schedule_data:
                    schedule_data[home_team].append(
                        f"[{full_date} {time_text}] vs {away_team} (홈) @{stadium_text}"
                    )
                    
        except Exception as e:
            print(f"{month}월 데이터 수집 중 오류 발생: {e}")

# 실행 (2026년 기준)
scrap_kbo_schedule(2026)

# 4. 결과 파일 저장 (txt)
output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kbo_schedules_2026_txt")
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

print("\n--- 파일 생성 시작 ---")
for team, games in schedule_data.items():
    filename = f"{output_dir}/{team}_schedule_2026.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"=== 2026년 {team} 경기 일정 ===\n\n")
        if not games:
            f.write("예정된 경기 일정이 없습니다.\n")
        else:
            for game in games:
                f.write(game + "\n")
    print(f"[{team}] 파일 생성 완료: {filename}")

print("\n모든 작업이 완료되었습니다.")