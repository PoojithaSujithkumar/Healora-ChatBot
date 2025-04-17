import gradio as gr
import google.generativeai as genai
import os
from datetime import datetime
import plotly.express as px
import pandas as pd
from langdetect import detect
import random
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64
from email.mime.text import MIMEText
import re
import json

# Configure Gemini API (expects GEMINI_API_KEY in Hugging Face secrets)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Gmail API configuration (expects GMAIL_ADDRESS, GMAIL_TOKEN_JSON in secrets)
GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS")
GMAIL_TOKEN_JSON = os.getenv("GMAIL_TOKEN_JSON")

# Initialize Gmail API client
def get_gmail_service():
    try:
        creds = Credentials.from_authorized_user_info(json.loads(GMAIL_TOKEN_JSON))
        return build("gmail", "v1", credentials=creds)
    except Exception as e:
        raise Exception(f"Failed to initialize Gmail API: {str(e)}")

# Coping Strategies Library
coping_strategies = {
    "happy": [
        "Keep the positivity flowing! Try writing down three things you’re grateful for today.",
        "Share your joy! Call a friend or loved one to spread the good vibes."
    ],
    "sad": [
        "It’s okay to feel this way. Try a gentle activity like listening to calming music or taking a short walk.",
        "Write down your thoughts in a journal to process what’s on your mind."
    ],
    "anxious": [
        "Take slow, deep breaths: inhale for 4 seconds, hold for 4, exhale for 4.",
        "Try a grounding exercise: name 5 things you see, 4 you can touch, 3 you hear, 2 you smell, 1 you taste."
    ],
    "stressed": [
        "Pause for a moment and stretch your body to release tension.",
        "Break tasks into smaller steps and tackle one at a time."
    ],
    "other": [
        "Reflect on what’s on your mind with a quick mindfulness moment: focus on your breath for 60 seconds.",
        "Engage in a favorite hobby to lift your spirits."
    ]
}

# Regional Resources
regional_resources = {
    "USA": [
        "National Suicide Prevention Lifeline: 1-800-273-8255",
        "Crisis Text Line: Text HOME to 741741",
        "[MentalHealth.gov](https://www.mentalhealth.gov/)"
    ],
    "India": [
        "Vandrevala Foundation: 1860-2662-345",
        "AASRA Suicide Prevention: +91-9820466726",
        "[iCall Helpline](https://icallhelpline.org/)"
    ],
    "UK": [
        "Samaritans: 116 123",
        "Shout Crisis Text Line: Text SHOUT to 85258",
        "[Mind UK](https://www.mind.org.uk/)"
    ],
    "Global": [
        "Befrienders Worldwide: [Find a helpline](https://befrienders.org/)",
        "[WHO Mental Health Resources](https://www.who.int/health-topics/mental-health)"
    ]
}

# Mock Therapist Database
therapists = {
    "Dr. Jane Smith": {
        "specialty": "Anxiety and Depression",
        "email": "jane.smith@example.com",
        "times": ["09:00", "11:00", "14:00", "16:00"]
    },
    "Dr. Amit Patel": {
        "specialty": "Stress Management",
        "email": "amit.patel@example.com",
        "times": ["10:00", "12:00", "15:00", "17:00"]
    },
    "Dr. Sarah Brown": {
        "specialty": "Trauma and PTSD",
        "email": "sarah.brown@example.com",
        "times": ["08:00", "13:00", "15:30", "18:00"]
    }
}

# Initialize Gemini model
model = genai.GenerativeModel("learnlm-1.5-pro-experimental", 
                             generation_config={"temperature": 0.7, "max_output_tokens": 200})

