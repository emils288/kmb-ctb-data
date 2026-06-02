import requests
import csv
import time

def main():
    print("🚌 雲端中心：城巴數據獨立極速測試...")
    
    # 1. 獲取城巴路線
    ctb_routes_url = "https://rt.data.gov.hk/v2/transport/citybus/route/ctb"
    try:
        print("發起城巴清單請求...")
        res = requests.get(ctb_routes_url, timeout=15)
        print(f"HTTP 狀態碼: {res.status_code}")
        ctb_routes = res.json()['data']
        print(f"成功取得城巴共 {len(ctb_routes)} 條路線！海外 IP 沒被牆！")
    except Exception as e:
        print(f"❌ 城巴第一步就卡死/被牆: {e}")
        return

    ctb_rs_data = []
    ctb_stop_dict = {}
    
    # 先測試前 10 條線，唔好浪費時間，睇吓過唔過到
    print("開始測試前 10 條城巴線...")
    for r in ctb_routes[:10]:
        route_num = r['route']
        for bound in ['outbound', 'inbound']:
            b_code = 'O' if bound == 'outbound' else 'I'
            url = f"https://rt.data.gov.hk/v2/transport/citybus/route-stop/CTB/{route_num}/{bound}"
            try:
                res = requests.get(url, timeout=5).json()
                if 'data' in res:
                    for stop_item in res['data']:
                        stop_id = stop_item['stop']
                        ctb_rs_data.append([route_num, b_code, stop_id])
                        ctb_stop_dict[stop_id] = "待查"
            except Exception:
                continue
            time.sleep(0.1)
            
    print(f"前 10 條線測試成功，共抓到 {len(ctb_rs_data)} 筆記錄！")
    
    # 寫入一個臨時 ctb_rs.csv
    with open('ctb_rs.csv', 'w', newline='', encoding='utf-8') as f:
        csv.writer(f).writerows(ctb_rs_data)
    print("✅ 城巴局部測試檔已寫入！")

if __name__ == "__main__":
    main()
