# Healora: Your Safe Space for Healing and Hope

## Overview
Healora is a mental health support chatbot designed to provide empathetic, region-specific assistance. Built with Python using the Gradio framework, it integrates the Google Gemini AI (`learnlm-1.5-pro-experimental`) for conversations, Gmail API for appointment scheduling, and Plotly/Pandas for mood tracking. It offers coping strategies, emergency resources, therapist appointments, and conversation history management tailored to users' needs.

## Features
- **Conversational Support**: AI-driven responses with adjustable tones (Neutral, Calm, Motivational) and language detection.
- **Mood Tracking**: Log moods and visualize trends with interactive plots.
- **Coping Strategies**: Personalized advice based on selected mood (Happy, Sad, Anxious, Stressed, Other).
- **Regional Resources**: Displays emergency helplines for USA, India, UK, and Global regions.
- **Appointment Scheduling**: Book appointments with therapists and receive email notifications.
- **Emergency Meeting**: Request urgent Google Meet sessions with therapists.
- **Conversation History**: Archive and reload past conversations.

## Prerequisites
- Python 3.7 or higher
- Required dependencies: `gradio`, `google-generativeai`, `plotly`, `pandas`, `langdetect`, `google-auth-oauthlib`, `google-auth-httplib2`, `google-api-python-client`
- Environment variables: `GEMINI_API_KEY`, `GMAIL_ADDRESS`, `GMAIL_TOKEN_JSON`

## Installation
1. Clone the repository or save the code as `healora_chatbot.py`.
2. Install dependencies:
   ```bash
   pip install gradio google-generativeai plotly pandas langdetect google-auth-oauthlib google-auth-httplib2 google-api-python-client
   ```
3. Set up environment variables in a `.env` file or system environment:
   ```
   GEMINI_API_KEY=your_gemini_api_key
   GMAIL_ADDRESS=your_gmail_address
   GMAIL_TOKEN_JSON=your_generated_token
   ```
   - Obtain `GEMINI_API_KEY` from Google AI Studio.
   - Generate `GMAIL_TOKEN_JSON` via Google Cloud Console with Gmail API enabled.
4. Run the application:
   ```bash
   python healora_chatbot.py
   ```
   - Access the interface at `http://127.0.0.1:7860`.

## Usage
### Interface
- **Header**: Displays the title and welcome message.
- **Controls**: Dropdowns for mood, conversation style, region, and a text box for input.
- **Chat Area**: Shows bot responses (left) and user messages (right).
- **Buttons**: "Send", "Clear Chat", "New Conversation", "Emergency Resources".
- **Accordions**: "Mood Journal", "Schedule Appointment", "Request Emergency Meeting".

### Workflow
1. Select a region (e.g., "USA") and mood (e.g., "Sad").
2. Type a message (e.g., "I feel overwhelmed") and click "Send" for a response with coping tips and resources.
3. Log moods or view trends in the "Mood Journal".
4. Click "Emergency Resources" for region-specific helplines.
5. Schedule an appointment by selecting a therapist, time, date, and email.
6. Request an emergency meeting with details and confirm to send an alert.
7. Use "New Conversation" to archive and start fresh, or load past chats from the dropdown.

## Configuration
- **Gemini Model**: Uses `learnlm-1.5-pro-experimental` with `temperature=0.7` and `max_output_tokens=200`.
- **Therapists**: Predefined list with specialties and time slots (e.g., Dr. Jane Smith for Anxiety and Depression).
- **Email**: Notifications sent from `GMAIL_ADDRESS` to therapist and user emails.

## Future Improvements
- Add multilingual support.
- Integrate real-time therapist availability.
- Enhance UI with themes or animations.
- Implement user authentication.
- Add voice interaction.

## License
For educational purposes.

## Contributing
Feel free to submit issues or pull requests on the repository (if hosted). Contributions to improve features or fix bugs are welcome!

## Contact
For support, reach out via the project repository or email (if applicable).
