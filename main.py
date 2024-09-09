import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

try:
    from openai import OpenAI

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def get_completion(prompt):
        completion = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful movie recommendation assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        return completion.choices[0].message.content
except ImportError:
    import openai
    openai.api_key = os.getenv("OPENAI_API_KEY")
    def get_completion(prompt):
        completion = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful movie recommendation assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        return completion.choices[0].message['content']

st.set_page_config(page_title="Movie Recommender", page_icon="🎬", layout="wide")

st.markdown("""
    <style>
    .big-font {
        font-size:30px !important;
        font-weight: bold;
    }
    .medium-font {
        font-size:20px !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<p class="big-font">🎬 Movie Recommendation System</p>', unsafe_allow_html=True)

st.markdown('<p class="medium-font">How Does It Work?</p>', unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.write("1️⃣ Select your favorite movie genres")
with col2:
    st.write("2️⃣ Specify your top 3 favorite movies")
with col3:
    st.write("3️⃣ Click 'Get Recommendations'")
with col4:
    st.write("4️⃣ Enjoy personalized movie recommendations!")

genres = ["Action", "Comedy", "Drama", "Science Fiction", "Horror", "Animated", "Historical", "Musical", "Thriller",
          "Romance"]
selected_genres = st.multiselect("Select Your Favorite Movie Genres", genres)

st.subheader("Your Top 3 Favorite Movies")
favorite_movies = []
cols = st.columns(3)
for i, col in enumerate(cols):
    with col:
        movie = st.text_input(f"Movie {i + 1}", key=f"movie_{i}")
        favorite_movies.append(movie)

if st.button("Get Recommendations", key="recommend"):
        prompt = f"""Based on the following information:
        Favorite genres: {', '.join(selected_genres)}
        Favorite movies: {', '.join(favorite_movies)}

        Please recommend 3 movies. Provide the recommendations in a table format with the following columns:            Name of Movie | Type | Short Summary

        Give the response in English language. Keep the summaries concise, about 20-30 words each.
        The output should be in a format that can be easily converted to a pandas DataFrame.
        """

        recommendations = get_completion(prompt)

        st.subheader("Recommended Movies")
        try:
            if recommendations.strip().startswith("|"):
                st.markdown(recommendations)
            else:
                st.error("The AI did not return a properly formatted table. Please try again.")
        except Exception as e:
            st.error(f"Sorry, there was an error processing the recommendations: {e}")

st.markdown("---")
st.markdown("❤️️️️ Enjoy the movie ❤️")