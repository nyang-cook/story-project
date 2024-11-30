import os
import openai
from audio_recorder_streamlit import audio_recorder
import streamlit as st
from gtts import gTTS
import base64


# OpenAI 클라이언트 생성
client = openai.OpenAI(api_key="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")  # API 키 입력


# 음성을 텍스트로 변환하는 함수 (STT)
def STT(audio_data):
    filename = 'input.mp3'
    with open(filename, "wb") as f:
        f.write(audio_data)
    
    try:
        with open(filename, "rb") as audio_file:
            response = client.audio.transcriptions.create(
                file=audio_file,
                model="whisper-1",
                response_format="text"
            )
        transcript = response
    except Exception as e:
        transcript = f"STT 변환 중 오류 발생: {e}"
    finally:
        if os.path.exists(filename):
            os.remove(filename)
    
    return transcript


# 텍스트를 음성으로 변환하는 함수 (TTS)
def TTS(text):
    try:
        tts = gTTS(text, lang="ko")
        filename = "output.mp3"
        tts.save(filename)

        with open(filename, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            md = f"""
                <audio autoplay="true" controls>
                <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                </audio>
                """
            st.markdown(md, unsafe_allow_html=True)

        os.remove(filename)
    except Exception as e:
        st.error(f"TTS 변환 중 오류 발생: {e}")


# ChatGPT를 활용해 동화 내용을 생성하는 함수
def ask_gpt(prompt):
    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "너는 동화 작가야!, 장면당 2-3줄의 동화를 써줘."},
                {"role": "user", "content": prompt}
            ],
            model="gpt-4o-mini"
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"ChatGPT 호출 중 오류 발생: {e}"


# DALL-E를 활용해 동화 내용을 그림으로 생성하는 함수
def generate_image(prompt):
    try:
        response = client.images.generate(
            model = "dall-e-2",
            prompt=prompt,
            n=1,
            size="512x512"  # 원하는 이미지 크기 설정
        )
        image_url = response.data[0].url
        return image_url
    except Exception as e:
        return f"이미지 생성 중 오류 발생: {e}"


# 메인 함수
def main():
    st.title("AI 기반 동화 생성기 🎨📖🎤")

    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    if "last_audio" not in st.session_state:
        st.session_state["last_audio"] = None

    st.header("음성 입력 방식 선택")
    input_mode = st.radio(
        "음성 입력 방식을 선택하세요:",
        ("녹음", "파일 업로드")
    )

    if input_mode == "녹음":
        st.subheader("음성 녹음")
        audio_data = audio_recorder(text="녹음 버튼을 눌러 음성을 입력하세요!")

        if audio_data:
            if audio_data != st.session_state["last_audio"]:
                st.session_state["last_audio"] = audio_data

                with st.spinner("음성을 텍스트로 변환 중..."):
                    user_input = STT(audio_data)
                st.write(f"🎤 변환된 텍스트: **{user_input}**")

                with st.spinner("동화를 생성 중..."):
                    story = ask_gpt(user_input)
                st.markdown(f"📖 생성된 동화:\n\n{story}")

                with st.spinner("동화를 음성으로 변환 중..."):
                    TTS(story)

                with st.spinner("동화를 그림으로 변환 중..."):
                    image_url = generate_image(story)
                    if "오류 발생" not in image_url:
                        st.image(image_url, caption="DALL-E가 생성한 동화 삽화")
                    else:
                        st.error(image_url)
            else:
                st.info("새로운 음성을 녹음해주세요.")
        else:
            st.info("음성을 녹음하고 결과를 확인하세요!")
    
    elif input_mode == "파일 업로드":
        st.subheader("음성 파일 업로드")
        uploaded_file = st.file_uploader("음성 파일을 업로드하세요 (MP3 형식)", type=["mp3"])

        if uploaded_file is not None:
            audio_data = uploaded_file.read()

            with st.spinner("음성을 텍스트로 변환 중..."):
                user_input = STT(audio_data)
            st.write(f"🎤 변환된 텍스트: **{user_input}**")

            with st.spinner("동화를 생성 중..."):
                story = ask_gpt(user_input)
            st.markdown(f"📖 생성된 동화:\n\n{story}")

            with st.spinner("동화를 음성으로 변환 중..."):
                TTS(story)

            with st.spinner("동화를 그림으로 변환 중..."):
                image_url = generate_image(story)
                if "오류 발생" not in image_url:
                    st.image(image_url, caption="DALL-E가 생성한 동화 삽화")
                else:
                    st.error(image_url)


if __name__ == "__main__":
    main()