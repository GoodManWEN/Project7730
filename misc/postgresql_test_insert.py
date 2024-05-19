

from postgresql_test_utils import generate_random_data_single
import asyncio
import asyncpg

async def insert_one_stock(stock_id,  conn):
    data = generate_random_data_single(stock_id,convert_time=False)
    batch_size = 5000
    for bstart in range(0, len(data), batch_size):
        batch_data = data[bstart: bstart+batch_size]
        sql = "INSERT INTO finance(stock_name, date_time, open, close, high, low, volume, amount, turn) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)"
        await conn.executemany(sql, batch_data)
    else:
        print(f"{stock_id=} INSERT DONE.")


async def main():
    conn = await asyncpg.connect(user='postgres', password='123456', database='test', host='127.0.0.1')
    for stock_id in range(900, 1001):
        await insert_one_stock(stock_id, conn)

loop = asyncio.new_event_loop()
loop.run_until_complete(main())