import pandas as pd
import numpy as np
import twitter_get_user_data as tgud


def prepare_ann_model():
    dataset = pd.read_csv('for_ml.csv')
    X = dataset.iloc[:, 3:13].values
    y = dataset.iloc[:, 13].values
    
    # Splitting the dataset into the Training set and Test set
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.5, random_state = 0)
    
    # Feature Scaling
    from sklearn.preprocessing import StandardScaler
    sc = StandardScaler()
    X_train = sc.fit_transform(X_train)
    X_test = sc.transform(X_test)
        
    # Importing the Keras libraries and packages
    from keras.models import Sequential
    from keras.layers import Dense
    
    # Initialising the ANN
    classifier = Sequential()
    
    # Adding the input layer and the first hidden layer
    classifier.add(Dense(4, activation = 'relu', input_dim = 10))
    
    # Adding the second hidden layer
    classifier.add(Dense(4, activation = 'relu'))
    
    # Adding the output layer
    classifier.add(Dense(1, activation = 'sigmoid'))
    
    # Compiling the ANN
    classifier.compile(optimizer = 'adam', loss = 'binary_crossentropy', metrics = ['accuracy'])
    
    # Fitting the ANN to the Training set
    classifier.fit(X_train, y_train, batch_size = 10, epochs = 100)
    
    # Saving the model
    classifier.save('bot_data/ann_model')

def ann_predict_bot(screen_name):
    from tensorflow import keras
    classifier = keras.models.load_model('bot_data/ann_model')
    from joblib import load
    sc = load('bot_data/std_scaler.bin')
    
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
    # Predicting the Test set results
    y_pred = classifier.predict(user)
    y_pred = (y_pred > 0.5)
    
    return int(y_pred)