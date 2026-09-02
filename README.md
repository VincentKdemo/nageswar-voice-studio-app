# Azure Voice Studio

A Streamlit app that translates typed text to English with Azure AI Translator while reading the original text aloud with Azure AI Speech.

## Run locally

1. Create and activate a virtual environment.
2. Install dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

3. Set credentials in a `.env` file in the project folder:

   ```dotenv
   AZURE_SPEECH_KEY=your-key
   AZURE_SPEECH_REGION=eastus
   # Optional when Speech and Translator use the same Azure AI resource.
   AZURE_TRANSLATOR_KEY=your-translator-key
   AZURE_TRANSLATOR_REGION=eastus
   AZURE_TRANSLATOR_ENDPOINT=https://api.cognitive.microsofttranslator.com
   ```

   You can also set them in your shell:

   ```powershell
   $env:AZURE_SPEECH_KEY = "your-key"
   $env:AZURE_SPEECH_REGION = "eastus"
   $env:AZURE_TRANSLATOR_KEY = "your-translator-key"
   $env:AZURE_TRANSLATOR_REGION = "eastus"
   ```

   Or create `.streamlit/secrets.toml`:

   ```toml
   AZURE_SPEECH_KEY = "your-key"
   AZURE_SPEECH_REGION = "eastus"
   AZURE_TRANSLATOR_KEY = "your-translator-key"
   AZURE_TRANSLATOR_REGION = "eastus"
   AZURE_TRANSLATOR_ENDPOINT = "https://api.cognitive.microsofttranslator.com"
   ```

4. Start the app:

   ```powershell
   streamlit run app.py
   ```

The Azure Speech resource must be in a supported region and the region value must match the resource.
