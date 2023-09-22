import streamlit as st
import openai
import tiktoken
import re

encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")

# Streamlit config
st.set_page_config(
    page_title="Call Analysis",
    layout='wide',
    page_icon="musical_note",
    menu_items={
         'About': 'Call Kevin MAMERI',
     }
)

# Set page title, header and links to docs
st.header("🗣 Call analysis POC using Python, Streamlit and OpenAI✨")
st.caption(f"App developed by IntescIA ;)")

# Let the user input the OPENAI_API_KEY
openai_api_key = st.text_input("Please enter your OPENAI_API_KEY", type="password")

if openai_api_key:
    openai.api_key = openai_api_key
else:
    st.warning("Please enter your OPENAI_API_KEY to proceed.")
    st.stop()

upload_path = "upload_path/"

st.markdown("""---""")
st.subheader("Upload The Audio File or Text File Below")
uploaded_file = st.file_uploader("Choose a file", accept_multiple_files=False, type=["wav", "mp3", "txt"], label_visibility='hidden')

if uploaded_file is not None:
    file_name = uploaded_file.name
    file_path = f"./{file_name}"

    if file_name.endswith(".txt"):
        with st.spinner(f"Processing Text File ... 💫"):
            file_contents = uploaded_file.read().decode("utf-8")
            user_input = file_contents
    else:
        with st.spinner(f"Processing Audio ... 💫"):
            audio_bytes = uploaded_file.read()
            with open(file_path, "wb") as f:
                f.write(audio_bytes)

            with open(file_path, "rb") as audio_file:
                transcribe = openai.Audio.transcribe(audio_file)
                user_input = transcribe.text

        st.title("Generated Original Text 🔊")
        st.write(user_input)

    # Retirer les uuid du texte
    uuid_pattern = r'\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b\s'
    user_input = re.sub(uuid_pattern, "", user_input)

    # Réduire la longueur du texte si nécessaire
    max_tokens = 16_000  # Définir une limite pour éviter de dépasser la limite de tokens du modèle
    encoded_user_input = encoding.encode(user_input)
    if len(encoded_user_input) > max_tokens:
        user_input = encoding.decode(encoded_user_input[:max_tokens])
        st.warning("Le texte dépasse la limite maximale de tokens du modèle. Il a été tronqué à 16 000 tokens.")

    with st.spinner(f"Processing Text ... 💫"):
        model = "gpt-3.5-turbo-16k"
        system_input = "Tu es le directeur général d'un grand éditeur SAAS, tu dois analyser la démo de notre commercial avec un prospect qui présente notre applicatif, ta réponse dont contenir 3 parties : 1_Les points positifs de cet échange. 2_Les points à améliorer dans sa présentation. 3_ Les fonctionnalités qu'on pourrait développer."
        res = openai.ChatCompletion.create(
          model=model,
          messages=[
                {"role": "system", "content": system_input},
                {"role": "user", "content": user_input},
            ]
        )
        st.title("Generated analysis 🔊")
        st.write(res.choices[0].message.content)