# Chatbot function
def chatbot_function(message, mood, conversation_mode, region, state):
    if "chat_history" not in state:
        state["chat_history"] = []
    if "conversation_archive" not in state:
        state["conversation_archive"] = []
    if "current_conversation_id" not in state:
        state["current_conversation_id"] = 0
    
    history = state["chat_history"]
    
    try:
        lang = detect(message) if message.strip() else "en"
    except:
        lang = "en"
    
    if mood and mood != "Select mood (optional)":
        history.append([f"I'm feeling {mood.lower()}.", None])
    
    history.append([message, None])
    
    tone_instruction = {
        "Calm": "Respond in a soothing, gentle tone to promote relaxation.",
        "Motivational": "Use an uplifting, encouraging tone to inspire confidence.",
        "Neutral": "Maintain a balanced, empathetic tone."
    }.get(conversation_mode, "Maintain a balanced, empathetic tone.")
    
    prompt = f"""
    You are Healora, a compassionate mental health support chatbot. Engage in a supportive conversation with the user based on their input: {message}. 
    - Provide empathetic, sensitive responses in the user's language (detected as {lang}).
    - {tone_instruction}
    - If signs of distress are detected, suggest coping strategies relevant to their mood or input.
    - Recommend professional resources tailored to the user's region ({region}).
    - Keep responses concise, warm, and encouraging.
    """
    
    try:
        response = model.generate_content(prompt)
        response_text = response.text
    except Exception:
        response_text = "I'm here for you. Could you share a bit more so I can support you better?"
    
    if mood and mood != "Select mood (optional)":
        mood_key = mood.lower()
        if mood_key in coping_strategies:
            strategy = random.choice(coping_strategies[mood_key])
            response_text += f"\n\n**Coping Strategy**: {strategy}"
    
    region_key = region if region in regional_resources else "Global"
    resources = "\n\n**Recommended Resources**:\n" + "\n".join(regional_resources[region_key])
    response_text += resources
    
    history[-1][1] = response_text
    state["chat_history"] = history
    
    chat_display = generate_chat_display(history)
    
    return chat_display, state

# Generate chat display with left/right alignment and black text
def generate_chat_display(history):
    chat_display = """
    <style>
        .chat-container { max-width: 600px; margin: auto; }
        .message { margin: 10px 0; padding: 10px; border-radius: 10px; width: 80%; color: #000000; }
        .bot-message { background-color: #3A3B3C; float: left; clear: both; }
        .user-message { background-color: #192734; float: right; clear: both; }
    </style>
    <div class='chat-container'>
    """
    for user_msg, bot_msg in history:
        if user_msg:
            chat_display += f"<div class='message user-message'><strong>You</strong>: {user_msg}</div>"
        if bot_msg:
            chat_display += f"<div class='message bot-message'><strong>Healora</strong>: {bot_msg}</div>"
    chat_display += "</div>"
    return chat_display

# Clear chat history
def clear_chat(state):
    state["chat_history"] = []
    return "", state

# Start new conversation
def new_conversation(state):
    if state["chat_history"]:
        state["conversation_archive"].append({
            "id": state["current_conversation_id"],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "history": state["chat_history"]
        })
        state["current_conversation_id"] += 1
        state["chat_history"] = []
    return "", update_conversation_dropdown(state), state

# Update conversation dropdown
def update_conversation_dropdown(state):
    choices = ["Current Conversation"] + [
        f"Conversation {conv['id']} ({conv['timestamp']})" 
        for conv in state["conversation_archive"]
    ]
    return gr.update(choices=choices, value="Current Conversation")

# Load selected conversation
def load_conversation(selected_conversation, state):
    if selected_conversation == "Current Conversation":
        return generate_chat_display(state["chat_history"]), state
    else:
        for conv in state["conversation_archive"]:
            if f"Conversation {conv['id']} ({conv['timestamp']})" == selected_conversation:
                return generate_chat_display(conv["history"]), state
        return generate_chat_display(state["chat_history"]), state

# Mood journal function
def log_mood(mood, state):
    if mood and mood != "Select mood (optional)":
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        state["mood_journal"].append({"timestamp": timestamp, "mood": mood.lower()})
        return "Mood logged successfully!", state
    return "Please select a mood to log.", state

# Mood trend visualization
def show_mood_trends(state):
    if not state["mood_journal"]:
        return "No moods logged yet.", state
    df = pd.DataFrame(state["mood_journal"])
    fig = px.line(df, x="timestamp", y="mood", title="Mood Trends Over Time", markers=True)
    return fig, state

# Emergency resources
def show_emergency_resources(region):
    region_key = region if region in regional_resources else "Global"
    return f"**Crisis Support ({region_key})**:\n" + "\n".join(regional_resources[region_key])

