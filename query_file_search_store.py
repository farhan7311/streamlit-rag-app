import os
from google import genai
from google.genai import types

# Set your Gemini API key
os.environ["GOOGLE_API_KEY"] = "AIzaSyDozUi50Nlq2YHmruVo9nmp0pybzfKPNpI"

# Initialize Gemini client
client = genai.Client()

# Use your actual File Search Store name (the one used with REST upload, e.g., fileSearchStores/xxxxxx)
file_search_store_name = "fileSearchStores/myfilesearchstore-8sfn1in8688v"

# Run a query against your uploaded document
while True:
    user_query = input("Ask something (or type 'exit' to quit): ")
    if user_query.lower() == "exit":
        break
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=user_query,
        config=types.GenerateContentConfig(
            tools=[
                types.Tool(
                    file_search=types.FileSearch(
                        file_search_store_names=[file_search_store_name]
                    )
                )
            ]
        )
    )
    print("Response:", response.text)
