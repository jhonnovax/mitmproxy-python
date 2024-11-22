import re
import mimetypes
from mitmproxy import http

# Mapping of URL patterns to local file paths
REDIRECTS = {
    r"https://example\.com/static/(.*)": "/path/to/local/files/static/\\1",
    r"https://cdn\.example\.com/assets/(.*)": "/path/to/assets/\\1",
}

def request(flow: http.HTTPFlow) -> None:
    for pattern, local_path in REDIRECTS.items():
        match = re.match(pattern, flow.request.url)
        if match:
            # Resolve the local file path using the regex match
            resolved_path = re.sub(pattern, local_path, flow.request.url)
            try:
                with open(resolved_path, "rb") as f:
                    content = f.read()
                
                # Dynamically determine the content type
                content_type, _ = mimetypes.guess_type(resolved_path)
                if not content_type:
                    content_type = "application/octet-stream"  # Default fallback

                # Return the local file content
                flow.response = http.Response.make(
                    200,  # HTTP status code
                    content,
                    {"Content-Type": content_type}  # Dynamically set the MIME type
                )
                print(f"Redirected {flow.request.url} to {resolved_path}")
            except FileNotFoundError:
                # If the local file is not found, continue with the original request
                print(f"File not found for {flow.request.url}. Continuing with the original request.")
            break