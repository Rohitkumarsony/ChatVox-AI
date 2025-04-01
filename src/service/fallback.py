import random
import string

# Generate a random username
def random_valid_name(length=5):
    """Generate a random username with the specified length."""
    first_char = random.choice(string.ascii_uppercase)
    remaining_chars = ''.join(random.choice(string.ascii_lowercase) for _ in range(length - 1))
    return first_char + remaining_chars



def random_valid_name_for_voice():
    """Generate a random AI-friendly name similar to human names but unique."""
    bot_names = ["Alexon", "Zylo", "Lexar", "Jexi", "Kairo", 
                 "Vexo", "Sirius", "Nexo", "Axion", "Zyron"]
    return random.choice(bot_names)

# Define fallback responses
def get_random_fallback_response_for_voice(user_name):
    """Get a random fallback response, including the username."""
    fallback_responses = [
        f"I'm sorry, {user_name}, I couldn't find the answer to that. Can you explain a bit more about what you're looking for?",
        f"Hmm, {user_name}, I couldn't find enough context to answer that. What exactly would you like me to focus on?",
        f"That’s a tricky one, {user_name}. Can you provide more details or clarify what you’re asking?",
        f"Sorry about that, {user_name}. Could you share more context or clarify your question?",
        f"Apologies, {user_name}, I don’t have enough information to assist. What else can you share about this?",
        f"Hmm, {user_name}, that’s outside my knowledge right now. What other details can you provide?",
        f"Oops, {user_name}! I didn’t get enough information for that. Can you rephrase your question?",
        f"Sorry, {user_name}, I don’t have an answer for that right now. What else should I know to assist you better?",
        f"Hmm, {user_name}, I don’t have the details to answer that. Can you tell me more about what you’re looking for?",
    ] 
    return random.choice(fallback_responses)

# Define fallback responses
def get_random_fallback_response(user_name):
    """Get a random fallback response, including the username."""
    fallback_responses = [
        f"I'm sorry, {user_name}, I couldn't find the answer to that. Can you explain a bit more about what you're looking for? 😊",
        f"Hmm, {user_name}, I couldn't find enough context to answer that. What exactly would you like me to focus on? 😊",
        f"That’s a tricky one, {user_name}. Can you provide more details or clarify what you’re asking? 😊",
        f"Hmm, {user_name}, I might need more details to help with that. Could you rephrase or be more specific? 😊",
        f"Sorry about that, {user_name}. Could you share more context or clarify your question? 😊",
        f"Oops! I couldn’t find the answer, {user_name}. Can you ask in a different way or give me an example? 😊",
        f"That’s a tough question, {user_name}. Can you tell me more so I can try to help? 😊",
        f"Apologies, {user_name}, I don’t have enough information to assist. What else can you share about this? 😊",
        f"Hmm, {user_name}, that’s outside my knowledge right now. What other details can you provide? 😊",
        f"I couldn’t find what you’re looking for, {user_name}. Can you explain what you need in another way? 😊",
        f"Oops, {user_name}! I didn’t get enough information for that. Can you rephrase your question? 😊",
        f"I don’t have enough information, {user_name}. What other specifics can you provide? 😊",
        f"That question’s a bit tricky, {user_name}. Can you share more details or examples? 😊",
        f"Sorry, {user_name}, I don’t have an answer for that right now. What else should I know to assist you better? 😊",
        f"Hmm, {user_name}, I don’t have the details to answer that. Can you tell me more about what you’re looking for? 😊",
        f"That’s a tough one, {user_name}! Could you let me know how I can assist better? 😊",
        f"Hmm, {user_name}, I don’t have enough context. Can you share more about what you need? 😊",
        f"I’m sorry, {user_name}, I don’t have the answer yet. What’s the key detail I should focus on? 😊",
        f"Oops, {user_name}, I couldn’t help this time. Can you let me know what else you’re curious about? 😊",
        f"I couldn’t find enough information, {user_name}. Could you give me an example of what you mean? 😊",
        f"Apologies, {user_name}. Can you let me know what exactly you need help with? 😊",
        f"I’m not sure about that one, {user_name}. Can you share more details or a different question? 😊",
        f"Hmm, {user_name}, I couldn’t get the right context for that. Can you try asking in another way? 😊",
        f"I’m not quite sure, {user_name}. Could you give me a little more detail to work with? 😊",
        f"That one’s tough, {user_name}. What else can you share to help me understand better? 😊",
        f"Oops! I couldn’t quite find the right answer, {user_name}. Could you provide more details? 😊",
        f"Hmm, {user_name}, I don’t have enough to go on. What else can you tell me? 😊",
        f"I couldn’t find the answer, {user_name}. What’s another way to approach this question? 😊",
        f"I’m not sure I got that, {user_name}. Could you rephrase your question? 😊",
        f"Sorry, {user_name}, I couldn’t help with that. What other angle should we try? 😊",
    ]
    return random.choice(fallback_responses)

