import requests
import csv
import time

def main():
    print("🚌 雲端中心：開始大一統同步（安全降速防封鎖版）...")
    
    all_rs = []
    all_stops = {}

    # --------------------------------------------------
    # 🌟 1. 抓取九巴 KMB 數據
    # --------------------------------------------------
    print("正在下載九巴數據...")
    try:
        kmb_rs = requests.get("https://data.etabus.gov.hk/v1/transport/kmb/route-stop", timeout=30).json()['data']
        for item in kmb_rs:
            all_rs.append([item['route'], item['bound'], item['stop']])
            
        kmb_stops = requests.get("https://data.etabus.gov.hk/v1/transport/kmb/stop", timeout=30).json()['data']
        for item in kmb_stops:
            all_stops[item['stop']] = item['name_tc']
        print(f"九巴下載完成，共 {len(all_rs)} 條分站記錄。")
    except Exception as e:
        print(f"❌ 九巴下載失敗: {e}")

    # --------------------------------------------------
    # 🌟 2. 抓取城巴 CTB 數據 (加入安全降速與保命超時防線)
    # --------------------------------------------------
    print("正在下載城巴路線列表...")
    try:
        ctb_routes = requests.get("https://rt.data.gov.hk/v2/transport/citybus/route/ctb", timeout=30).json()['data']
        print(f"成功取得城巴共 {len(ctb_routes)} 條路線。開始逐條爬取分站...")
    except Exception as e:
        print(f"❌ 城巴路線清單獲取失敗: {e}")
        return

    ctb_rs_data = []
    ctb_stop_dict = {}
    
    count = 0
    for r in ctb_routes:
        route_num = r['route']
        count += 1
        if count % 20 == 0:
            print(f"已處理 {count}/{len(ctb_routes)} 條城巴路線...")

        for bound in ['outbound', 'inbound']:
            b_code = 'O' if bound == 'outbound' else 'I'
            url = f"https://rt.data.gov.hk/v2/transport/citybus/route-stop/CTB/{route_num}/{bound}"
            
            try:
                # 設 5 秒超時，卡住就即刻拋棄，絕對不准卡死 5 分鐘！
                res = requests.get(url, timeout=5).json()
                if 'data' in res:
                    for stop_item in res['data']:
                        stop_id = stop_item['stop']
                        ctb_rs_data.append([route_num, b_code, stop_id])
                        
                        # 記錄需要查詢名嘅 Unique ID
                        if stop_id not in ctb_stop_dict:
                            ctb_stop_dict[stop_id] = "未知車站"
            except Exception:
                # 某條線超時就直接 Skip，保住大局
                continue
            
            # 👑 降速保命符：每 Call 完一個方向，強行睡眠 0.15 秒，防止被政府 Gateway 封鎖 IP！
            time.sleep(0.15)

    # --------------------------------------------------
    # 🌟 3. 獲取城巴車站中文字名 (批量安全獲取)
    # --------------------------------------------------
    print(f"開始獲取城巴共 {len(ctb_stop_dict)} 個獨一無二嘅車站名稱...")
    s_count = 0
    for stop_id in list(ctb_stop_dict.keys()):
        s_count += 1
        if s_count % 100 == 0:
            print(f"已獲取 {s_count}/{len(ctb_stop_dict)} 個車站名...")
            
        s_url = f"https://rt.data.gov.hk/v2/transport/citybus/stop/{stop_id}"
        try:
            s_res = requests.get(s_url, timeout=3).json()
            if 'data' in s_res:
                ctb_stop_dict[stop_id] = s_res['data']['name_tc']
        except Exception:
            # 獲取失敗就保持「未知車站」，不阻礙腳本運行
            pass
            
        # 👑 降速保命符：每查一個站名，休息 0.1 秒
        time.sleep(0.1)

    # --------------------------------------------------
    # 🌟 4. 分家打包寫入 CSV
    # --------------------------------------------------
    print("正在將數據寫入個別 CSV 檔案...")
    
    # 寫入九巴
    with open('kmb_rs.csv', 'w', newline='', encoding='utf-8') as f:
        csv.writer(f).writerows(all_rs)
    with open('kmb_stop.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        for s_id, s_name in all_stops.items():
            writer.writerow([s_id, s_name])

    # 寫入城巴
    with open('ctb_rs.csv', 'w', newline='', encoding='utf-8') as f:
        csv.writer(f).writerows(ctb_rs_data)
    with open('ctb_stop.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        for s_id, s_name in ctb_stop_dict.items():
            writer.writerow([s_id, s_name])
            
    print("✅ 【大一統分家】所有 CSV 檔案安全生成完畢！")

if __name__ == "__main__":
    main()
