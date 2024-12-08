from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import pandas as pd

def train_spam_model():
    data = pd.read_csv('spam_data.csv')
    X = data['email']
    y = data['label']

    from sklearn.feature_extraction.text import CountVectorizer
    vectorizer = CountVectorizer()
    X = vectorizer.fit_transform(X)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
 
    clf = RandomForestClassifier()
    clf.fit(X_train, y_train)
    
    return clf, vectorizer

spam_clf, vectorizer = train_spam_model()
