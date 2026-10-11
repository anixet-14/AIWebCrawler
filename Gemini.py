from google import genai
from google.genai.errors import APIError

# 🔑 CONFIGURATION
     # <-- Targeted model

def verify_specific_model():
    """
    Checks if the hardcoded API key works and if the specified
    Gemini model is active and accessible.
    """
    if GEMINI_API_KEY == "your_actual_key_here" or not GEMINI_API_KEY:
        print("❌ Error: Please update the 'GEMINI_API_KEY' variable with your actual token.")
        return

    try:
        print(f"Connecting to Google servers to test access for model: '{GEMINI_MODEL}'...")
        
        # Initialize the official SDK client with your key
        client = genai.Client(api_key=GEMINI_API_KEY)
        
        # Fetch metadata specifically for your chosen model
        # This checks permission boundaries without costing token usage
        model_info = client.models.get(model=GEMINI_MODEL)
        
        print(f"\n✅ Success! Your API key is valid and '{GEMINI_MODEL}' is working.")
        print("-" * 50)
        print(f"Model Name:  {model_info.name}")
        print(f"Display Name:{model_info.display_name}")
        print(f"Description: {model_info.description}")
        print("-" * 50)

    except APIError as e:
        print(f"\n❌ API Error: Connection failed.")
        print(f"Status Code: {e.code}")
        print(f"Message: {e.message}")
        if "not found" in e.message.lower():
            print(f"💡 Suggestion: Double-check that '{GEMINI_MODEL}' is spelled correctly or available in your region.")
            
    except Exception as e:
        print("\n❌ Error: An unexpected issue occurred.")
        print(f"Details: {e}")

if __name__ == "__main__":
    verify_specific_model()
