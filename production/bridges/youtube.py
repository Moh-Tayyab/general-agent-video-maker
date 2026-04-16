"""
YouTube upload bridge — authenticate, upload, set SEO metadata, thumbnail.
"""
import os
import json
import subprocess
import http.server
import socketserver
import webbrowser
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

class YouTubeBridge:
    def __init__(self, client_secrets_path: str):
        self.client_secrets = client_secrets_path
        self.credentials_path = os.path.join(os.path.dirname(client_secrets_path), "youtube_credentials.json")
        self.youtube = None

    def authenticate(self) -> bool:
        """Run OAuth flow, save tokens, build YouTube client."""
        if os.path.exists(self.credentials_path):
            # Load existing credentials
            from google.oauth2.credentials import Credentials
            creds = Credentials.from_authorized_user_file(self.credentials_path, SCOPES)
            if creds and creds.valid:
                self.youtube = build("youtube", "v3", credentials=creds)
                print("Authenticated from saved credentials.")
                return True

        # Run OAuth flow
        flow = InstalledAppFlow.from_client_secrets_file(self.client_secrets, SCOPES)
        creds = flow.run_local_server(port=8080, prompt="consent", access_type="offline")
        self.youtube = build("youtube", "v3", credentials=creds)

        # Save credentials
        with open(self.credentials_path, "w") as f:
            f.write(creds.to_json())
        print("Authenticated and credentials saved.")
        return True

    def get_channel_info(self):
        """Get authenticated channel details."""
        if not self.youtube:
            return None
        response = self.youtube.channels().list(part="snippet,contentDetails,statistics", mine=True).execute()
        return response

    def upload(
        self,
        video_path: str,
        title: str,
        description: str,
        tags: list[str],
        category_id: str = "22",  # People & Blogs
        privacy_status: str = "public",
        thumbnail_path: str = None
    ) -> dict:
        """
        Upload video with full SEO metadata.
        Returns: {"success": bool, "video_id": str, "video_url": str}
        """
        if not self.youtube:
            return {"success": False, "error": "Not authenticated"}

        body = {
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags,
                "categoryId": category_id,
                "defaultLanguage": "en",
            },
            "status": {
                "privacyStatus": privacy_status,
                "selfDeclaredMadeForKids": False,
            },
        }

        media = MediaFileUpload(video_path, chunksize=-1, resumable=True)

        request = self.youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media
        )

        print(f"Uploading: {title}")
        response = None
        try:
            status, response = request.next_chunk()
            if status:
                print(f"Upload progress: {int(status * 100)}%")
        except HttpError as e:
            return {"success": False, "error": str(e)}

        if response and "id" in response:
            video_id = response["id"]
            video_url = f"https://youtu.be/{video_id}"

            # Upload thumbnail
            if thumbnail_path and os.path.exists(thumbnail_path):
                self.youtube.thumbnails().set(
                    videoId=video_id,
                    media_body=MediaFileUpload(thumbnail_path)
                ).execute()
                print("Thumbnail uploaded.")

            return {
                "success": True,
                "video_id": video_id,
                "video_url": video_url,
                "title": title
            }
        return {"success": False, "error": "No video ID in response"}