
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from textblob import TextBlob
import numpy as np
import re
from collections import Counter
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import scipy.stats as stats

# Load Data
df = pd.read_csv("data/comments_likes.csv")

# Data Cleaning: Remove special characters and convert to lowercase
def clean_text(text):
    text = re.sub(r"[^a-zA-Z0-9\s]", "", str(text))
    return text.lower()

df["clean_comment"] = df["comment"].apply(clean_text)

#Likes Distribution Analysis
plt.figure(figsize=(8, 5))
sns.histplot(df["likes"], bins=50, kde=True)
plt.title("Likes Distribution of Comments")
plt.xlabel("Number of Likes")
plt.ylabel("Frequency")
plt.yscale("log")  # Log scale to better visualize distribution
plt.savefig("visuals/likes_distribution.png")
plt.close()

#Sentiment Analysis Using TextBlob
def get_sentiment(text):
    return TextBlob(text).sentiment.polarity

df["sentiment_score"] = df["clean_comment"].apply(get_sentiment)

#Classify sentiment into categories
df["sentiment"] = df["sentiment_score"].apply(
    lambda x: "Positive" if x > 0.1 else ("Negative" if x < -0.1 else "Neutral")
)

#Sentiment Distribution
sentiment_counts = df["sentiment"].value_counts()
plt.figure(figsize=(6, 4))
sns.barplot(x=sentiment_counts.index, y=sentiment_counts.values, palette="coolwarm")
plt.title("Sentiment Distribution of Comments")
plt.xlabel("Sentiment")
plt.ylabel("Number of Comments")
plt.savefig("visuals/sentiment_distribution.png")
plt.close()

#Word Frequency Analysis & Word Cloud
words = " ".join(df["clean_comment"])
wordcloud = WordCloud(width=800, height=400, background_color="white").generate(words)

plt.figure(figsize=(10, 5))
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")
plt.title("Word Cloud of Most Common Words")
plt.savefig("visuals/word_cloud.png")
plt.close()

#Topic Modeling (LDA)
vectorizer = CountVectorizer(stop_words="english", max_features=1000)
X = vectorizer.fit_transform(df["clean_comment"])

lda_model = LatentDirichletAllocation(n_components=3, random_state=42)
lda_model.fit(X)

# Extract Top Words per Topic
def get_top_words(model, feature_names, n_top_words):
    topics = []
    for topic_idx, topic in enumerate(model.components_):
        top_words = [feature_names[i] for i in topic.argsort()[:-n_top_words - 1:-1]]
        topics.append(", ".join(top_words))
    return topics

top_words_per_topic = get_top_words(lda_model, vectorizer.get_feature_names_out(), 10)

topics_df = pd.DataFrame({
    "Topic": range(1, 4),
    "Top Keywords": top_words_per_topic
})

#Save Topic Modeling as Image
plt.figure(figsize=(8, 5))
topics_df.set_index("Topic")["Top Keywords"].str.split(", ").apply(len).plot(kind="bar", color="purple", alpha=0.7)
plt.xlabel("Topic")
plt.ylabel("Number of Keywords")
plt.title("LDA Topic Distribution")
plt.savefig("visuals/topic_modeling.png")
plt.close()

#Comment Length vs Likes Correlation
df["comment_length"] = df["clean_comment"].apply(len)

plt.figure(figsize=(8, 5))
sns.scatterplot(x=df["comment_length"], y=df["likes"], alpha=0.5)
plt.title("Comment Length vs Number of Likes")
plt.xlabel("Comment Length")
plt.ylabel("Number of Likes")
plt.yscale("log")
plt.savefig("visuals/comment_length_vs_likes.png")
plt.close()

#Compute Correlations
sentiment_vs_likes_corr = stats.spearmanr(df["sentiment_score"], df["likes"]).correlation
comment_length_vs_likes_corr = stats.spearmanr(df["comment_length"], df["likes"]).correlation

#Display Results
print(f"Sentiment Score vs. Likes Correlation: {sentiment_vs_likes_corr:.3f}")
print(f"Comment Length vs. Likes Correlation: {comment_length_vs_likes_corr:.3f}")

#Save Results as CSV
df.to_csv("processed_comments_sentiment.csv", index=False)
topics_df.to_csv("lda_topics.csv", index=False)
