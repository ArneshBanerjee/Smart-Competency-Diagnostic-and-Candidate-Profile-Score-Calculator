
from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import resume_parsing_app
import job_listings_app
import course_recommendation_app

app = Flask(__name__)

# Route for uploading resume and parsing it
@app.route('/', methods=['GET', 'POST'])
def upload_resume():
    if request.method == 'POST':
        if 'resume' not in request.files:
            return 'No file part'
        file = request.files['resume']
        if file.filename == '':
            return 'No selected file'
        if file:
            file_path = os.path.join('uploads', file.filename)
            file.save(file_path)

            # Extract information from the resume
            parsed_data = resume_parsing_app.parse_resume(file_path)

            # Debugging
            print(parsed_data)  # Check the content of parsed_data

            # Redirect to homepage with parsed data
            return redirect(url_for('home', job_title=parsed_data.get('job_title')))

    return render_template('resume.html')

# Route for the homepage with dropdown filter
@app.route('/home', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        selected_option = request.form['filter']
        job_title = request.form['job_title']

        if selected_option == 'job':
            recommended_jobs = job_listings_app.recommend_jobs(job_title)
            return jsonify(recommended_jobs=recommended_jobs)
        elif selected_option == 'course':
            recommended_courses = course_recommendation_app.recommend_courses(job_title)
            return jsonify(recommended_courses=recommended_courses)

    job_title = request.args.get('job_title', '')
    return render_template('home.html', job_title=job_title)

if __name__ == '__main__':
    app.run(debug=True)
