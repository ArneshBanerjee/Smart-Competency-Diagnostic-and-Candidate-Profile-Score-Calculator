from flask import Flask, request, render_template
import pickle
from PyPDF2 import PdfReader
import re


app = Flask(__name__)

#loading the ml modes
rf_classifier_categorization = pickle.load(open('/Users/arneshbanerjee/Coding/Code/ml/job_recomendation/models/rf_classifier_categorization.pkl', 'rb'))
tfidf_vectorizer_categorization = pickle.load(open('/Users/arneshbanerjee/Coding/Code/ml/job_recomendation/models/tfidf_vectorizer_categorization.pkl', 'rb'))
rf_classifier_job_recomendation = pickle.load(open('/Users/arneshbanerjee/Coding/Code/ml/job_recomendation/models/rf_classifier_job_recommendation.pkl', 'rb'))
tfidf_vectorizer_job_recommendation = pickle.load(open('/Users/arneshbanerjee/Coding/Code/ml/job_recomendation/models/tfidf_vectorizer_job_recommendation.pkl', 'rb'))

#function


def cleanResume(txt):
    cleanText = re.sub(r'http\S+\s', ' ', txt)  # links
    cleanText = re.sub(r'RT|cc', ' ', cleanText)
    cleanText = re.sub(r'#\S+\s', ' ', cleanText)  # special characters
    cleanText = re.sub(r'@\S+', ' ', cleanText)
    cleanText = re.sub(r'[%s]' % re.escape(r"""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""), ' ', cleanText)
    cleanText = re.sub(r'[^\x00-\x7f]', ' ', cleanText)
    cleanText = re.sub(r'\s+', ' ', cleanText)
    return cleanText

def predict_category(resume_text):
    resume_text= cleanResume(resume_text)
    resume_tfidf = tfidf_vectorizer_categorization.transform([resume_text])
    predicted_category = rf_classifier_categorization.predict(resume_tfidf)[0]
    return predicted_category

def job_recommendation(resume_text):
    resume_text= cleanResume(resume_text)
    resume_tfidf = tfidf_vectorizer_job_recommendation.transform([resume_text])
    predicted_category = rf_classifier_job_recomendation.predict(resume_tfidf)[0]
    return predicted_category


def pdf_to_text(file):
    reader = PdfReader(file)
    text = ''
    for page in range(len(reader.pages)):
        text += reader.pages[page].extract_text()
    return text

#resume searching

#route path
@app.route("/")
def resume():
    return render_template('resume.html')


@app.route("/pred", methods=['POST'])
def pred():
    if 'resume' in request.files:
        file = request.files['resume']
        filename = file.filename

        if filename.endswith('.pdf'):
            text = pdf_to_text(file)
        elif filename.endswith('.txt'):
            text = file.read().decode('utf-8')
        else:
            return render_template('resume.html', message = "Invalid file type. Please upload pdf or txt file.")

        predicted_category = predict_category(text)
        recomended_job = job_recommendation(text)





        return render_template('resume.html', predicted_category = predicted_category, recomended_job = recomended_job)
    else:
        return render_template("resume.html", message = "No resume uploaded")




#main
if __name__ == "__main__":
    app.run(debug=True)