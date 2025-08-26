from django.shortcuts import render
from django.http import JsonResponse
import google.generativeai as genai
from datetime import datetime
import re

# Configure Gemini API
API_KEY = "AIzaSyBFHpWlfh6m9gyBNlutt03UTeUhUvOFKsc"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")
chat_session = model.start_chat()

def index(request):
    return render(request, "index.html")

def send_message(request):
    if request.method == "POST":
        user_message = request.POST.get("message")
        
        # Check if this is a simple greeting
        if is_simple_greeting(user_message):
            # Respond naturally to simple greetings
            response_text = get_natural_greeting_response()
        else:
            # Create a more specific prompt for complex queries
            prompt = f"""
            Please provide a well-structured response to the following query. 
            Use clear headings, bullet points, and paragraphs for better readability.
            Format your response using markdown-like syntax:
            - Use **bold** for important concepts
            - Use *italic* for emphasis
            - Use `code` for technical terms
            - Use # for main headings
            - Use ## for subheadings
            - Use - for bullet points
            
            Query: {user_message}
            """
            
            response = chat_session.send_message(prompt)
            response_text = format_gemini_response(response.text)
        
        timestamp = datetime.now().strftime("%H:%M")
        return JsonResponse({
            "reply": response_text,
            "timestamp": timestamp
        })

def is_simple_greeting(message):
    """Check if the message is a simple greeting"""
    simple_greetings = ["hi", "hello", "hey", "hi there", "hello there", "hey there"]
    message_lower = message.lower().strip()
    
    # Check for exact matches or messages that are just greetings
    if message_lower in simple_greetings:
        return True
        
    # Check for greetings with minimal additional text
    if len(message_lower.split()) <= 3:
        for greeting in simple_greetings:
            if message_lower.startswith(greeting):
                return True
                
    return False

def get_natural_greeting_response():
    """Return a natural response to greetings"""
    responses = [
        "Hello! How can I help you today? 😊",
        "Hi there! What would you like to know?",
        "Hey! Nice to chat with you. What's on your mind?",
        "Hi! I'm here to help. What can I assist you with?",
        "Hello! What can I do for you today?"
    ]
    
    # In a real implementation, you might want to randomize this
    return responses[0]

def format_gemini_response(text):
    """
    Further clean and format the response from Gemini AI
    """
    # Remove redundant phrases
    text = re.sub(r'^(当然|当然可以|当然,|好的|没问题).*?\.\s*', '', text)
    
    # Ensure proper paragraph breaks
    text = re.sub(r'\.\s+([A-Z])', '.\n\n\\1', text)
    
    # Format lists properly
    text = re.sub(r'(\d+\.)\s+', '\n\\1 ', text)
    text = re.sub(r'[-•]\s+', '\n- ', text)
    
    return text