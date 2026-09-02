# Standard-library imports used for environment variables and type hints.
import os
from typing import Any

# Third-party libraries used to build the interface and call Azure Speech.
import streamlit as st
import azure.cognitiveservices.speech as speechsdk
from azure.ai.translation.text import TextTranslationClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv


# Load values from a local .env file, if one is present.
load_dotenv()


# Configure the browser page before rendering any Streamlit components.
st.set_page_config(
    page_title="Azure Voice Studio",
    page_icon="◉",
    layout="centered",
    initial_sidebar_state="collapsed",
)


# Map the names shown in the dropdown to Azure Speech voice identifiers.
# The identifiers are the values required by the Azure Speech SDK.
VOICE_OPTIONS = {
    "Jenny · English (United States)": "en-US-JennyNeural",
    "Aria · English (United States)": "en-US-AriaNeural",
    "Guy · English (United States)": "en-US-GuyNeural",
    "Sonia · English (United Kingdom)": "en-GB-SoniaNeural",
    "Ryan · English (United Kingdom)": "en-GB-RyanNeural",
    "Ava · English (Canada)": "en-CA-ClaraNeural",
    "Natasha · English (Australia)": "en-AU-NatashaNeural",
    "Xiaoxiao · Chinese (Simplified)": "zh-CN-XiaoxiaoNeural",
    "Elvira · Spanish (Spain)": "es-ES-ElviraNeural",
    "Denise · French (France)": "fr-FR-DeniseNeural",
    "Hedda · German (Germany)": "de-DE-HeddaNeural",
    "Swara · Hindi (India)": "hi-IN-SwaraNeural",
    "Madhur · Hindi (India)": "hi-IN-MadhurNeural",
    "Aarav · Hindi (India)": "hi-IN-AaravNeural",
    "Ananya · Hindi (India)": "hi-IN-AnanyaNeural",
    # add voice options for Japanese
    "Nanami · Japanese (Japan)": "ja-JP-NanamiNeural",
    # add voice options for Korean
    "Sunwoo · Korean (Korea)": "ko-KR-SunwooNeural",
}


def get_setting(name: str) -> str:
    """Read a setting from Streamlit secrets, then fall back to the environment."""
    # Streamlit secrets are convenient for deployed apps, while environment
    # variables and .env files are convenient for local development.
    try:
        value = st.secrets.get(name)
    except (FileNotFoundError, KeyError):
        value = None
    return str(value or os.getenv(name, "")).strip()


def synthesize_speech(text: str, voice_name: str, speech_key: str, speech_region: str) -> bytes:
    """Convert text to WAV audio bytes using the selected Azure voice."""
    # Create the Azure client configuration using the supplied credentials.
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)
    speech_config.speech_synthesis_voice_name = voice_name

    # Request WAV-compatible PCM audio so it can be played and downloaded by
    # the browser without writing a temporary file to disk.
    speech_config.set_speech_synthesis_output_format(
        speechsdk.SpeechSynthesisOutputFormat.Riff24Khz16BitMonoPcm
    )

    # audio_config=None keeps the result in memory instead of sending it to
    # the computer's speakers or saving it directly to a file.
    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=None)
    result = synthesizer.speak_text_async(text).get()

    # Return the generated audio when Azure completes the request successfully.
    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        return bytes(result.audio_data)

    # Convert Azure cancellation details into a normal Python exception so the
    # caller can display a useful message in the Streamlit interface.
    if result.reason == speechsdk.ResultReason.Canceled:
        details = speechsdk.SpeechSynthesisCancellationDetails(result)
        message = details.error_details or "Azure Speech canceled the synthesis request."
        raise RuntimeError(message)
    raise RuntimeError("Azure Speech did not return audio for this request.")


def translate_to_english(
    text: str, translator_key: str, translator_region: str, translator_endpoint: str
) -> str:
    """Translate the submitted text to English without changing the speech input."""
    client = TextTranslationClient(
        endpoint=translator_endpoint,
        credential=AzureKeyCredential(translator_key),
        region=translator_region,
    )
    response = client.translate(
        body=[text],
        to_language=["en"],
    )
    if not response or not response[0].translations:
        raise RuntimeError("Azure Translator did not return an English translation.")
    return response[0].translations[0].text


