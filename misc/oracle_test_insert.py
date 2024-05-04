from oracle_test_insert import generate_random_data_single
import cx_Oracle

dsn = cx_Oracle.makedsn(host="localhost", port=1521, service_name='orcl')
conn = cx_Oracle.connect(user="system", password="123456", dsn=dsn)

cur = conn.cursor()


def insert_one_stock(stock_id, cur, conn):
    data = generate_random_data_single(stock_id)
    batch_size = 5000
    for bstart in range(0, len(data), batch_size):
        batch_data = data[bstart: bstart+batch_size]
        sql = "INSERT INTO finance(stock_name, date_time, open, close, high, low, volume, amount, turn) VALUES (:1, TO_DATE(:2, 'YYYY-MM-DD HH24:MI:SS'), :3, :4, :5, :6, :7, :8, :9)"
        cur.executemany(sql, batch_data)
        conn.commit()
    else:
        print(f"{stock_id=} INSERT DONE.")

for stock_id in range(1, 10001):
    insert_one_stock(stock_id, cur, conn)