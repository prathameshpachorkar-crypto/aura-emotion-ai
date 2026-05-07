import google.generativeai as genai
from config import GEMINI_API_KEY

# Configure the API
genai.configure(api_key=GEMINI_API_KEY)

# Storing memory in memory (pun intended) for simple local execution.
chat_history = []

def get_system_prompt(emotion):
    """ Dynamically updates instructions based on the user's face. """
    base_prompt = "You are an AI emotional support and conversational chatbot. "
    
    emotion_guidelines = {
        "Happy": "The user looks HAPPY. Validate their positive state and encourage them to fully experience it. Suggest documenting the moment or practicing gratitude to reinforce positive neural pathways.",
        "Sad": "The user looks SAD. Use active listening and validate their feelings. Empathize and gently suggest grounding techniques, journaling, or CBT-inspired cognitive reframing without being dismissive of their current state.",
        "Angry": "The user looks ANGRY. Remain calm, grounding, and de-escalating. Encourage taking a step back, taking deep breaths, and finding a healthy outlet for the energy. Do not tell them to simply 'calm down'.",
        "Fear": "The user looks FEARFUL or ANXIOUS. Emphasize safety and reassurance. Guide them through the 4-7-8 breathing exercise or the 5-4-3-2-1 grounding technique (Psychological First Aid) to help regulate their nervous system.",
        "Surprise": "The user looks SURPRISED. Be curious and engaged. Validate their reaction and help them process whatever unexpected event occurred calmly.",
        "Disgust": "The user looks DISGUSTED. Be neutral, validating, and explore what triggered the feeling. Help them logically evaluate the situation and distance themselves if necessary.",
        "Neutral": "The user looks NEUTRAL. Provide normal, helpful, and polite responses. Ask open-ended questions to check in on their emotional state."
    }
    
    guideline = emotion_guidelines.get(emotion, emotion_guidelines["Neutral"])
    return base_prompt + guideline

def generate_emotion_response(user_message, current_emotion):
    global chat_history
    
    system_instruction = get_system_prompt(current_emotion)
    
    # Using Gemini 1.5 Flash as it's the fastest and supports system instructions natively
    model = genai.GenerativeModel(
        model_name='gemini-flash-latest',
        system_instruction=system_instruction
    )
    
    # Initialize a chat session with previous history
    chat = model.start_chat(history=chat_history)
    
    # Note: I pass the emotion context invisibly into the prompt so the model is strictly aware.
    contextual_prompt = f"[System Notice: The user's current detected emotion is {current_emotion}]. User says: {user_message}"
    
    try:
        response = chat.send_message(contextual_prompt)
        # Update history
        chat_history = chat.history
        return response.text
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return "I'm having trouble connecting to my brain right now. Please check my API key."