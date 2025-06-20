import pandas as pd
from tinydb import TinyDB

# Load TinyDB JSON
db = TinyDB('data/responses.json')

# Convert to Pandas DataFrame
df = pd.DataFrame(db.all())

# Export to Excel
df.to_excel('data/responses.xlsx', index=False)

print("Exported successfully to data/responses.xlsx")
