import pandas as pd
import os

def convert():
    data_dir = 'data'
    files = {
        '订单数据.xlsx': 'orders.pkl',
        '订单明细.xlsx': 'order_items.pkl',
        '用户数据.xlsx': 'users.pkl',
        '商品数据.xlsx': 'products.pkl'
    }

    for excel_file, pkl_file in files.items():
        excel_path = os.path.join(data_dir, excel_file)
        pkl_path = os.path.join(data_dir, pkl_file)

        if not os.path.exists(excel_path):
            print(f'跳过: {excel_file} 不存在')
            continue

        print(f'转换: {excel_file} -> {pkl_file}')
        df = pd.read_excel(excel_path)

        if '下单时间' in df.columns:
            df['下单时间'] = pd.to_datetime(df['下单时间'])
            df['日期'] = df['下单时间'].dt.date
            df['月份'] = df['下单时间'].dt.to_period('M')
            df['星期'] = df['下单时间'].dt.day_name()
            df['小时'] = df['下单时间'].dt.hour

        df.to_pickle(pkl_path)
        excel_size = os.path.getsize(excel_path) / 1024 / 1024
        pkl_size = os.path.getsize(pkl_path) / 1024 / 1024
        print(f'  Excel: {excel_size:.1f}MB -> Pickle: {pkl_size:.1f}MB')

    print('\n转换完成！')

if __name__ == '__main__':
    convert()
