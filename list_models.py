#!/usr/bin/env python3
"""
List available Gemini models
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

print("📋 Available Gemini Models:\n")
print("=" * 80)

try:
    models = genai.list_models()
    for model in models:
        print(f"✅ {model.name}")
        if 'generateContent' in model.supported_generation_methods:
            print(f"   - Supports: generateContent")
        print()
except Exception as e:
    print(f"Error: {e}")

print("=" * 80)
