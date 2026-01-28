import os
import glob
from datetime import datetime, timedelta

def parse_line(line):
    """
    Parses a single line of the schedule text file.
    Format example: [2026.03.28 14:00] vs KT (홈) @잠실
    """
    line = line.strip()
    if not line or not line.startswith('['):
        return None
        
    try:
        # Split into [timestamp] and content
        header, rest = line.split('] ', 1)
        timestamp_str = header.replace('[', '')
        
        # Parse datetime
        game_dt = datetime.strptime(timestamp_str, '%Y.%m.%d %H:%M')
        
        # Parse content: "vs KT (홈) @잠실"
        # Assuming space separation: "vs", "KT", "(홈)", "@잠실"
        parts = rest.split(' ')
        
        if len(parts) >= 4:
            opponent = parts[1]
            game_type = parts[2] # (홈) or (원정)
            stadium = parts[3].lstrip('@')
        else:
            # Fallback if stadium might be missing or format differs slightly
            opponent = parts[1] if len(parts) > 1 else "?"
            game_type = parts[2] if len(parts) > 2 else ""
            stadium = ""

        return {
            'dt': game_dt,
            'opponent': opponent,
            'type': game_type,
            'stadium': stadium
        }
    except Exception as e:
        print(f"Skipping line (parse error): {line} | Error: {e}")
        return None

def generate_ics_content(team_name, events):
    """
    Generates ICS file content from a list of event dictionaries.
    """
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Song Yeongchan//KBO Schedule 2026//KR",
        "CALSCALE:GREGORIAN",
        f"X-WR-CALNAME:2026 {team_name} 경기일정",
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
        # End time is approximate (Start + 3.5 hours for baseball)
        dt_end = dt + timedelta(hours=3, minutes=30)
        
        start_str = dt.strftime('%Y%m%dT%H%M%S')
        end_str = dt_end.strftime('%Y%m%dT%H%M%S')
        
        # Summary Format: vs {Opponent} ({Type}) {Time}
        time_str = dt.strftime('%H:%M')
        summary = f"vs {event['opponent']} {event['type']} {time_str}"
        
        lines.append("BEGIN:VEVENT")
        lines.append(f"DTSTART;TZID=Asia/Seoul:{start_str}")
        lines.append(f"DTEND;TZID=Asia/Seoul:{end_str}")
        lines.append(f"SUMMARY:{summary}")
        lines.append(f"LOCATION:{event['stadium']}")
        lines.append(f"DESCRIPTION:{summary} @{event['stadium']}")
        lines.append(f"UID:{start_str}-{team_name}-{event['opponent']}@kbo2026")
        lines.append("END:VEVENT")
        
    lines.append("END:VCALENDAR")
    return "\n".join(lines)

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    txt_dir = os.path.join(base_dir, "kbo_schedules_2026_txt")
    ics_dir = os.path.join(base_dir, "kbo_schedules_2026_ics")
    
    # Ensure ICS directory exists
    if not os.path.exists(ics_dir):
        os.makedirs(ics_dir)
        
    # Search for TXT files in the TXT directory
    txt_files = glob.glob(os.path.join(txt_dir, "*_schedule_2026.txt"))
    
    if not txt_files:
        print(f"No text files found in {txt_dir}")
        return

    print(f"Found {len(txt_files)} schedule files in {txt_dir}")
    
    for txt_file in txt_files:
        filename = os.path.basename(txt_file)
        # Extract team name from filename (e.g., "LG_schedule_2026.txt" -> "LG")
        team_name = filename.split('_')[0]
        
        print(f"Processing {team_name}...")
        
        events = []
        with open(txt_file, 'r', encoding='utf-8') as f:
            for line in f:
                event = parse_line(line)
                if event:
                    events.append(event)
        
        if not events:
            print(f"  No events found for {team_name}.")
            continue
            
        ics_content = generate_ics_content(team_name, events)
        
        ics_filename = filename.replace('.txt', '.ics')
        # Save to the ICS directory
        ics_path = os.path.join(ics_dir, ics_filename)
        
        with open(ics_path, 'w', encoding='utf-8') as f:
            f.write(ics_content)
            
        print(f"  Created {ics_filename} with {len(events)} events.")

if __name__ == "__main__":
    main()
