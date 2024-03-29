from vco_api_main import vco_api_main

class pccwg_vco(vco_api_main):
    def __init__(self):
        super().__init__()

if __name__ == '__main__':
    '''
    Create the VCO client object and detect WAN anomoly
    by calling the respective function
    '''
    conn = pccwg_vco()
    conn.detect_wan_anomaly(min_per_sample = 5, 
        interval_sec_present = 300, 
        interval_sec_hist = 3600)
    '''
    min_per_sample of 5 i.e. one sample every 5 minutes
    interval_sec_present of 300 i.e. 5 minutes
    interval_sec_hist of 3600 i.e. 60 minutes
    '''
