import os
import glob
from datetime import datetime, timedelta

def get_city_from_stadium(stadium):
    stadium = stadium.replace('@', '').strip()
    mapping = {
        '잠실': '서울',
        '고척': '서울',
        '문학': '인천',
        '수원': '수원',
        '대전': '대전',
        '대구': '대구',
        '광주': '광주',
        '사직': '부산',
        '창원': '창원'
    }
    return mapping.get(stadium, stadium)

def parse_line(line, team_name):
    """
    Parses a single line.
    Format: [2026.03.28 14:00] vs KT (홈) @잠실
    Returns None if it's not a Home game (to avoid duplication).
    """
    line = line.strip()
    if not line or not line.startswith('['):
        return None
        
    try:
        # [2026.03.28 14:00] ...
        header, rest = line.split('] ', 1)
        timestamp_str = header.replace('[', '')
        game_dt = datetime.strptime(timestamp_str, '%Y.%m.%d %H:%M')
        
        # vs KT (홈) @잠실
        parts = rest.split(' ')
        if len(parts) < 3:
            return None
            
        opponent = parts[1]
        game_type = parts[2] # (홈) or (원정)
        stadium = parts[3] # @잠실
        
        # Only process HOME games to prevent duplicates in the ALL calendar
        if '(홈)' not in game_type:
            return None
            
        city = get_city_from_stadium(stadium)
        
        # Subject Team (team_name) is HOME
        # Opponent is AWAY
        
        return {
            'dt': game_dt,
            'home': team_name,
            'away': opponent,
            'stadium': stadium.replace('@', ''),
            'city': city
        }
    except Exception as e:
        # print(f"Skipping line: {line} ({e})")
        return None

def generate_ics_content(events):
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Song Yeongchan//KBO League 2026//KR",
        "CALSCALE:GREGORIAN",
        "X-WR-CALNAME:2026 KBO 전체 경기일정",
        "X-WR-TIMEZONE:Asia/Seoul",
        "BEGIN:VTIMEZONE",
        "TZID:Asia/Seoul",
        "X-LIC-LOCATION:Asia/Seoul",
        "BEGIN:STANDARD",
        "TZOFFSETFROM:+0900",
        "TZOFFSETTO:+0900",
        "TZNAME:KST",
        "DTSTART:19700101T000000",
        "END:STANDARD",
        "END:VTIMEZONE"
    ]
    
    for event in events:
        dt = event['dt']
        dt_end = dt + timedelta(hours=3, minutes=30)
        
        start_str = dt.strftime('%Y%m%dT%H%M%S')
        end_str = dt_end.strftime('%Y%m%dT%H%M%S')
        
        # Format: Away vs Home (City)
        # ex: KT vs LG (서울)
        summary = f"{event['away']} vs {event['home']} ({event['city']})"
        location = f"{event['stadium']}, {event['city']}"
        
        lines.append("BEGIN:VEVENT")
        lines.append(f"DTSTART;TZID=Asia/Seoul:{start_str}")
        lines.append(f"DTEND;TZID=Asia/Seoul:{end_str}")
        lines.append(f"SUMMARY:{summary}")
        lines.append(f"LOCATION:{location}")
        lines.append(f"DESCRIPTION:{summary} @{event['stadium']}")
        lines.append(f"UID:{start_str}-{event['away']}-{event['home']}@kbo2026")
        lines.append("END:VEVENT")
        
    lines.append("END:VCALENDAR")
    return "\n".join(lines)

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    txt_dir = os.path.join(base_dir, "kbo_schedules_2026_txt")
    ics_dir = os.path.join(base_dir, "kbo_schedules_2026_ics")
    
    if not os.path.exists(ics_dir):
        os.makedirs(ics_dir)
        
    txt_files = glob.glob(os.path.join(txt_dir, "*_schedule_2026.txt"))
    all_events = []
    
    print(f"Scanning {len(txt_files)} files for KBO All Schedule...")
    
    for txt_file in txt_files:
        filename = os.path.basename(txt_file)
        team_name = filename.split('_')[0]
        
        with open(txt_file, 'r', encoding='utf-8') as f:
            for line in f:
                event = parse_line(line, team_name)
                if event:
                    all_events.append(event)
    
    # Sort events by date
    all_events.sort(key=lambda x: x['dt'])
    
    print(f"Total Unique Games Found: {len(all_events)}")
    
    output_path = os.path.join(ics_dir, "KBO_League_2026.ics")
    content = generate_ics_content(all_events)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print(f"created {output_path}")

if __name__ == "__main__":
    main()