# Get available times and therapist details
def get_therapist_details(therapist):
    if therapist and therapist in therapists:
        details = f"""
        **Therapist Details**:
        - Name: {therapist}
        - Specialty: {therapists[therapist]["specialty"]}
        - Email: {therapists[therapist]["email"]}
        """
        return gr.update(choices=therapists[therapist]["times"], value=None), details
    return gr.update(choices=[], value=None), "Please select a therapist."

# Create MIME message for Gmail API
def create_message(to, subject, message_text):
    message = MIMEText(message_text)
    message["to"] = to
    message["from"] = GMAIL_ADDRESS
    message["subject"] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {"raw": raw}

# Send emails using Gmail API
def send_emails(therapist, time_slot, date, user_email, therapist_email, appointment_note, chat_history, state):
    if "failed_emails" not in state:
        state["failed_emails"] = []
    
    # Format chat history for email
    chat_history_text = "Chat History:\n"
    for user_msg, bot_msg in chat_history:
        if user_msg:
            chat_history_text += f"You: {user_msg}\n"
        if bot_msg:
            chat_history_text += f"Healora: {bot_msg}\n"
    
    therapist_body = f"""
Dear {therapist},

You have a new appointment:
- Date: {date}
- Time: {time_slot}
- Client Email: {user_email}
- Note: {appointment_note}
- Therapist Details:
  - Specialty: {therapists[therapist]["specialty"]}
  - Email: {therapist_email}
- {chat_history_text}

Please confirm with the client.

Best,
Healora
    """
    therapist_message = create_message(therapist_email, "New Appointment", therapist_body)
    
    user_body = f"""
Dear User,

Your appointment is booked:
- Therapist: {therapist}
- Specialty: {therapists[therapist]["specialty"]}
- Email: {therapist_email}
- Date: {date}
- Time: {time_slot}
- Note: {appointment_note}

Expect a confirmation from {therapist}.

Best,
Healora
    """
    user_message = create_message(user_email, "Appointment Confirmation", user_body)
    
    try:
        service = get_gmail_service()
        therapist_result = service.users().messages().send(userId="me", body=therapist_message).execute()
        user_result = service.users().messages().send(userId="me", body=user_message).execute()
        return True, ""
    except HttpError as e:
        error_msg = f"Gmail API error: {str(e)}"
        state["failed_emails"].append({
            "therapist_email": {"to": therapist_email, "subject": "New Appointment", "body": therapist_body},
            "user_email": {"to": user_email, "subject": "Appointment Confirmation", "body": user_body},
            "error": error_msg,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        return False, error_msg
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        state["failed_emails"].append({
            "therapist_email": {"to": therapist_email, "subject": "New Appointment", "body": therapist_body},
            "user_email": {"to": user_email, "subject": "Appointment Confirmation", "body": user_body},
            "error": error_msg,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        return False, error_msg

# Schedule appointment
def schedule_appointment(therapist, time_slot, date, user_email, appointment_note, state):
    if not therapist or therapist not in therapists:
        return "Please select a therapist.", state
    if not time_slot or time_slot not in therapists[therapist]["times"]:
        return "Please select a valid time slot.", state
    if not date:
        return "Please select a date.", state
    if not user_email or not re.match(r"[^@]+@[^@]+\.[^@]+", user_email):
        return "Please enter a valid email address.", state
    
    try:
        appointment_date = datetime.strptime(date, "%Y-%m-%d")
        if appointment_date < datetime.now():
            return "Please select a future date.", state
    except ValueError:
        return "Invalid date format. Use YYYY-MM-DD.", state
    
    appointment = {
        "therapist": therapist,
        "time": time_slot,
        "date": date,
        "user_email": user_email,
        "appointment_note": appointment_note,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    state["appointments"].append(appointment)
    
    therapist_email = therapists[therapist]["email"]
    success, error_msg = send_emails(therapist, time_slot, date, user_email, therapist_email, appointment_note, state["chat_history"], state)
    if success:
        return f"Appointment booked with {therapist} on {date} at {time_slot}.", state
    else:
        return (f"Appointment booked with {therapist} on {date} at {time_slot}. "
                f"Emails from {GMAIL_ADDRESS} could not be sent. "
                f"Please email {therapist_email} with your details (date: {date}, time: {time_slot}, note: {appointment_note}) "
                f"and check {user_email} for confirmation (spam/junk)."), state

# Emergency meeting
def request_emergency_meeting(therapist, user_name, gender, age, user_email, state):
    if not therapist or therapist not in therapists:
        return "Please select a therapist.", "", state
    if not user_name:
        return "Please enter your name.", "", state
    if not gender:
        return "Please select your gender.", "", state
    if not age:
        return "Please enter your age.", "", state
    if not user_email or not re.match(r"[^@]+@[^@]+\.[^@]+", user_email):
        return "Please enter a valid email address.", "", state
    
    meeting_link = "https://meet.google.com/rek-ocrw-sjc"
    confirmation_message = f"""
    **Emergency Meeting Requested**
    - Therapist: {therapist}
    - Meeting Link: {meeting_link}
    
    Would you like to start the meeting now?
    """
    state["emergency_meeting"] = {
        "therapist": therapist,
        "user_name": user_name,
        "gender": gender,
        "age": age,
        "user_email": user_email,
        "meeting_link": meeting_link
    }
    return confirmation_message, gr.update(visible=True), state

# Confirm emergency meeting
def confirm_emergency_meeting(confirm, state):
    if "emergency_meeting" not in state:
        return "No emergency meeting requested.", state
    
    if confirm == "Yes":
        meeting_info = state["emergency_meeting"]
        therapist = meeting_info["therapist"]
        user_name = meeting_info["user_name"]
        gender = meeting_info["gender"]
        age = meeting_info["age"]
        user_email = meeting_info["user_email"]
        meeting_link = meeting_info["meeting_link"]
        therapist_email = os.getenv("THERAPIST_GMAIL_ADDRESS")
        
        alert_body = f"""
Dear {therapist},

An emergency meeting has been requested:
- Client Name: {user_name}
- Gender: {gender}
- Age: {age}
- Client Email: {user_email}
- Google Meet Link: {meeting_link}

Please join the meeting as soon as possible.

Best,
Healora
        """
        alert_message = create_message(therapist_email, "Emergency Meeting Request", alert_body)
        
        try:
            service = get_gmail_service()
            service.users().messages().send(userId="me", body=alert_message).execute()
            return f"Emergency meeting alert sent to {therapist}. Join the meeting at {meeting_link}.", state
        except Exception as e:
            state["failed_emails"].append({
                "therapist_email": {"to": therapist_email, "subject": "Emergency Meeting Request", "body": alert_body},
                "error": str(e),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            return (f"Failed to send emergency meeting alert to {therapist}. "
                    f"Please contact {therapist_email} directly with the meeting link: {meeting_link}."), state
    else:
        return "Emergency meeting cancelled.", state

# Gradio Interface
with gr.Blocks(title="Healora: Mental Health Support Chatbot") as demo:
    state = gr.State({"chat_history": [], "conversation_archive": [], "current_conversation_id": 0, "mood_journal": [], "appointments": [], "failed_emails": []})
    
    gr.Markdown("# Healora: Your Safe Space for Healing and Hope")
    gr.Markdown("I'm here to listen and support you. Feel free to share how you're feeling.")
    
    mood = gr.Dropdown(
        choices=["Select mood (optional)", "Happy", "Sad", "Anxious", "Stressed", "Other"],
        label="How are you feeling today? (Optional)"
    )
    
    conversation_mode = gr.Radio(
        choices=["Neutral", "Calm", "Motivational"],
        label="Conversation Style",
        value="Neutral"
    )
    
    region = gr.Dropdown(
        choices=["USA", "India", "UK", "Global"],
        label="Select your region for tailored resources",
        value="Global"
    )
    
    with gr.Row():
        conversation_dropdown = gr.Dropdown(
            choices=["Current Conversation"],
            label="Select Conversation",
            value="Current Conversation"
        )
        new_conversation_btn = gr.Button("New Conversation")
    
    chatbot = gr.HTML(
        label="Conversation",
        value=""
    )
    user_input = gr.Textbox(
        placeholder="Type your message here...",
        label="Your Message"
    )
    
    with gr.Row():
        submit_btn = gr.Button("Send")
        clear_btn = gr.Button("Clear Chat")
    
    emergency_btn = gr.Button("Emergency Resources")
    emergency_output = gr.Markdown("")
    
    with gr.Accordion("Mood Journal"):
        log_mood_btn = gr.Button("Log Mood")
        mood_log_output = gr.Textbox(label="Mood Log Status", interactive=False)
        mood_trend_btn = gr.Button("Show Mood Trends")
        mood_trend_output = gr.Plot()
    
    with gr.Accordion("Schedule Appointment"):
        therapist = gr.Dropdown(
            choices=list(therapists.keys()),
            label="Select a Therapist"
        )
        therapist_details = gr.Markdown("Select a therapist to view details.")
        time_slot = gr.Dropdown(
            choices=[],
            label="Select a Time Slot",
            value=None,
            interactive=True
        )
        date = gr.Textbox(
            label="Appointment Date (YYYY-MM-DD)",
            placeholder="e.g., 2025-04-20"
        )
        user_email = gr.Textbox(
            label="Your Email Address",
            placeholder="e.g., user@example.com"
        )
        appointment_note = gr.Textbox(
            label="Additional Note (Optional)",
            placeholder="Any specific details or concerns for the therapist"
        )
        schedule_btn = gr.Button("Book Appointment")
        schedule_output = gr.Textbox(label="Booking Status", interactive=False)
    
    with gr.Accordion("Request Emergency Meeting"):
        emergency_therapist = gr.Dropdown(
            choices=list(therapists.keys()),
            label="Select a Therapist"
        )
        user_name = gr.Textbox(
            label="Your Name",
            placeholder="e.g., John Doe"
        )
        gender = gr.Dropdown(
            choices=["Male", "Female", "Other"],
            label="Gender"
        )
        age = gr.Textbox(
            label="Age",
            placeholder="e.g., 30"
        )
        emergency_email = gr.Textbox(
            label="Your Email Address",
            placeholder="e.g., user@example.com"
        )
        emergency_btn = gr.Button("Request Emergency Meeting")
        emergency_output = gr.Markdown("")
        confirm_buttons = gr.Radio(
            choices=["Yes", "No"],
            label="Confirm Emergency Meeting",
            visible=False
        )
    
    submit_btn.click(
        fn=chatbot_function,
        inputs=[user_input, mood, conversation_mode, region, state],
        outputs=[chatbot, state]
    )
    user_input.submit(
        fn=chatbot_function,
        inputs=[user_input, mood, conversation_mode, region, state],
        outputs=[chatbot, state]
    )
    clear_btn.click(
        fn=clear_chat,
        inputs=[state],
        outputs=[chatbot, state]
    )
    new_conversation_btn.click(
        fn=new_conversation,
        inputs=[state],
        outputs=[chatbot, conversation_dropdown, state]
    )
    conversation_dropdown.change(
        fn=load_conversation,
        inputs=[conversation_dropdown, state],
        outputs=[chatbot, state]
    )
    emergency_btn.click(
        fn=show_emergency_resources,
        inputs=region,
        outputs=emergency_output
    )
    log_mood_btn.click(
        fn=log_mood,
        inputs=[mood, state],
        outputs=[mood_log_output, state]
    )
    mood_trend_btn.click(
        fn=show_mood_trends,
        inputs=[state],
        outputs=[mood_trend_output, state]
    )
    therapist.change(
        fn=get_therapist_details,
        inputs=therapist,
        outputs=[time_slot, therapist_details]
    )
    schedule_btn.click(
        fn=schedule_appointment,
        inputs=[therapist, time_slot, date, user_email, appointment_note, state],
        outputs=[schedule_output, state]
    )
    emergency_btn.click(
        fn=request_emergency_meeting,
        inputs=[emergency_therapist, user_name, gender, age, emergency_email, state],
        outputs=[emergency_output, confirm_buttons, state]
    )
    confirm_buttons.change(
        fn=confirm_emergency_meeting,
        inputs=[confirm_buttons, state],
        outputs=[emergency_output, state]
    )

    gr.Markdown("""
    ---
    **Helpful Resources:**
    - [National Suicide Prevention Lifeline](https://suicidepreventionlifeline.org/)
    - [MentalHealth.gov](https://www.mentalhealth.gov/)
    - [Crisis Text Line](https://www.crisistextline.org/)
    """)

if __name__ == "__main__":
    demo.launch()