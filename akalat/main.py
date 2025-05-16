import codecs
import json
import os

import requests
from flask import Flask, redirect, render_template, request
from markupsafe import Markup
from openai import OpenAI

app = Flask(__name__)

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])


@app.route("/")
def index():
    return render_template("index.html", theme="dark", placeholder="Search anything...")

@app.route("/search-redirect", methods=["POST"])
def searchRedirect():
    return redirect(f"/search?q={request.form['query'].replace(' ', '%20')}")

@app.route("/search", methods=["GET"])
def search():
    query = request.args["q"]
    
    data = requests.get(f"https://api.search.brave.com/res/v1/web/search?count=20&q={query.replace('%20', '+').replace(' ', '+')}", headers={"X-Subscription-Token": os.environ["BRAVE_SEARCH_API_KEY"]})
    data.encoding = "utf-8"
    jsonData = data.json()
    if jsonData.get("web", ""):
        results = jsonData["web"]["results"]
        fullResponse = []
        credible = ""

        for result in results:
            thumbnail = result.get("thumbnail", {})
            title = result.get("title", "Untitled")
            url = result.get("url", "javascript:void(0)")
            profile = result.get("profile", "")
            description = result.get("description", "")
            
            response = f"""<img src="{thumbnail.get('src', '/static/images/question-mark.svg')}"><br><br>
            <a href={url}><h2>{title}</h2></a>
            <a href={url}>{profile.get('long_name', 'No URL')}</a>
            <p>{description}</p>"""
            fullResponse.append(response)

            if profile.get("long_name", "") == "en.wikipedia.org" or profile.get("long_name", "") == "merriam-webster.com":
                credible = result.get("url", "")

        if not credible and results:
            credible = results[0].get("url", "")

        fullResponse = str(fullResponse).replace("'", "").replace("\\n", "").replace("[", "").replace("]", "").replace(",", "")

        shortBot = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that doesn't ask any questions, but gives reasonable, short definitions and answers to the question posed based on the article(s) given to you in no more than 12 words. If it is not a question, then give the input a definition. If it is a math expression, then answer it."},
                {"role": "user", "content": credible}
            ]
        )

        shortAns = shortBot.choices[0].message.content
        shortAns = str(shortBot.choices[0].message.content) if shortBot.choices and shortBot.choices[0].message and shortBot.choices[0].message.content else "No quick answer, sorry!"

        codecs.decode(str(fullResponse), "unicode_escape")
        
        return render_template("search.html", shortAns=Markup(f"<span style='font-weight: bold; font-size: 15px;'>Quick Answer:</span><br>{shortAns}"), response=Markup(fullResponse), theme="dark", placeholder=query.replace('%20', ' '))
    else:
        return render_template("search.html", response=Markup(f"Oops! We didn't find any results for your search, <b>{query.replace('%20', ' ')}</b>."), theme="dark")
    
if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000)
