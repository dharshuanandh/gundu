#!/usr/bin/env python3
import urllib.request
import sys

# Prepare multipart form data
boundary = '----WebKitFormBoundary1234567890'

with open('test_face_0.png', 'rb') as f:
    file_content = f.read()

# Build multipart body correctly with CRLF
parts = []
parts.append(f'--{boundary}\r\n'.encode())
parts.append(b'Content-Disposition: form-data; name="files"; filename="test_face_0.png"\r\n')
parts.append(b'Content-Type: image/png\r\n\r\n')
parts.append(file_content)
parts.append(b'\r\n')
parts.append(f'--{boundary}--\r\n'.encode())

multipart_body = b''.join(parts)

# Send request
req = urllib.request.Request(
    'http://127.0.0.1:8000/api/index',
    data=multipart_body,
    headers={
        'Content-Type': f'multipart/form-data; boundary={boundary}'
    }
)

try:
    with urllib.request.urlopen(req) as response:
        print(f"Status Code: {response.status}")
        print(f"Response: {response.read().decode()}")
except urllib.error.HTTPError as e:
    print(f"Status Code: {e.code}")
    print(f"Response: {e.read().decode()}")
except Exception as e:
    print(f"Error: {str(e)}")
    sys.exit(1)

