
import re
import numpy as np
import pandas as pd
from data_modules import MissingIndicator,ExtractLetters, CategoricalImputer, RareLabelCategoricalEncoder
from data_modules import NumericalImputer, MinMaxScaler, OneHotEncoder,OrderingFeatures


from . import config
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, f1_score
import sys


def get_data(URL):
     
    # Loading data from specific url
    df = pd.read_csv(URL)
    
    # Uncovering missing data
    df.replace('?', np.nan, inplace=True)
    df['age'] = df['age'].astype('float')
    df['fare'] = df['fare'].astype('float')

    # helper function 1
    def get_first_cabin(row):
        try:
            return row.split()[0]
        except:
            return np.nan
    
    # helper function 2
    def get_title(passenger):
        line = passenger
        if re.search('Mrs', line):
            return 'Mrs'
        elif re.search('Mr', line):
            return 'Mr'
        elif re.search('Miss', line):
            return 'Miss'
        elif re.search('Master', line):
            return 'Master'
        else:
            return 'Other'
    
    # Keep only one cabin | Extract the title from 'name'
    df['cabin'] = df['cabin'].apply(get_first_cabin)
    df['title'] = df['name'].apply(get_title)
    
    # Droping irrelevant columns
    df.drop(columns=config.DROP_COLS, 1, inplace=True)
    
    df.to_csv(config.DATASETS_DIR + config.RETRIEVED_DATA, index=False)
    
    return print('Data stored in {}'.format(config.DATASETS_DIR + config.RETRIEVED_DATA))


def train():

 titanic_pipeline = Pipeline(
                              [
                                ('missing_indicator', MissingIndicator(variables=config.NUMERICAL_VARS)),
                                ('cabin_only_letter', ExtractLetters()),
                                ('categorical_imputer', CategoricalImputer(variables=config.CATEGORICAL_VARS_WITH_NA)),
                                ('median_imputation', NumericalImputer(variables=config.NUMERICAL_VARS_WITH_NA)),
                                ('rare_labels', RareLabelCategoricalEncoder(tol=0.05, variables=config.CATEGORICAL_VARS)),
                                ('dummy_vars', OneHotEncoder(variables=config.CATEGORICAL_VARS)),
                                ('aligning_feats', OrderingFeatures()),
                                ('scaling', MinMaxScaler()),
                                ('log_reg', LogisticRegression(C=0.0005, class_weight='balanced', random_state=config.SEED_MODEL))
                              ])

 df = pd.read_csv(config.DATASETS_DIR + config.RETRIEVED_DATA)

 X_train, X_test, y_train, y_test = train_test_split(
                                                        df.drop(config.TARGET, axis=1),
                                                        df[config.TARGET],
                                                        test_size=0.2,
                                                        random_state=404
                                                   )

 titanic_pipeline.fit(X_train, y_train)

    
 class_pred = titanic_pipeline.predict(X_test)
 proba_pred = titanic_pipeline.predict_proba(X_test)[:,1]
 #print('test roc-auc : {}'.format(roc_auc_score(y_test, proba_pred)))
 #print('test accuracy: {}'.format(accuracy_score(y_test, class_pred)))
 #print()



if __name__ == "__main__":
    train()