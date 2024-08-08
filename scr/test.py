import pandas as pd

data = {
    'name': ['Alice', 'Bob', 'Charlie'],
    'age': [25, 30, 35],
    'city': ['New York', 'Los Angeles', 'Chicago']
}

df = pd.DataFrame(data)

for index, row in df.iterrows():
    print(f"Index: {index}, Name: {row['name']}, Age: {row['age']}")