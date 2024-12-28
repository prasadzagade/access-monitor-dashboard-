import re
from datetime import datetime, timedelta
import os
from collections import defaultdict

LOG_PATH = '/usr/local/apache/domlogs/aditya.printsflick.com.log'

def parse_logs():
    logs = []
    ip_last_request = defaultdict(lambda: {'date': None, 'path': None})
    
    print(f"Attempting to open log file: {LOG_PATH}")
    
    try:
        with open(LOG_PATH, 'r') as f:
            for line in f:
                match = re.match(r'(\S+) - - \[(.*?)\] "(\S+) (.*?) (\S+)" (\d+) (\d+) "(.*?)" "(.*?)"', line)
                if match:
                    ip, date_str, method, path, protocol, status, size, referer, user_agent = match.groups()
                    date = datetime.strptime(date_str, '%d/%b/%Y:%H:%M:%S %z')
                    
                    # Calculate duration
                    duration = None
                    if ip_last_request[ip]['date']:
                        duration = (date - ip_last_request[ip]['date']).total_seconds()
                        logs.append({
                            'ip': ip,
                            'date': ip_last_request[ip]['date'],
                            'method': method,
                            'path': ip_last_request[ip]['path'],
                            'protocol': protocol,
                            'status': status,
                            'size': size,
                            'referer': referer,
                            'user_agent': user_agent,
                            'duration': duration
                        })
                    
                    ip_last_request[ip] = {'date': date, 'path': path}
                    
        print(f"Successfully parsed {len(logs)} log entries")
    except Exception as e:
        print(f"Error parsing log file: {str(e)}")
    
    # Sort logs by date, most recent first
    logs.sort(key=lambda x: x['date'], reverse=True)
    return logs
