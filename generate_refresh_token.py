#!/usr/bin/env python3
"""Script to generate a Google Ads API OAuth 2.0 refresh token.

Takes a Client ID and Client Secret, prompts the user to authenticate in the browser,
and outputs both the refresh token and an authorized_user JSON file ready for Antigravity.
"""

import argparse
import json
import os
import sys

try:
    from google_auth_oauthlib.flow import InstalledAppFlow
except ImportError:
    print(
        "Error: 'google-auth-oauthlib' is required.\n"
        "Please install it with: pip install google-auth-oauthlib",
        file=sys.stderr,
    )
    sys.exit(1)

# Google Ads API Scope
SCOPES = ["https://www.googleapis.com/auth/adwords"]


def main():
    parser = argparse.ArgumentParser(
        description="Generate a Google Ads OAuth 2.0 refresh token using Client ID & Secret."
    )
    parser.add_argument(
        "--client-id",
        help="Google OAuth 2.0 Client ID",
        default=os.environ.get("GOOGLE_CLIENT_ID"),
    )
    parser.add_argument(
        "--client-secret",
        help="Google OAuth 2.0 Client Secret",
        default=os.environ.get("GOOGLE_CLIENT_SECRET"),
    )
    parser.add_argument(
        "--output",
        "-o",
        default="google_ads_credentials.json",
        help="Output path for the generated credentials JSON file (default: google_ads_credentials.json)",
    )
    args = parser.parse_args()

    client_id = args.client_id
    if not client_id:
        client_id = input("Enter your Google Client ID: ").strip()

    client_secret = args.client_secret
    if not client_secret:
        client_secret = input("Enter your Google Client Secret: ").strip()

    if not client_id or not client_secret:
        print("Error: Both Client ID and Client Secret are required.", file=sys.stderr)
        sys.exit(1)

    client_config = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    }

    print("\nInitiating OAuth 2.0 flow for Google Ads API...")
    flow = InstalledAppFlow.from_client_config(client_config, scopes=SCOPES)

    print("Opening browser for authorization (or follow the URL if running headlessly)...")
    credentials = flow.run_local_server(
        port=0,
        prompt="consent",
        access_type="offline",
    )

    refresh_token = credentials.refresh_token
    if not refresh_token:
        print(
            "\nWarning: No refresh token returned. This can happen if prompt='consent' was ignored "
            "or access was already granted. Try revoking access from https://myaccount.google.com/permissions and run again.",
            file=sys.stderr,
        )
        sys.exit(1)

    print("\n" + "=" * 60)
    print("OAuth Authentication Successful!")
    print(f"Refresh Token: {refresh_token}")
    print("=" * 60)

    # Save credentials in Google's authorized_user format
    creds_data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "type": "authorized_user",
    }

    output_path = os.path.abspath(args.output)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(creds_data, f, indent=2)

    print(f"\nSaved Antigravity-ready credentials file to:\n  {output_path}\n")
    print("You can configure Antigravity in ~/.gemini/config/mcp_config.json with:")
    print(f'  "GOOGLE_APPLICATION_CREDENTIALS": "{output_path}"')


if __name__ == "__main__":
    main()
