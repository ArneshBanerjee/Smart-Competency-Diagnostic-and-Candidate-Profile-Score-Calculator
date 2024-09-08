from flask import Flask, request, render_template
from PyPDF2 import PdfReader
import re
import pickle
from flask import redirect, url_for
from werkzeug.utils import secure_filename
import os
import json
from flask import flash



resume_data = {
    'name': None,
    'phone': None,
    'email': None,
    'education': None,
    'skills': None,
    'internships_experience': [],  # Already initialized
    'achievements': [],  # Initialize the achievements key with an empty list
}


user_scores = {}

users = []

app = Flask(__name__)
app.secret_key = 'supersecretkey'

#loading models
rf_classifier_categorization = pickle.load(open('models/rf_classifier_categorization.pkl', 'rb'))
tfidf_vectorizer_categorization = pickle.load(open('models/tfidf_vectorizer_categorization.pkl', 'rb'))
rf_classifier_job_recomendation = pickle.load(open('models/rf_classifier_job_recommendation.pkl', 'rb'))
tfidf_vectorizer_job_recommendation = pickle.load(open('models/tfidf_vectorizer_job_recommendation.pkl', 'rb'))

#job recommendation models
df = pickle.load(open('models/df.pkl', 'rb'))
similarity_job = pickle.load(open('models/similarity_job.pkl', 'rb'))

#course recommendation models
courses_list = pickle.load(open('models/courses.pkl','rb'))
similarity = pickle.load(open('models/similarity.pkl','rb'))

min_size = min(df.shape[0], similarity_job.shape[0]) #CHANGE 1

# Truncate df to match similarity_job if necessary
df = df.iloc[:min_size].reset_index(drop=True) #CHANGE 2

# Truncate similarity_job to match df
similarity_job = similarity_job[:min_size, :min_size] #CHANGE 3


