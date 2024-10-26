import subprocess
import time
import argparse





TIMEOUT = 0


def getter(iface_path):
    args = ['tx_bytes','rx_bytes','tx_packets','rx_packets']
    result = {}
    cmd = f'cat {iface_path}'
    for x in args:
        res = subprocess.run(f'{cmd}{x}', check=True, shell=True, capture_output=True).stdout
        result[x] = res.decode("utf-8")[0:-1]
    return result

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('timer')
    parser.add_argument('duration')
    parser.add_argument('iface')
    args = parser.parse_args()
    start = args.timer
    duration = args.duration
    TIMEOUT = int(duration)
    iface_path = f"/sys/class/net/{args.iface}/statistics/"
    while True:
        current_time = subprocess.run('date +"%T"', shell=True, check=True, capture_output=True).stdout.decode("utf-8")[0:-1]
        if current_time >= start:
            break
    res1 = getter(iface_path)
    time.sleep(TIMEOUT)
    res2 = getter(iface_path)
    delta = {}
    for key, value in res2.items():
        delta[key]=int(res2[key])-int(res1[key])


    delta['active_cores'] = subprocess.run("nproc", shell=True, check=True, capture_output=True).stdout.decode("utf-8")[0:-1]
    print(str(delta))

if __name__ == "__main__":
    main()
