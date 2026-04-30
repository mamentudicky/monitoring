from google import genai
import os

client = genai.Client(api_key="AIzaSyBrrzrf0937zB8Hy4MgAhm58PjOxTJsElQ")

try:
    print("Listing models...")
    for model in client.models.list():
        print(f"Model: {model.name}")
except Exception as e:
    print(f"Error listing models: {e}")
