import argparse
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sn
from pymongo import MongoClient
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
import datetime
import pickle

parser = argparse.ArgumentParser(description='Create Model')
parser.add_argument('-u', '--uri', required=True, help="mongodb uri with username/password")
args = parser.parse_args()

mongo_uri = args.uri
mongo_db = "sales"
mongo_collection = "sales"

client = MongoClient(mongo_uri)
db = client[mongo_db]
collection = db[mongo_collection]

# Fetch all documents
data = list(collection.find({}))

# Create DataFrame
df = pd.DataFrame(data)

# Convert columns to numeric type
df['price'] = df['price'].str.replace(r'$', '')
df['price'] = df['price'].str.replace(r',', '')
df['price'] = pd.to_numeric(df['price'], errors='coerce')
df['last12MonthEarnings'] = df['last12MonthEarnings'].str.replace(r'$', '')
df['last12MonthEarnings'] = df['last12MonthEarnings'].str.replace(r',', '')
df['last12MonthEarnings'] = pd.to_numeric(df['last12MonthEarnings'], errors='coerce')
df['dollarAge'] = pd.to_numeric(df['dollarAge'], errors='coerce')

# Drop rows with NaN values after conversion
df = df.dropna(subset=['price', 'last12MonthEarnings'])

# Calculate additional columns
df['avg_multiply'] = df['price'] / df['last12MonthEarnings']
#df['dollarAge_num'] = df['dollarAge'].astype(float)

# Drop unnecessary columns
df = df.drop(columns=["title", "_id"])

# Compute correlation matrix
corr = df.corr()

print(corr)
sn.heatmap(corr, annot=True)
plt.show()

# Prepare data for training
y = df['price']
X = df[['last12MonthEarnings', 'dollarAge']]

# Split data into train and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42)

# Baseline Linear Regression
lr = LinearRegression()
lr.fit(X_train, y_train)
y_pred_lr = lr.predict(X_test)
lr_r2 = r2_score(y_test, y_pred_lr)
lr_mse = mean_squared_error(y_test, y_pred_lr)
print("Linear Regression:")
print("r2:\t{}\nMSE:\t{}".format(lr_r2, lr_mse))

# Gradient Boosting Regressor
gbr = GradientBoostingRegressor(n_estimators=50, random_state=9000)
gbr.fit(X_train, y_train)
y_pred_gbr = gbr.predict(X_test)
gbr_r2 = r2_score(y_test, y_pred_gbr)
gbr_mse = mean_squared_error(y_test, y_pred_gbr)
print("\nGradient Boosting Regressor:")
print("r2:\t{}\nMSE:\t{}".format(gbr_r2, gbr_mse))

# Demo
last12MonthEarnings = 10000
dollarAge = 5
demo_input = [[last12MonthEarnings, dollarAge]]
demo_df = pd.DataFrame(columns=['last12MonthEarnings', 'dollarAge'], data=demo_input)
demo_output = gbr.predict(demo_df)
predictedPrice = demo_output[0]

print("\n*** DEMO ***")
print("Last 12 Month Earnings:", last12MonthEarnings)
print("Dollar Age:", dollarAge)
print("Our Model:", predictedPrice)

# Save and load the model
with open('GradientBoostingRegressor.pkl', 'wb') as fid:
    pickle.dump(gbr, fid)

with open('GradientBoostingRegressor.pkl', 'rb') as fid:
    gbr_loaded = pickle.load(fid)
