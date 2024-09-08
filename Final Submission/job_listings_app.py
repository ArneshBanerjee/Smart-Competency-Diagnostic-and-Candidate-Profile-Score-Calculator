import streamlit as st
import pandas as pd
import pickle

# Load data
df = pickle.load(open('models/df.pkl', 'rb'))
similarity = pickle.load(open('models/similarity.pkl', 'rb'))

# Recommendation function
def recommendation(title):
    # Ensure the title exists in the DataFrame
    if title not in df['Title'].values:
        return []

    idx = df[df['Title'] == title].index[0]  # Get the index of the job title
    idx = df.index.get_loc(idx)

    # Check that idx is within the bounds of the similarity matrix
    if idx >= len(similarity):
        return []

    # Get similar job recommendations based on the similarity matrix
    distances = sorted(list(enumerate(similarity[idx])), reverse=True, key=lambda x: x[1])[1:20]

    jobs = []
    for i in distances:
        if i[0] < len(df):  # Ensure that the index is valid
            jobs.append(df.iloc[i[0]].Title)

    return jobs

# Streamlit app
st.title('Job Recommendation System')

# Select job title from the DataFrame
title = st.selectbox('Search job', df['Title'])

# Get job recommendations
jobs = recommendation(title)

# Display recommended jobs if any
if jobs:
    st.write(jobs)
else:
    st.write("No similar jobs found.")







'''from flask import Flask, render_template, request
import pandas as pd
import pickle

app = Flask(__name__)

# Load the job titles and the similarity model
df = pd.read_pickle('/path/to/your/new_df.pkl')  # Replace with the correct path
similarity_jobs = pickle.load(open('/path/to/your/new_similarity_job.pkl', 'rb'))  # Replace with the correct path

@app.route('/')
def home():
    job_titles = df['Title'].unique().tolist()
    return render_template('index.html', job_titles=job_titles)

@app.route('/recommend_jobs', methods=['POST'])
def recommend_jobs():
    selected_job = request.form['job_title']
    recommended_jobs = get_recommended_jobs(selected_job)
    return render_template('result.html', selected_job=selected_job, recommended_jobs=recommended_jobs)

def get_recommended_jobs(job_title):
    # Find the index of the job in the dataframe
    job_idx = df[df['Title'] == job_title].index[0]
    
    # Get similarity scores and sort jobs
    similarity_scores = list(enumerate(similarity_jobs[job_idx]))
    similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)[1:6]  # Get top 5
    
    # Fetch recommended job titles
    recommended_jobs = [df['Title'].iloc[i[0]] for i in similarity_scores]
    return recommended_jobs

if __name__ == '__main__':
    app.run(debug=True)'''
