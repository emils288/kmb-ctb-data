import requests
import csv

def main():
    print("🚌 雲端中心：開始同步九巴與城巴數據...")
    
    # ==================================================
    # 🌟 1. 抓取九巴 KMB 數據 (對齊官方 etabus.gov.hk)
    # ==================================================
    print("正在打包九巴數據...")
    kmb_rs_url = "https://data.etabus.gov.hk/v1/transport/kmb/route-stop"
    kmb_stop_url = "https://data.etabus.gov.hk/v1/transport/kmb/stop"
    
    kmb_rs_data = []
    kmb_rs = requests.get(kmb_rs_url).json()['data']
    for item in kmb_rs:
        kmb_rs_data.append([item['route'], item['bound'], item['stop']])
        
    kmb_stop_data = []
    kmb_stops = requests.get(kmb_stop_url).json()['data']
    for item in kmb_stops:
        kmb_stop_data.append([item['stop'], item['name_tc']])

    with open('kmb_rs.csv', 'w', newline='', encoding='utf-8') as f:
        csv.writer(f).writerows(kmb_rs_data)
    with open('kmb_stop.csv', 'w', newline='', encoding='utf-8') as f:
        csv.writer(f).writerows(kmb_stop_data)

    # ==================================================
    # 🌟 2. 抓取城巴 CTB 數據 (對齊官方 rt.data.gov.hk)
    # ==================================================
    print("正在打包城巴數據...")
    ctb_routes_url = "https://rt.data.gov.hk/v2/transport/citybus/route/ctb"
    ctb_routes = requests.get(ctb_routes_url).json()['data']
    
    ctb_rs_data = []
    ctb_stop_dict = {}
    
    for r in ctb_routes:
        route_num = r['route']
        for bound in ['outbound', 'inbound']:
            b_code = 'O' if bound == 'outbound' else 'I'
            url = f"https://rt.data.gov.hk/v2/transport/citybus/route-stop/CTB/{route_num}/{bound}"
            res = requests.get(url).json()
            if 'data' in res:
                for stop_item in res['data']:
                    stop_id = stop_item['stop']
                    ctb_rs_data.append([route_num, b_code, stop_id])
                    
                    # 雲端直接爬埋城巴站名
                    if stop_id not in ctb_stop_dict:
                        s_url = f"https://rt.data.gov.hk/v2/transport/citybus/stop/{stop_id}"
                        s_res = requests.get(s_url).json()
                        if 'data' in s_res:
                            ctb_stop_dict[stop_id] = s_res['data']['name_tc']

    with open('ctb_rs.csv', 'w', newline='', encoding='utf-8') as f:
        csv.writer(f).writerows(ctb_rs_data)
        
    with open('ctb_stop.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        for s_id, s_name in ctb_stop_dict.items():
            writer.writerow([s_id, s_name])
            
    print("✅ 所有數據獨立打包完成！")

if __name__ == "__main__":
    main()
