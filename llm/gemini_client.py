import google.generativeai as genai
import os

def init_gemini(api_key):
    genai.configure(api_key="AIzaSyDaW3FIrAlu3Kf_iLIDt8j5wlOw3lXTDiY")
    return genai.GenerativeModel(model_name="gemini-2.0-flash")
