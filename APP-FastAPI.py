from fastapi import FastAPI, HTTPException, Form
from fastapi.responses import HTMLResponse
from RAG_News import categorize, get_linksDB, get_news, get_news_GEN, TextSummarizationPipeline

app = FastAPI()

# Route for the homepage
@app.get("/", response_class=HTMLResponse)
async def read_root():
    return """
    <html>
    <head>
        <title>News Summarization App</title>
<style>
    body {
        font-family: Arial, sans-serif;
        background-color: #f4f4f4;
        margin: 0;
        padding: 0;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 100vh;
        font-size: 18px; /* Increase base font size */
    }
    h1 {
        color: #333;
        font-size: 36px; /* Increase heading size */
    }
    form {
        background-color: white;
        padding: 30px; /* Increase padding */
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    label {
        margin-bottom: 15px; /* Adjust margin for better spacing */
        font-weight: bold;
        font-size: 18px; /* Increase label size */
    }
    input[type="text"], select {
        padding: 15px; /* Increase padding for inputs */
        width: 400px; /* Increase width */
        border: 1px solid #ccc;
        border-radius: 5px;
        margin-bottom: 20px;
        font-size: 18px; /* Increase input font size */
    }
    input[type="submit"] {
        padding: 15px 30px; /* Increase button size */
        background-color: #4CAF50;
        color: white;
        border: none;
        border-radius: 5px;
        cursor: pointer;
        font-size: 18px; /* Increase button text size */
    }
    input[type="submit"]:hover {
        background-color: #45a049;
    }
    img {
        width: 200px; /* Increase image size */
        height: 200px;
        border-radius: 50%;
        margin-bottom: 20px;
    }
    .hidden {
        display: none;
    }
</style>

        <script>
            function toggleInputFields() {
                var option = document.getElementById('option').value;
                var keywordInput = document.getElementById('user_prompt');
                var linkInput = document.getElementById('user_link');
                
                // Initially hide both fields
                keywordInput.classList.add('hidden');
                linkInput.classList.add('hidden');
                
                // Show the appropriate input field based on the selection
                if (option === "Search by Keywords") {
                    keywordInput.classList.remove('hidden');
                } else if (option === "Enter a Link") {
                    linkInput.classList.remove('hidden');
                }
            }
            
            // Ensure input field visibility is set correctly on page load
            window.onload = toggleInputFields;
        </script>
    </head>
    <body>
        <h1>📰 News Summarization App</h1>
        <img src="https://r2.erweima.ai/i/EJJ5qsqnSX-l5xsDwWN1SQ.png" alt="News Logo">
        <form action="/summarize" method="post">
            <label for="option">How would you like to summarize news?</label>
            <select name="option" id="option" onchange="toggleInputFields()">
                <option value="Search by Keywords">Search by Keywords 🔍</option>
                <option value="Enter a Link">Enter a Link 🌐</option>
            </select>

            <label for="user_prompt" class="hidden">Enter Search Keywords:</label>
            <input type="text" id="user_prompt" name="user_prompt" placeholder="e.g., AI in healthcare" class="hidden">

            <label for="user_link" class="hidden">Or Enter a Web Link:</label>
            <input type="text" id="user_link" name="user_link" placeholder="e.g., https://example.com/news-article" class="hidden">
            
            <input type="submit" value="🔎 Summarize News">
        </form>
    </body>
    </html>
    """

@app.post("/summarize", response_class=HTMLResponse)
async def summarize_news(option: str = Form(...), user_prompt: str = Form(None), user_link: str = Form(None)):
    if option == "Search by Keywords" and user_prompt:
        model_name = 'meta/meta-llama-3-8b-instruct'
        category = categorize(user_prompt, model_name)

        if category is None:
            category = "General"

        allowed_categories = ['Technology', 'Science', 'Health', 'Sports']

        if category not in allowed_categories:
            links = get_linksDB(category, user_prompt)
            if not links:
                return HTMLResponse("""
                    <html>
                        <head><title>No News Found</title></head>
                        <body>
                            <h1>No related news found.</h1>
                            <a href='/'>Go Back</a>
                        </body>
                    </html>
                """)
            summarizer = TextSummarizationPipeline()
            summaries = []

            for link in links:
                news_content = get_news_GEN(link, user_prompt)

                # Ensure news_content is a string
                if isinstance(news_content, list):
                    news_content = ' '.join(news_content)  # Join list into a single string
                
                summary = summarizer.generate_summary(news_content)
                summaries.append({"article": "", "summary": summary[0]['generated_text']})
                break
        else:
            links = get_linksDB(category, user_prompt)
            if not links:
                return HTMLResponse("""
                    <html>
                        <head><title>No News Found</title></head>
                        <body>
                            <h1>No related news found.</h1>
                            <a href='/'>Go Back</a>
                        </body>
                    </html>
                """)
            summarizer = TextSummarizationPipeline()
            summaries = []

            for link in links:
                news_content = get_news(link)

                # Ensure news_content is a string
                if isinstance(news_content, list):
                    news_content = ' '.join(news_content)  # Join list into a single string
                
                summary = summarizer.generate_summary(news_content)
                summaries.append({"article": link, "summary": summary[0]['generated_text']})

        categorized_title_html = f"<h2>Your prompt is categorized under: <strong>{category if category else 'General'}</strong></h2>"

    elif option == "Enter a Link" and user_link:
        news_content = get_news(user_link)
        
        # Ensure news_content is a string
        if isinstance(news_content, list):
            news_content = ' '.join(news_content)  # Join list into a single string

        if news_content:
            summarizer = TextSummarizationPipeline()
            summary = summarizer.generate_summary(news_content)
            summaries = [{"article": user_link, "summary": summary[0]['generated_text']}]
            categorized_title_html = ""  # No category title for direct links
        else:
            return HTMLResponse("""
                <html>
                    <head><title>Error</title></head>
                    <body>
                        <h1>Failed to retrieve content from the link.</h1>
                        <a href='/'>Go Back</a>
                    </body>
                </html>
            """)

    else:
        return HTMLResponse("""
            <html>
                <head><title>Error</title></head>
                <body>
                    <h1>Please enter valid keywords or a link.</h1>
                    <a href='/'>Go Back</a>
                </body>
            </html>
        """)

    summaries_html = "<br>".join([f"<div class='summary-container'><h2>Article: <a href='{s['article']}'>{s['article']}</a></h2><p>{s['summary']}</p></div>" for s in summaries])

    return f"""
    <html>
        <head>
            <title>News Summaries</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f4;
                    margin: 0;
                    padding: 20px;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                }}
                h1 {{
                    color: #333;
                }}
                .summary-container {{
                    margin: 20px;
                    padding: 20px;
                    background-color: white;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
                    max-width: 600px;
                }}
                .summary-container h2 {{
                    color: #4CAF50;
                }}
                .summary-container p {{
                    color: #333;
                    line-height: 1.6;
                }}
                a {{
                    text-decoration: none;
                    color: #4CAF50;
                }}
            </style>
        </head>
        <body>
            <h1>News Summarization Results</h1>
            {categorized_title_html}
            {summaries_html}
            <a href='/'>Go Back</a>
        </body>
    </html>
    """