#cleaning resume
def cleanResume(txt):
    cleanText = re.sub('http\S+\s', ' ', txt)
    cleanText = re.sub('RT|cc', ' ', cleanText)
    cleanText = re.sub('#\S+\s', ' ', cleanText)
    cleanText = re.sub('@\S+', '  ', cleanText)
    cleanText = re.sub('[%s]' % re.escape("""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""), ' ', cleanText)
    cleanText = re.sub(r'[^\x00-\x7f]', ' ', cleanText)
    cleanText = re.sub('\s+', ' ', cleanText)
    return cleanText

def predict_category(resume_text):
    resume_text = cleanResume(resume_text)
    resume_tfidf = tfidf_vectorizer_categorization.transform([resume_text])
    predicted_category = rf_classifier_categorization.predict(resume_tfidf)[0]
    return predicted_category

def job_recommendation(resume_text):
    resume_text= cleanResume(resume_text)
    resume_tfidf = tfidf_vectorizer_job_recommendation.transform([resume_text])
    recommended_job = rf_classifier_job_recomendation.predict(resume_tfidf)[0]
    return recommended_job


def pdf_to_text(file):
    reader = PdfReader(file)
    text = ''
    for page in range(len(reader.pages)):
        text += reader.pages[page].extract_text()
    return text



def extract_contact_number_from_resume(text):
    contact_number = None

    # regex pattern used
    pattern = r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"
    match = re.search(pattern, text)
    if match:
        contact_number = match.group()

    return contact_number
def extract_email_from_resume(text):
    email = None

    pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
    match = re.search(pattern, text)
    if match:
        email = match.group()

    return email

def extract_skills_from_resume(text):
    #predefined skillsl
    skills_list = [
        'Python', 'Data Analysis', 'Machine Learning', 'Communication', 'Project Management', 'Deep Learning', 'SQL',
        'Tableau',
        'Java', 'C++', 'JavaScript', 'HTML', 'CSS', 'React', 'Angular', 'Node.js', 'MongoDB', 'Express.js', 'Git',
        'Research', 'Statistics', 'Quantitative Analysis', 'Qualitative Analysis', 'SPSS', 'R', 'Data Visualization',
        'Matplotlib',
        'Seaborn', 'Plotly', 'Pandas', 'Numpy', 'Scikit-learn', 'TensorFlow', 'Keras', 'PyTorch', 'NLTK', 'Text Mining',
        'Natural Language Processing', 'Computer Vision', 'Image Processing', 'OCR', 'Speech Recognition',
        'Recommendation Systems',
        'Collaborative Filtering', 'Content-Based Filtering', 'Reinforcement Learning', 'Neural Networks',
        'Convolutional Neural Networks',
        'Recurrent Neural Networks', 'Generative Adversarial Networks', 'XGBoost', 'Random Forest', 'Decision Trees',
        'Support Vector Machines',
        'Linear Regression', 'Logistic Regression', 'K-Means Clustering', 'Hierarchical Clustering', 'DBSCAN',
        'Association Rule Learning',
        'Apache Hadoop', 'Apache Spark', 'MapReduce', 'Hive', 'HBase', 'Apache Kafka', 'Data Warehousing', 'ETL',
        'Big Data Analytics',
        'Cloud Computing', 'Amazon Web Services (AWS)', 'Microsoft Azure', 'Google Cloud Platform (GCP)', 'Docker',
        'Kubernetes', 'Linux',
        'Shell Scripting', 'Cybersecurity', 'Network Security', 'Penetration Testing', 'Firewalls', 'Encryption',
        'Malware Analysis',
        'Digital Forensics', 'CI/CD', 'DevOps', 'Agile Methodology', 'Scrum', 'Kanban', 'Continuous Integration',
        'Continuous Deployment',
        'Software Development', 'Web Development', 'Mobile Development', 'Backend Development', 'Frontend Development',
        'Full-Stack Development',
        'UI/UX Design', 'Responsive Design', 'Wireframing', 'Prototyping', 'User Testing', 'Adobe Creative Suite',
        'Photoshop', 'Illustrator',
        'InDesign', 'Figma', 'Sketch', 'Zeplin', 'InVision', 'Product Management', 'Market Research',
        'Customer Development', 'Lean Startup',
        'Business Development', 'Sales', 'Marketing', 'Content Marketing', 'Social Media Marketing', 'Email Marketing',
        'SEO', 'SEM', 'PPC',
        'Google Analytics', 'Facebook Ads', 'LinkedIn Ads', 'Lead Generation', 'Customer Relationship Management (CRM)',
        'Salesforce',
        'HubSpot', 'Zendesk', 'Intercom', 'Customer Support', 'Technical Support', 'Troubleshooting',
        'Ticketing Systems', 'ServiceNow',
        'ITIL', 'Quality Assurance', 'Manual Testing', 'Automated Testing', 'Selenium', 'JUnit', 'Load Testing',
        'Performance Testing',
        'Regression Testing', 'Black Box Testing', 'White Box Testing', 'API Testing', 'Mobile Testing',
        'Usability Testing', 'Accessibility Testing',
        'Cross-Browser Testing', 'Agile Testing', 'User Acceptance Testing', 'Software Documentation',
        'Technical Writing', 'Copywriting',
        'Editing', 'Proofreading', 'Content Management Systems (CMS)', 'WordPress', 'Joomla', 'Drupal', 'Magento',
        'Shopify', 'E-commerce',
        'Payment Gateways', 'Inventory Management', 'Supply Chain Management', 'Logistics', 'Procurement',
        'ERP Systems', 'SAP', 'Oracle',
        'Microsoft Dynamics', 'Tableau', 'Power BI', 'QlikView', 'Looker', 'Data Warehousing', 'ETL',
        'Data Engineering', 'Data Governance',
        'Data Quality', 'Master Data Management', 'Predictive Analytics', 'Prescriptive Analytics',
        'Descriptive Analytics', 'Business Intelligence',
        'Dashboarding', 'Reporting', 'Data Mining', 'Web Scraping', 'API Integration', 'RESTful APIs', 'GraphQL',
        'SOAP', 'Microservices',
        'Serverless Architecture', 'Lambda Functions', 'Event-Driven Architecture', 'Message Queues', 'GraphQL',
        'Socket.io', 'WebSockets'
                     'Ruby', 'Ruby on Rails', 'PHP', 'Symfony', 'Laravel', 'CakePHP', 'Zend Framework', 'ASP.NET', 'C#',
        'VB.NET', 'ASP.NET MVC', 'Entity Framework',
        'Spring', 'Hibernate', 'Struts', 'Kotlin', 'Swift', 'Objective-C', 'iOS Development', 'Android Development',
        'Flutter', 'React Native', 'Ionic',
        'Mobile UI/UX Design', 'Material Design', 'SwiftUI', 'RxJava', 'RxSwift', 'Django', 'Flask', 'FastAPI',
        'Falcon', 'Tornado', 'WebSockets',
        'GraphQL', 'RESTful Web Services', 'SOAP', 'Microservices Architecture', 'Serverless Computing', 'AWS Lambda',
        'Google Cloud Functions',
        'Azure Functions', 'Server Administration', 'System Administration', 'Network Administration',
        'Database Administration', 'MySQL', 'PostgreSQL',
        'SQLite', 'Microsoft SQL Server', 'Oracle Database', 'NoSQL', 'MongoDB', 'Cassandra', 'Redis', 'Elasticsearch',
        'Firebase', 'Google Analytics',
        'Google Tag Manager', 'Adobe Analytics', 'Marketing Automation', 'Customer Data Platforms', 'Segment',
        'Salesforce Marketing Cloud', 'HubSpot CRM',
        'Zapier', 'IFTTT', 'Workflow Automation', 'Robotic Process Automation (RPA)', 'UI Automation',
        'Natural Language Generation (NLG)',
        'Virtual Reality (VR)', 'Augmented Reality (AR)', 'Mixed Reality (MR)', 'Unity', 'Unreal Engine', '3D Modeling',
        'Animation', 'Motion Graphics',
        'Game Design', 'Game Development', 'Level Design', 'Unity3D', 'Unreal Engine 4', 'Blender', 'Maya',
        'Adobe After Effects', 'Adobe Premiere Pro',
        'Final Cut Pro', 'Video Editing', 'Audio Editing', 'Sound Design', 'Music Production', 'Digital Marketing',
        'Content Strategy', 'Conversion Rate Optimization (CRO)',
        'A/B Testing', 'Customer Experience (CX)', 'User Experience (UX)', 'User Interface (UI)', 'Persona Development',
        'User Journey Mapping', 'Information Architecture (IA)',
        'Wireframing', 'Prototyping', 'Usability Testing', 'Accessibility Compliance', 'Internationalization (I18n)',
        'Localization (L10n)', 'Voice User Interface (VUI)',
        'Chatbots', 'Natural Language Understanding (NLU)', 'Speech Synthesis', 'Emotion Detection',
        'Sentiment Analysis', 'Image Recognition', 'Object Detection',
        'Facial Recognition', 'Gesture Recognition', 'Document Recognition', 'Fraud Detection',
        'Cyber Threat Intelligence', 'Security Information and Event Management (SIEM)',
        'Vulnerability Assessment', 'Incident Response', 'Forensic Analysis', 'Security Operations Center (SOC)',
        'Identity and Access Management (IAM)', 'Single Sign-On (SSO)',
        'Multi-Factor Authentication (MFA)', 'Blockchain', 'Cryptocurrency', 'Decentralized Finance (DeFi)',
        'Smart Contracts', 'Web3', 'Non-Fungible Tokens (NFTs)']


    skills = []

    for skill in skills_list:
        pattern = r"\b{}\b".format(re.escape(skill))
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            skills.append(skill)

    return skills


def extract_education_from_resume(text):
    education = []

    education_keywords = [
        'Computer Science', 'Information Technology', 'Software Engineering', 'Electrical Engineering', 'Mechanical Engineering', 'Civil Engineering',
        'Chemical Engineering', 'Biomedical Engineering', 'Aerospace Engineering', 'Nuclear Engineering', 'Industrial Engineering', 'Systems Engineering',
        'Environmental Engineering', 'Petroleum Engineering', 'Geological Engineering', 'Marine Engineering', 'Robotics Engineering', 'Biotechnology',
        'Biochemistry', 'Microbiology', 'Genetics', 'Molecular Biology', 'Bioinformatics', 'Neuroscience', 'Biophysics', 'Biostatistics', 'Pharmacology',
        'Physiology', 'Anatomy', 'Pathology', 'Immunology', 'Epidemiology', 'Public Health', 'Health Administration', 'Nursing', 'Medicine', 'Dentistry',
        'Pharmacy', 'Veterinary Medicine', 'Medical Technology', 'Radiography', 'Physical Therapy', 'Occupational Therapy', 'Speech Therapy', 'Nutrition',
        'Sports Science', 'Kinesiology', 'Exercise Physiology', 'Sports Medicine', 'Rehabilitation Science', 'Psychology', 'Counseling', 'Social Work',
        'Sociology', 'Anthropology', 'Criminal Justice', 'Political Science', 'International Relations', 'Economics', 'Finance', 'Accounting', 'Business Administration',
        'Management', 'Marketing', 'Entrepreneurship', 'Hospitality Management', 'Tourism Management', 'Supply Chain Management', 'Logistics Management',
        'Operations Management', 'Human Resource Management', 'Organizational Behavior', 'Project Management', 'Quality Management', 'Risk Management',
        'Strategic Management', 'Public Administration', 'Urban Planning', 'Architecture', 'Interior Design', 'Landscape Architecture', 'Fine Arts',
        'Visual Arts', 'Graphic Design', 'Fashion Design', 'Industrial Design', 'Product Design', 'Animation', 'Film Studies', 'Media Studies',
        'Communication Studies', 'Journalism', 'Broadcasting', 'Creative Writing', 'English Literature', 'Linguistics', 'Translation Studies',
        'Foreign Languages', 'Modern Languages', 'Classical Studies', 'History', 'Archaeology', 'Philosophy', 'Theology', 'Religious Studies',
        'Ethics', 'Education', 'Early Childhood Education', 'Elementary Education', 'Secondary Education', 'Special Education', 'Higher Education',
        'Adult Education', 'Distance Education', 'Online Education', 'Instructional Design', 'Curriculum Development'
        'Library Science', 'Information Science', 'Computer Engineering', 'Software Development', 'Cybersecurity', 'Information Security',
        'Network Engineering', 'Data Science', 'Data Analytics', 'Business Analytics', 'Operations Research', 'Decision Sciences',
        'Human-Computer Interaction', 'User Experience Design', 'User Interface Design', 'Digital Marketing', 'Content Strategy',
        'Brand Management', 'Public Relations', 'Corporate Communications', 'Media Production', 'Digital Media', 'Web Development',
        'Mobile App Development', 'Game Development', 'Virtual Reality', 'Augmented Reality', 'Blockchain Technology', 'Cryptocurrency',
        'Digital Forensics', 'Forensic Science', 'Criminalistics', 'Crime Scene Investigation', 'Emergency Management', 'Fire Science',
        'Environmental Science', 'Climate Science', 'Meteorology', 'Geography', 'Geomatics', 'Remote Sensing', 'Geoinformatics',
        'Cartography', 'GIS (Geographic Information Systems)', 'Environmental Management', 'Sustainability Studies', 'Renewable Energy',
        'Green Technology', 'Ecology', 'Conservation Biology', 'Wildlife Biology', 'Zoology']

    for keyword in education_keywords:
        pattern = r"(?i)\b{}\b".format(re.escape(keyword))
        match = re.search(pattern, text)
        if match:
            education.append(match.group())

    return education

def extract_name_from_resume(text):
    name = None

    pattern = r"(\b[A-Z][a-z]+\b)\s(\b[A-Z][a-z]+\b)"
    match = re.search(pattern, text)
    if match:
        name = match.group()

    return name
def recommend(course):
    index = courses_list[courses_list['course_name'] == course].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_course_names = []
    for i in distances[1:7]:
        course_name = courses_list.iloc[i[0]].course_name
        recommended_course_names.append(course_name)
    return recommended_course_names

#questions for skill verification
web_dev_questions = [
    {
        'question': 'What does HTML stand for?',
        'options': ['HyperText Markup Language', 'Home Tool Markup Language', 'HyperLinks and Text Markup Language'],
        'answer': 'HyperText Markup Language'
    },
    {
        'question': 'Which CSS property is used to change the background color?',
        'options': ['background-color', 'color', 'bgcolor'],
        'answer': 'background-color'
    },
    {
        'question': 'Inside which HTML element do we put the JavaScript?',
        'options': ['<script>', '<js>', '<javascript>'],
        'answer': '<script>'
    },
    {
        'question': 'Which HTML attribute is used to define inline styles?',
        'options': ['class', 'styles', 'style'],
        'answer': 'style'
    },
    {
        'question': 'How do you make a list that lists the items with numbers?',
        'options': ['<ol>', '<ul>', '<list>'],
        'answer': '<ol>'
    }
]


#resume generator
def generate_resume(resume_data):
    """Generates a basic resume in plain text format.

    Args:
        resume_data (dict): A dictionary containing the resume information.

    Returns:
        str: The generated resume as a plain text string.
    """

    resume_text = f"""
**{resume_data['name']}**

**Contact:**
* Phone: {resume_data['phone']}
* Email: {resume_data['email']}

**Education:**
* {resume_data['education']}

**Skills:**
* {resume_data['skills']}

**Experience:**
* {resume_data['internships_experience']}

**Achievements:**
* {resume_data['achievements']}
"""

    # Add more sections or customize the format as needed

    return resume_text


#routes

@app.route('/')

# Login page route

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # Add the new user to the dummy users list
        users.append({
            'username': username,
            'email': email,
            'password': password  # You should hash the password in a real app!
        })
        
        # Redirect to the resume page after successful sign-up
        #return redirect(url_for('resume_wizard'))
        return render_template('resume.html')
    
    return render_template('signup.html')





# def resume():
#     # Provide a simple UI to upload a resume
#     return render_template("resume.html")

@app.route('/pred', methods=['POST'])

def pred():
    # Process the PDF or TXT file and make prediction
    if 'resume' in request.files:
        file = request.files['resume']
        filename = file.filename
        if filename.endswith('.pdf'):
            text = pdf_to_text(file)
        elif filename.endswith('.txt'):
            text = file.read().decode('utf-8')
        else:
            return render_template('resume.html', message="Invalid file format. Please upload a PDF or TXT file.")

        predicted_category = predict_category(text)
        recommended_job = job_recommendation(text)
        phone = extract_contact_number_from_resume(text)
        email = extract_email_from_resume(text)

        extracted_skills = extract_skills_from_resume(text)
        extracted_education = extract_education_from_resume(text)
        name = extract_name_from_resume(text)

        # Update global resume_data
        global resume_data
        resume_data = {
            'name': name,
            'phone': phone,
            'email': email,
            'education': extracted_education,
            'skills': ', '.join(extracted_skills)
        }

        return render_template('resume.html', predicted_category=predicted_category, recommended_job=recommended_job,
                               phone=phone, name=name, email=email, extracted_skills=extracted_skills, extracted_education=extracted_education)
    else:
        return render_template("resume.html", message="No resume file uploaded.")



@app.route('/next_page')
def next_page():
    # Render the next page with clickable text options
    return render_template('next_page.html')

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER




@app.route('/profile', methods=['GET', 'POST'])
def profile():
    global resume_data
    if request.method == 'POST':
        # Update resume data
        resume_data['name'] = request.form['name']
        resume_data['phone'] = request.form['phone']
        resume_data['email'] = request.form['email']
        resume_data['education'] = request.form['education']
        resume_data['skills'] = request.form['skills'].split(", ")  # Split skills by comma
        
        # Handle profile photo upload
        if 'profile_photo' in request.files:
            file = request.files['profile_photo']
            if file and file.filename:
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                resume_data['profile_photo'] = filename
        
        # Get work experience and achievements
        work_experience = request.form.getlist('work_experience')
        achievements = request.form.getlist('achievements')

        # Update work experience and achievements
        resume_data['work_experience'] = work_experience
        resume_data['achievements'] = achievements

        # Calculate points
        skill_points = len(resume_data['skills']) * 5
        work_points = len(work_experience) * 10
        achievement_points = len(achievements) * 10
        total_points = skill_points + work_points + achievement_points
        
        resume_data['points'] = {
            'skill_points': skill_points,
            'work_points': work_points,
            'achievement_points': achievement_points,
            'total_points': total_points
        }

        return redirect(url_for('profile'))

    # Ensure points exist in the resume data even when the page is first loaded
    if 'points' not in resume_data:
        resume_data['points'] = {
            'skill_points': 0,
            'work_points': 0,
            'achievement_points': 0,
            'total_points': 0
        }

    return render_template('profile.html', resume_data=resume_data)




@app.route('/job_recommendation', methods=['GET', 'POST'])
def job_recommendation_page():
    
    if request.method == 'POST':
        selected_job = request.form.get('job_title')
        
    

        # Debug: Print selected job and check if it exists in the dataframe
        print(f"Selected Job: {selected_job}")
       
        
        if selected_job in df['Title'].values:
            # Find the index of the selected job in the dataframe
            job_index = df[df['Title'] == selected_job].index[0]
            
            # Debug: Print job_index and dimensions of similarity_job
            print(f"Selected Job Index: {job_index}")
            print(f"Similarity Job Matrix Shape: {similarity_job.shape}")

            # Check if the job_index is within bounds of the similarity_job matrix
            if job_index >= similarity_job.shape[0]:
                error = "Job index is out of bounds for similarity matrix."
                print(f"Error: {error}")
                return render_template('job_recommendation.html', 
                                       all_jobs=df['Title'].tolist(), 
                                       error=error)

            # Get similar jobs
            distances = similarity_job[job_index]
            job_indices = distances.argsort()[:10]  # Get top 10 similar jobs
            
            # Validate job_indices within bounds of df
            valid_indices = [i for i in job_indices if i < len(df)]
            print(f"Valid Indices: {valid_indices}")

            if not valid_indices:
                error = "No valid job indices found."
                print(f"Error: {error}")
                recommended_jobs = []
            else:
                recommended_jobs = df.iloc[valid_indices]['Title'].tolist()
                error = None
        else:
            recommended_jobs = []
            error = "Selected job title not found."
        
        return render_template('job_recommendation.html', 
                               all_jobs=df['Title'].tolist(), 
                               recommended_jobs=recommended_jobs, 
                               selected_job=selected_job, 
                               error=error)
    
    # For GET request, render the page with a search box
    all_jobs = df['Title'].tolist()
    return render_template('job_recommendation.html', all_jobs=all_jobs)





@app.route('/course_recommendation', methods=['GET', 'POST'])
def course_recommendation():
    recommended_courses = []
    if request.method == 'POST':
        selected_course = request.form['course_name']
        recommended_courses = recommend(selected_course)
    
    course_list = courses_list['course_name'].tolist()
    return render_template('course_recommendation.html', 
                           course_list=course_list, 
                           recommended_courses=recommended_courses)




@app.route('/resume_wizard', methods=['GET', 'POST'])
def resume_wizard():
    global resume
    if request.method == 'POST':
        add_more_skills = request.form.get('add_more_skills')
        add_more_internships_experience = request.form.get('add_more_internships_experience')
        add_more_achievements = request.form.get('add_more_achievements')
        if 'achievements' not in resume_data:
            resume_data['achievements'] = []
        resume_data['achievements'].append(add_more_achievements)


        # Update resume data with additional information
        
        if add_more_skills:
            resume_data['skills'] += ', ' + add_more_skills
        if add_more_internships_experience:
            # Check if the key exists before appending
            if 'internships_experience' in resume_data:
                resume_data['internships_experience'].append(add_more_internships_experience)
            else:
                resume_data['internships_experience'] = [add_more_internships_experience]
        if add_more_achievements:
            resume_data['achievements'].append(add_more_achievements)

        generated_resume = generate_resume(resume_data)
        return render_template('resume_wizard.html', resume_data=resume_data, generated_resume=generated_resume)

    return render_template('resume_wizard.html', resume_data=resume_data)





@app.route('/skill_verification')
def skill_verification():
    return "<h1>Skill Verification Page</h1>"




@app.route('/community_chat')
def community_chat():
    return render_template('community_chat.html')



#main
if __name__ == '__main__':
    app.run(debug=True)
