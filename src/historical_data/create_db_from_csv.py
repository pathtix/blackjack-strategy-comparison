import sqlite3
import pandas as pd

def create_db_from_csv(csv_file_path, db_file_path):
    conn = sqlite3.connect(db_file_path)
    chunksize = 100000

    cols_to_keep = ['initial_hand', 'dealer_up', 'actions_taken']
    dtype = {'initial_hand': 'str', 'dealer_up': 'str', 'actions_taken': 'str'}

    # Read and store the CSV data in chunks
    for chunk in pd.read_csv(csv_file_path, usecols=cols_to_keep, dtype=dtype, chunksize=chunksize):
        chunk.to_sql('historical_data', conn, if_exists='append', index=False)

    # Create an index on initial_hand and dealer_up for faster lookups
    cursor = conn.cursor()
    cursor.execute("CREATE INDEX idx_historical_data ON historical_data (initial_hand, dealer_up)")
    conn.commit()
    conn.close()

if __name__ == "__main__":
    # Provide the path to your CSV file and the path where you want to save the SQLite database file
    csv_file_path = 'etc/blackjack_simulator.csv'
    db_file_path = 'src/historical_data/historical_data.db'
    create_db_from_csv(csv_file_path, db_file_path)