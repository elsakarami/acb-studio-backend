from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import CountVectorizer
import pandas as pd

def train_spam_model():
    data = pd.read_csv('spam_data.csv')
    X = data['email']
    y = data['label']

    vectorizer = CountVectorizer(max_features=1000, min_df=5, ngram_range=(1, 2))
    X = vectorizer.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    clf = RandomForestClassifier(n_estimators=100, max_depth=10, class_weight='balanced')
    clf.fit(X_train, y_train)

    return clf, vectorizer