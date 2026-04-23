# 



import os
from groq import Groq

def test_key():
    api_key = os.environ.get("GROQ_API_KEY")

    if not api_key:
        print("API key not found. Set GROQ_API_KEY environment variable.")
        return False

    client = Groq(api_key=api_key)
    
    print("Testing Groq API...")

    try:
        completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": "Hello, are you working?",
                }
            ],
            model="llama3-8b-8192",
        )
        print("API Status: WORKING")
        print(f"Response: {completion.choices[0].message.content}")
        return True

    except Exception as e:
        print("API Status: FAILED")
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    test_key()