import asyncio
import subprocess

from connections import *
import sqlite3
import ast
            
iface = "wg0"
eth = "enp5s0f0"
test_name = "WG_site2site_MTU100"
test_time = 30
def time_counter():
    current_time = subprocess.run('date +"%T"', shell=True, check=True, capture_output=True).stdout.decode("utf-8")[0:-1]

    hours = int(current_time[:2])
    minutes = int(current_time[3:5])
    seconds = int(current_time[6:])+5

    if seconds > 55:
        if seconds > 55:
            seconds = 0
            minutes += 1

        if minutes > 59:
            minutes = 0
            hours += 1

    start_time = f"{hours:02}:{minutes:02}:{seconds:02}"

    return start_time

def get_throughput(data: dict, hostname: str):
    tx = int(data['tx_bytes'])
    rx = int(data['rx_bytes'])
    tx = (tx*8)/(1e6*test_time)
    rx = (rx*8)/(1e6*test_time)
    print(f"#HOSTNAME: {hostname} [RX: {rx};TX {tx}]")
    return tx, rx


def run_cmd(args:str):
    print(f"# {args}")
    return subprocess.run(args, shell=True, text=True)



async def main():

    h1 = Host(ip='192.168.1.11',usr='root',passwd='tc403',name='h1')
    h2 = Host(ip='192.168.1.12',usr='root',passwd='tc403',name='h2')



    db = sqlite3.connect(f"{test_name}.db")
    cursor = db.cursor()

    cursor.execute(
        f"CREATE TABLE pc1_{iface} (name TEXT, tx_throughput INTEGER, rx_throughput INTEGER, tx_bytes INTEGER, rx_bytes INTEGER, tx_packets INTEGER, rx_packets INTEGER)")
    cursor.execute(
        f"CREATE TABLE pc2_{iface} (name TEXT, tx_throughput INTEGER, rx_throughput INTEGER, tx_bytes INTEGER, rx_bytes INTEGER, tx_packets INTEGER, rx_packets INTEGER)")
    cursor.execute(
        f"CREATE TABLE pc1_{eth} (name TEXT, tx_throughput INTEGER, rx_throughput INTEGER, tx_bytes INTEGER, rx_bytes INTEGER, tx_packets INTEGER, rx_packets INTEGER)")
    cursor.execute(
        f"CREATE TABLE pc2_{eth} (name TEXT, tx_throughput INTEGER, rx_throughput INTEGER, tx_bytes INTEGER, rx_bytes INTEGER, tx_packets INTEGER, rx_packets INTEGER)")

    # Debug connection and commands


    await h1.set_cores_down()
    await h2.set_cores_down()
      # Make sure this runs valid commands


    for x in range(0, h1.cores):
        start_time = time_counter()
        print(f"Starting h1 and h2 at {start_time}")
        results = await asyncio.gather(
            h1.start(start_time, test_time, iface),
            h1.start(start_time, test_time, eth),
            h2.start(start_time, test_time, iface),
            h2.start(start_time, test_time, eth)
        )
        h1_res = ast.literal_eval(results[0])
        h2_res = ast.literal_eval(results[2])
        h1_res_eth = ast.literal_eval(results[1])
        h2_res_eth = ast.literal_eval(results[3])
        print("?#h1_res",h1_res)
        print("?#h2_res",h2_res)

        # Insert into DB
        print("Inserting to DB...")
        h1_tx_th, h1_rx_th = get_throughput(h1_res, 'h1-iface')
        h2_tx_th, h2_rx_th = get_throughput(h2_res, 'h2-iface')

        h1_tx_th_eth, h1_rx_th_eth = get_throughput(h1_res_eth, 'h1-eth')
        h2_tx_th_eth, h2_rx_th_eth = get_throughput(h2_res_eth, 'h2-eth')

        cursor.execute(
            f"INSERT INTO pc1_{iface} VALUES ('cores {h1_res['active_cores']} | {x + 1}' ,{h1_tx_th},{h1_rx_th},{h1_res['tx_bytes']},{h1_res['rx_bytes']},{h1_res['tx_packets']} ,{h1_res['rx_packets']} )")
        cursor.execute(
            f"INSERT INTO pc2_{iface} VALUES ('cores {h2_res['active_cores']} | {x+1}' ,{h2_tx_th},{h2_rx_th},{h2_res['tx_bytes']},{h2_res['rx_bytes']},{h2_res['tx_packets']} ,{h2_res['rx_packets']} )")
        cursor.execute(
            f"INSERT INTO pc1_{eth} VALUES ('cores {h1_res_eth['active_cores']} | {x + 1}' ,{h1_tx_th_eth},{h1_rx_th_eth},{h1_res_eth['tx_bytes']},{h1_res_eth['rx_bytes']},{h1_res_eth['tx_packets']} ,{h1_res_eth['rx_packets']} )")
        cursor.execute(
            f"INSERT INTO pc2_{eth} VALUES ('cores {h2_res_eth['active_cores']} | {x + 1}' ,{h2_tx_th_eth},{h2_rx_th_eth},{h2_res_eth['tx_bytes']},{h2_res_eth['rx_bytes']},{h2_res_eth['tx_packets']} ,{h2_res_eth['rx_packets']} )")

        db.commit()


        # Increase cores
        await h1.core_up()
        await h2.core_up()



if __name__ == "__main__":
    asyncio.run(main())