import pandas as pd
import numpy as np
import twitter_get_user_data as tgud

def prepare_model():
    dataset = pd.read_csv('for_ml.csv')
    X = dataset.iloc[:, 3:13].values
    y = dataset.iloc[:, 13].values
    
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.5, random_state = 0)
    
    from sklearn.preprocessing import StandardScaler
    sc = StandardScaler()
    X_train = sc.fit_transform(X_train)
    X_test = sc.transform(X_test)
    from joblib import dump
    dump(sc, 'bot_data/std_scaler.bin', compress=True)
    
    from sklearn.ensemble import RandomForestClassifier
    classifier = RandomForestClassifier(n_estimators = 10, criterion = 'entropy', random_state = 0)
    classifier.fit(X_train, y_train)
    
    dump(classifier, 'bot_data/decision_trees.joblib')
    
def dt_pretict_bot(screen_name):
    from joblib import load
    # load pre-trained model
    classifier = load('bot_data/decision_trees.joblib')
    sc = load('bot_data/std_scaler.bin')
    
    # get user data for prediction
    user_details = tgud.get_single_user(screen_name)
    user_data = []
    user_data.append(int(user_details['Followers Count']))
    user_data.append(int(user_details['Friends Count']))
    user_data.append(int(user_details['Protected']))  
    if user_details['Location']:
        user_data.append(1)
    else:
        user_data.append(0)
    user_data.append(int(user_details['Verified']))
    user_data.append(int(user_details['Listed count']))
    user_data.append(int(user_details['Favourites count']))
    user_data.append(int(user_details['Status count']))
    user_data.append(int(user_details['Default profile']))
    user_data.append(int(user_details['Default profile image']))
    user = np.array(user_data)
    user = user.reshape(1, 10)
    user = sc.transform(user)

    y_pred = classifier.predict(user)
    y_pred = (y_pred > 0.5)
    
    return int(y_pred)
    