import streamlit as st
import os
from RAG_News import categorize, get_linksDB, get_news, get_news_GEN, TextSummarizationPipeline

# Page Title
st.title("📰 News Summarization App")
st.write("Easily summarize news articles based on keywords or by providing a link.")

# Add space for better UI separation
st.write("---")

# Option for users to choose between searching keywords or providing a link
st.subheader("Select an Option:")
option = st.selectbox(
    "How would you like to summarize news?",
    ("Search by Keywords 🔍", "Enter a Web Link 🌐")
)

st.write("")  # Add a little space for better readability

# Input area based on user's choice
if option == "Search by Keywords 🔍":
    user_prompt = st.text_input("Enter your search keywords below:", placeholder="e.g., AI in healthcare")
    user_link = None  # Reset the link input when using keywords

elif option == "Enter a Web Link 🌐":
    user_link = st.text_input("Enter a web link below:", placeholder="e.g., https://example.com/news-article")
    user_prompt = None  # Reset the keyword input when using a link

st.write("")  # Another small space before the button

# Summarize button
if st.button("🔎 Summarize News"):
    if option == "Search by Keywords 🔍" and user_prompt:
        # Categorize the input
        model_name = 'meta/meta-llama-3-8b-instruct'
        category = categorize(user_prompt, model_name)
        st.write(f"🗂️ Your prompt is categorized under: {category if category else 'General'}")

        # Use a default category if categorization fails
        if category is None:
            category = "General"  # or any default category you want to use

        # Define the allowed categories
        allowed_categories = ['Technology', 'Science', 'Health', 'Sports']

        # Check if the category is one of the allowed categories
        if category not in allowed_categories:
            links = get_linksDB(category, user_prompt)
            if not links:
                st.write("⚠️ No related news found.")
            else:
                summarizer = TextSummarizationPipeline()

                # Display summaries
                for link in links:
                    # Pass user_prompt to get_news
                    news_content = get_news_GEN(link, user_prompt)

                    summary = summarizer.generate_summary(news_content)
                    st.write(summary[0]['generated_text'])
                    st.write("---")
                    break
        else:
            # Retrieve news links
            links = get_linksDB(category, user_prompt)
            if not links:
                st.write("⚠️ No related news found.")
            else:
                summarizer = TextSummarizationPipeline()

                # Display summaries
                for link in links:
                    # Pass user_prompt to get_news
                    news_content = get_news(link)

                    summary = summarizer.generate_summary(news_content)
                    st.write(f"🔗 [Read Article]({link})")
                    st.write(summary[0]['generated_text'])
                    st.write("---")

    elif option == "Enter a Web Link 🌐" and user_link:
        # Summarize content from the user-provided link
        news_content = get_news(user_link)
        if news_content:
            summarizer = TextSummarizationPipeline()
            summary = summarizer.generate_summary(news_content)
            st.write(f"🔗 [Read Article]({user_link})")
            st.write(summary[0]['generated_text'])
            st.write("---")
        else:
            st.write("⚠️ Failed to retrieve content from the link.")
    else:
        st.write("⚠️ Please enter valid keywords or a link.")