def main() -> None:
    """Render the voice studio interface and process speech requests."""
    # Add the application's custom visual theme and responsive layout rules.
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
        :root { --ink: #17232d; --muted: #64717b; --paper: #f4f7f5; --mint: #b9e7d4; --coral: #ee765f; --line: #d9e4de; }
        .stApp { background: radial-gradient(circle at 100% 0%, #d8f2e6 0, transparent 34%), var(--paper); color: var(--ink); }
        .block-container { max-width: 780px; padding: 4rem 1.25rem 3rem; }
        h1, h2, h3 { font-family: 'Space Grotesk', sans-serif !important; color: var(--ink) !important; letter-spacing: -0.03em; }
        p, label, .stMarkdown, .stTextInput, .stTextArea, .stSelectbox { font-family: 'DM Sans', sans-serif; }
        .eyebrow { color: #177254; font: 700 .76rem 'DM Sans', sans-serif; letter-spacing: .16em; text-transform: uppercase; margin-bottom: .8rem; }
        .lede { color: var(--muted); font: 400 1.05rem/1.6 'DM Sans', sans-serif; max-width: 590px; margin-bottom: 2rem; }
        .panel { background: rgba(255,255,255,.82); border: 1px solid var(--line); border-radius: 18px; padding: 1.25rem 1.25rem .55rem; box-shadow: 0 8px 26px rgba(45, 77, 63, .07); margin-bottom: 1rem; }
        .panel-title { color: var(--ink); font: 700 1rem 'DM Sans', sans-serif; margin-bottom: .6rem; }
        .hint { color: var(--muted); font: .84rem/1.5 'DM Sans', sans-serif; margin-top: -.5rem; margin-bottom: 1rem; }
        div[data-testid='stForm'] { border: 0; padding: 0; }
        .stButton > button { background: var(--coral); color: white; border: 0; border-radius: 10px; font: 700 .95rem 'DM Sans', sans-serif; min-height: 3rem; box-shadow: 0 5px 12px rgba(238,118,95,.22); }
        .stButton > button:hover { background: #d9614d; color: white; }
        [data-testid='stAudio'] { margin-top: .75rem; }
        @media (max-width: 640px) { .block-container { padding-top: 2.5rem; } }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Render the page heading and short instructions for the user.
    st.markdown('<div class="eyebrow">Azure AI Speech · voice studio</div>', unsafe_allow_html=True)
    st.title("Give your words a voice.")
    st.markdown(
        '<div class="lede">Write or paste a message, choose a voice, and create a clear audio clip in seconds.</div>',
        unsafe_allow_html=True,
    )

    # Read credentials at runtime so secrets are not hard-coded in the source.
    speech_key = get_setting("AZURE_SPEECH_KEY")
    speech_region = get_setting("AZURE_SPEECH_REGION")
    translator_key = get_setting("AZURE_TRANSLATOR_KEY") or speech_key
    translator_region = get_setting("AZURE_TRANSLATOR_REGION") or speech_region
    translator_endpoint = (
        get_setting("AZURE_TRANSLATOR_ENDPOINT")
        or "https://api.cognitive.microsofttranslator.com"
    )

    # Group the text input, voice selector, and submit button into one form.
    # Streamlit evaluates the form values when the user submits the form.
    with st.form("speech_form"):
        st.markdown('<div class="panel-title">Your message</div>', unsafe_allow_html=True)
        text = st.text_area(
            "Text to read aloud",
            placeholder="Type or paste text here... उदाहरण: नमस्ते, आप कैसे हैं?",
            height=190,
            max_chars=5000,
            label_visibility="collapsed",
        )
        # Give the user guidance about length and punctuation.
        st.markdown('<div class="hint">Up to 5,000 characters. Punctuation helps Azure Speech find a natural rhythm.</div>', unsafe_allow_html=True)
        selected_voice = st.selectbox(
            "Voice",
            options=list(VOICE_OPTIONS),
            format_func=lambda voice: voice,
        )
        submitted = st.form_submit_button("Create audio", use_container_width=True)

    # Validate the submission before making a network request to Azure.
    if submitted:
        if not text.strip():
            st.warning("Add a message before creating audio.")
        elif not speech_key or not speech_region:
            st.error("Azure Speech credentials are missing. Add AZURE_SPEECH_KEY and AZURE_SPEECH_REGION to your environment or Streamlit secrets.")
        elif not translator_key or not translator_region:
            st.error("Azure Translator credentials are missing. Add AZURE_TRANSLATOR_KEY and AZURE_TRANSLATOR_REGION, or use the same Azure AI resource credentials as Speech.")
        else:
            # Show progress while the Azure SDK contacts the speech service.
            with st.spinner("Creating your audio clip..."):
                try:
                    # Translate separately, while preserving the original text
                    # for speech synthesis in the selected native voice.
                    st.session_state.translation = translate_to_english(
                        text.strip(),
                        translator_key,
                        translator_region,
                        translator_endpoint,
                    )
                    # Store the audio and selected voice in session state so
                    # they remain available after Streamlit reruns the script.
                    st.session_state.audio = synthesize_speech(
                        text.strip(), VOICE_OPTIONS[selected_voice], speech_key, speech_region
                    )
                    st.session_state.voice = selected_voice
                except Exception as error:  # noqa: BLE001 - show SDK errors in the app
                    st.session_state.audio = None
                    st.session_state.translation = None
                    st.error(f"Could not create audio: {error}")

    translation: str | None = st.session_state.get("translation")
    if translation:
        st.markdown('<div class="panel"><div class="panel-title">English translation</div>', unsafe_allow_html=True)
        st.write(translation)
        st.markdown("</div>", unsafe_allow_html=True)

    # Display the previous result, if synthesis succeeded in this session.
    audio: Any = st.session_state.get("audio")
    if audio:
        st.markdown('<div class="panel"><div class="panel-title">Your audio clip</div>', unsafe_allow_html=True)
        st.caption(f"Voice: {st.session_state.get('voice', selected_voice)}")
        st.audio(audio, format="audio/wav")
        st.download_button(
            "Download WAV",
            data=audio,
            file_name="azure-voice-clip.wav",
            mime="audio/wav",
            use_container_width=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)


    # Start the Streamlit application when this file is run directly.
if __name__ == "__main__":
    main()
