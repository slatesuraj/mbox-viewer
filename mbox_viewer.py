import os
import json
import mailbox
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from datetime import datetime
import email.utils

class MboxHandler(BaseHTTPRequestHandler):
    def __init__(self, mbox_path, *args, **kwargs):
        self.mbox = mailbox.mbox(mbox_path)
        super().__init__(*args, **kwargs)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        if path == '/emails':
            self.handle_emails(query)
        elif path == '/email':
            self.handle_single_email(query)
        elif path == '/':
            self.serve_file('index.html')
        elif path.endswith(('.js', '.css')):
            self.serve_file(path[1:])
        else:
            self.send_response(404)
            self.end_headers()

    def serve_file(self, filename):
        try:
            with open(filename, 'rb') as f:
                content = f.read()
            
            content_type = 'text/html'
            if filename.endswith('.js'):
                content_type = 'application/javascript'
            elif filename.endswith('.css'):
                content_type = 'text/css'

            self.send_response(200)
            self.send_header('Content-type', content_type)
            self.end_headers()
            self.wfile.write(content)
        except FileNotFoundError:
            self.send_response(404)
            self.end_headers()

    def handle_single_email(self, query):
        try:
            email_id = int(query.get('id', [0])[0])
            email_data = None
            current_id = 0

            for message in self.mbox:
                try:
                    if current_id == email_id:
                        date_str = message.get('date')
                        date_tuple = email.utils.parsedate_tz(date_str) if date_str else None
                        date = datetime.fromtimestamp(email.utils.mktime_tz(date_tuple)) if date_tuple else None

                        payload = message.get_payload()
                        if isinstance(payload, list):
                            payload = '\n'.join([p.as_string() if hasattr(p, 'as_string') else str(p) for p in payload])
                        elif hasattr(payload, 'as_string'):
                            payload = payload.as_string()

                        email_data = {
                            'id': current_id,
                            'subject': message.get('subject', '(No subject)'),
                            'from': message.get('from', ''),
                            'date': date.strftime('%Y-%m-%d %H:%M:%S') if date else '',
                            'body': payload
                        }
                        break
                    current_id += 1
                except Exception as e:
                    print(f"Error processing message: {e}")
                    continue

            if email_data:
                response_data = json.dumps(email_data)
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Content-Length', len(response_data))
                self.end_headers()
                self.wfile.write(response_data.encode())
            else:
                self.send_response(404)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Email not found'}).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())

    def handle_emails(self, query):
        try:
            page = int(query.get('page', [1])[0])
            per_page = int(query.get('per_page', [20])[0])
            search = query.get('search', [''])[0].lower()
            from_date = query.get('from_date', [''])[0]
            to_date = query.get('to_date', [''])[0]
            sender = query.get('sender', [''])[0].lower()

            emails = []
            total = 0

            for message in self.mbox:
                try:
                    date_str = message.get('date')
                    if not date_str:
                        continue
                        
                    date_tuple = email.utils.parsedate_tz(date_str)
                    if not date_tuple:
                        continue
                        
                    date = datetime.fromtimestamp(email.utils.mktime_tz(date_tuple))

                    if from_date and date < datetime.strptime(from_date, '%Y-%m-%d'):
                        continue
                    if to_date and date > datetime.strptime(to_date, '%Y-%m-%d'):
                        continue

                    msg_sender = message.get('from', '')
                    if sender and sender not in msg_sender.lower():
                        continue

                    subject = message.get('subject', '(No subject)')
                    if search and search not in subject.lower() and search not in msg_sender.lower():
                        continue

                    payload = message.get_payload()
                    if isinstance(payload, list):
                        payload = '\n'.join([p.as_string() if hasattr(p, 'as_string') else str(p) for p in payload])
                    elif hasattr(payload, 'as_string'):
                        payload = payload.as_string()

                    emails.append({
                        'id': total,
                        'subject': subject,
                        'from': msg_sender,
                        'date': date.strftime('%Y-%m-%d %H:%M:%S'),
                        'body': payload
                    })
                    total += 1
                except Exception as e:
                    print(f"Error processing message: {e}")
                    continue

            start = (page - 1) * per_page
            end = start + per_page
            paginated = emails[start:end]

            response_data = json.dumps({
                'emails': paginated,
                'total': total,
                'page': page,
                'per_page': per_page,
                'total_pages': (total + per_page - 1) // per_page
            })

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Content-Length', len(response_data))
            self.end_headers()
            self.wfile.write(response_data.encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())

def run_server(mbox_path='emails.mbox', port=8000):
    if not os.path.exists(mbox_path):
        print(f"Error: MBOX file not found at {mbox_path}")
        return

    def handler(*args, **kwargs):
        return MboxHandler(mbox_path, *args, **kwargs)

    server = HTTPServer(('', port), handler)
    print(f'Server running on http://localhost:{port}')
    print(f'Using MBOX file: {mbox_path}')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.server_close()

if __name__ == '__main__':
    run_server()
