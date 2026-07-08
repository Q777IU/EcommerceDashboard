import pandas as pd
import numpy as np
import os

class DataAnalyzer:
    def __init__(self, data_dir='data'):
        self.data_dir = data_dir
        self.df_orders, self.df_order_items, self.df_users, self.df_products = self._load_data()
        self._precompute()

    def _load_data(self):
        pkl_files = {
            'orders': 'orders.pkl',
            'order_items': 'order_items.pkl',
            'users': 'users.pkl',
            'products': 'products.pkl'
        }

        data = {}
        for key, filename in pkl_files.items():
            pkl_path = os.path.join(self.data_dir, filename)
            xlsx_path = os.path.join(self.data_dir, filename.replace('.pkl', '.xlsx').replace('orders', '订单数据').replace('order_items', '订单明细').replace('users', '用户数据').replace('products', '商品数据'))

            if os.path.exists(pkl_path):
                data[key] = pd.read_pickle(pkl_path)
            else:
                data[key] = pd.read_excel(xlsx_path)
                if key == 'orders' and '下单时间' in data[key].columns:
                    data[key]['下单时间'] = pd.to_datetime(data[key]['下单时间'])

        if '日期' not in data['orders'].columns:
            df = data['orders']
            df['日期'] = df['下单时间'].dt.date
            df['月份'] = df['下单时间'].dt.to_period('M')
            df['星期'] = df['下单时间'].dt.day_name()
            df['小时'] = df['下单时间'].dt.hour

        return data['orders'], data['order_items'], data['users'], data['products']

    def _precompute(self):
        self.completed_mask = self.df_orders['订单状态'] == '已完成'
        self.df_completed = self.df_orders[self.completed_mask]

        self.daily_trend = self.df_completed.groupby('日期').agg({
            '订单总金额': 'sum',
            '订单利润': 'sum',
            '订单ID': 'count',
            '用户ID': 'nunique'
        }).reset_index()
        self.daily_trend.columns = ['日期', '销售额', '利润', '订单数', '客户数']

        self.monthly_trend = self.df_completed.groupby('月份').agg({
            '订单总金额': 'sum',
            '订单利润': 'sum',
            '订单ID': 'count',
            '用户ID': 'nunique'
        }).reset_index()
        self.monthly_trend['月份'] = self.monthly_trend['月份'].astype(str)
        self.monthly_trend.columns = ['月份', '销售额', '利润', '订单数', '客户数']

        self.category_sales = self.df_order_items.merge(
            self.df_completed[['订单ID']], on='订单ID'
        ).groupby('商品类别').agg({
            '商品金额': 'sum',
            '商品成本': 'sum',
            '数量': 'sum',
            '订单ID': 'nunique'
        }).reset_index()
        self.category_sales['利润'] = self.category_sales['商品金额'] - self.category_sales['商品成本']
        self.category_sales['利润率'] = self.category_sales['利润'] / self.category_sales['商品金额']
        self.category_sales.columns = ['商品类别', '销售额', '成本', '销量', '订单数', '利润', '利润率']
        self.category_sales = self.category_sales.sort_values('销售额', ascending=False).reset_index(drop=True)

        self.region_sales = self.df_completed.groupby('省份').agg({
            '订单总金额': 'sum',
            '订单利润': 'sum',
            '订单ID': 'count',
            '用户ID': 'nunique'
        }).reset_index()
        self.region_sales.columns = ['省份', '销售额', '利润', '订单数', '客户数']
        self.region_sales = self.region_sales.sort_values('销售额', ascending=False).reset_index(drop=True)

        self.user_stats = self.df_completed.groupby('用户ID').agg({
            '订单总金额': ['sum', 'mean', 'count'],
            '订单利润': 'sum'
        }).reset_index()
        self.user_stats.columns = ['用户ID', '消费总额', '客单价', '订单数', '贡献利润']
        self.user_stats = self.user_stats.merge(
            self.df_users[['用户ID', '性别', '年龄', '省份', '城市', '会员等级']],
            on='用户ID', how='left'
        )

        self.member_stats = self.df_completed.groupby('会员等级').agg({
            '订单总金额': ['sum', 'mean'],
            '订单ID': 'count',
            '用户ID': 'nunique',
            '订单利润': 'sum'
        }).reset_index()
        self.member_stats.columns = ['会员等级', '总销售额', '客单价', '订单数', '客户数', '总利润']
        self.member_stats['人均消费'] = self.member_stats['总销售额'] / self.member_stats['客户数']
        self.member_stats = self.member_stats.sort_values('总销售额', ascending=False).reset_index(drop=True)

        self.pay_stats = self.df_completed.groupby('支付方式').agg({
            '订单总金额': 'sum',
            '订单ID': 'count'
        }).reset_index()
        self.pay_stats.columns = ['支付方式', '销售额', '订单数']
        self.pay_stats['占比'] = self.pay_stats['销售额'] / self.pay_stats['销售额'].sum()
        self.pay_stats = self.pay_stats.sort_values('销售额', ascending=False).reset_index(drop=True)

        self.hourly = self.df_completed.groupby('小时').agg({
            '订单总金额': 'sum',
            '订单ID': 'count'
        }).reset_index()
        self.hourly.columns = ['小时', '销售额', '订单数']
        self.hourly = self.hourly.sort_values('小时').reset_index(drop=True)

        weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        weekday_cn = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        self.weekly = self.df_completed.groupby('星期').agg({
            '订单总金额': 'sum',
            '订单ID': 'count'
        }).reset_index()
        self.weekly.columns = ['星期', '销售额', '订单数']
        self.weekly['星期_en'] = pd.Categorical(self.weekly['星期'], categories=weekday_order, ordered=True)
        self.weekly = self.weekly.sort_values('星期_en').reset_index(drop=True)
        self.weekly['星期'] = weekday_cn
        self.weekly = self.weekly.drop('星期_en', axis=1)

    def get_overview_stats(self, start_date=None, end_date=None):
        if start_date is None and end_date is None:
            df = self.df_orders
            df_c = self.df_completed
        else:
            mask = pd.Series(True, index=self.df_orders.index)
            if start_date:
                mask &= self.df_orders['日期'] >= pd.to_datetime(start_date).date()
            if end_date:
                mask &= self.df_orders['日期'] <= pd.to_datetime(end_date).date()
            df = self.df_orders[mask]
            df_c = df[df['订单状态'] == '已完成']

        total_orders = len(df)
        total_sales = df_c['订单总金额'].sum()
        total_profit = df_c['订单利润'].sum()
        total_customers = df['用户ID'].nunique()
        avg_order_value = df_c['订单总金额'].mean()
        conversion_rate = len(df_c) / total_orders if total_orders > 0 else 0

        return {
            '总订单数': total_orders,
            '总销售额': round(total_sales, 2),
            '总利润': round(total_profit, 2),
            '客户数': total_customers,
            '客单价': round(avg_order_value, 2),
            '转化率': round(conversion_rate, 4)
        }

    def get_sales_trend(self, period='daily', start_date=None, end_date=None):
        if start_date is None and end_date is None:
            return self.daily_trend.copy() if period == 'daily' else self.monthly_trend.copy()

        if period == 'daily':
            df = self.daily_trend.copy()
        else:
            df = self.monthly_trend.copy()
            df['月份'] = pd.to_datetime(df['月份'])

        if start_date:
            start = pd.to_datetime(start_date).date() if period == 'daily' else pd.to_datetime(start_date)
            col = '日期' if period == 'daily' else '月份'
            df = df[df[col] >= start]
        if end_date:
            end = pd.to_datetime(end_date).date() if period == 'daily' else pd.to_datetime(end_date)
            col = '日期' if period == 'daily' else '月份'
            df = df[df[col] <= end]

        if period == 'monthly':
            df['月份'] = df['月份'].astype(str)

        return df.reset_index(drop=True)

    def get_category_sales(self, start_date=None, end_date=None):
        if start_date is None and end_date is None:
            return self.category_sales.copy()

        df_items = self.df_order_items.copy()
        df_orders = self.df_completed[['订单ID', '日期']].copy()

        if start_date:
            df_orders = df_orders[df_orders['日期'] >= pd.to_datetime(start_date).date()]
        if end_date:
            df_orders = df_orders[df_orders['日期'] <= pd.to_datetime(end_date).date()]

        df_merged = df_items.merge(df_orders[['订单ID']], on='订单ID')

        cat = df_merged.groupby('商品类别').agg({
            '商品金额': 'sum',
            '商品成本': 'sum',
            '数量': 'sum',
            '订单ID': 'nunique'
        }).reset_index()
        cat['利润'] = cat['商品金额'] - cat['商品成本']
        cat['利润率'] = cat['利润'] / cat['商品金额']
        cat.columns = ['商品类别', '销售额', '成本', '销量', '订单数', '利润', '利润率']
        return cat.sort_values('销售额', ascending=False).reset_index(drop=True)

    def get_region_sales(self, start_date=None, end_date=None):
        if start_date is None and end_date is None:
            return self.region_sales.copy()

        df = self.df_completed.copy()
        if start_date:
            df = df[df['日期'] >= pd.to_datetime(start_date).date()]
        if end_date:
            df = df[df['日期'] <= pd.to_datetime(end_date).date()]

        rs = df.groupby('省份').agg({
            '订单总金额': 'sum',
            '订单利润': 'sum',
            '订单ID': 'count',
            '用户ID': 'nunique'
        }).reset_index()
        rs.columns = ['省份', '销售额', '利润', '订单数', '客户数']
        return rs.sort_values('销售额', ascending=False).reset_index(drop=True)

    def get_user_analysis(self):
        return self.user_stats.copy()

    def get_member_level_stats(self):
        return self.member_stats.copy()

    def get_age_gender_analysis(self):
        user_stats = self.user_stats.copy()

        bins = [0, 18, 25, 35, 45, 55, 100]
        labels = ['18岁以下', '18-25岁', '26-35岁', '36-45岁', '46-55岁', '55岁以上']
        user_stats['年龄段'] = pd.cut(user_stats['年龄'], bins=bins, labels=labels, right=True)

        age_stats = user_stats.groupby('年龄段').agg({
            '用户ID': 'count',
            '消费总额': 'sum',
            '贡献利润': 'sum'
        }).reset_index()
        age_stats.columns = ['年龄段', '用户数', '消费总额', '贡献利润']

        gender_stats = user_stats.groupby('性别').agg({
            '用户ID': 'count',
            '消费总额': 'sum',
            '贡献利润': 'sum'
        }).reset_index()
        gender_stats.columns = ['性别', '用户数', '消费总额', '贡献利润']

        return age_stats, gender_stats

    def get_top_products(self, top_n=10, start_date=None, end_date=None):
        df_items = self.df_order_items.copy()

        if start_date or end_date:
            df_orders = self.df_completed[['订单ID', '日期']].copy()
            if start_date:
                df_orders = df_orders[df_orders['日期'] >= pd.to_datetime(start_date).date()]
            if end_date:
                df_orders = df_orders[df_orders['日期'] <= pd.to_datetime(end_date).date()]
            df_items = df_items.merge(df_orders[['订单ID']], on='订单ID')
        else:
            df_items = df_items.merge(self.df_completed[['订单ID']], on='订单ID')

        top = df_items.groupby(['商品ID', '商品名称', '商品类别']).agg({
            '商品金额': 'sum',
            '数量': 'sum',
            '商品成本': 'sum',
            '订单ID': 'nunique'
        }).reset_index()
        top['利润'] = top['商品金额'] - top['商品成本']
        top['利润率'] = top['利润'] / top['商品金额']
        top.columns = ['商品ID', '商品名称', '商品类别', '销售额', '销量', '成本', '订单数', '利润', '利润率']
        return top.sort_values('销售额', ascending=False).head(top_n).reset_index(drop=True)

    def get_payment_method_stats(self, start_date=None, end_date=None):
        if start_date is None and end_date is None:
            return self.pay_stats.copy()

        df = self.df_completed.copy()
        if start_date:
            df = df[df['日期'] >= pd.to_datetime(start_date).date()]
        if end_date:
            df = df[df['日期'] <= pd.to_datetime(end_date).date()]

        ps = df.groupby('支付方式').agg({
            '订单总金额': 'sum',
            '订单ID': 'count'
        }).reset_index()
        ps.columns = ['支付方式', '销售额', '订单数']
        ps['占比'] = ps['销售额'] / ps['销售额'].sum()
        return ps.sort_values('销售额', ascending=False).reset_index(drop=True)

    def get_hourly_trend(self, start_date=None, end_date=None):
        if start_date is None and end_date is None:
            return self.hourly.copy()

        df = self.df_completed.copy()
        if start_date:
            df = df[df['日期'] >= pd.to_datetime(start_date).date()]
        if end_date:
            df = df[df['日期'] <= pd.to_datetime(end_date).date()]

        h = df.groupby('小时').agg({
            '订单总金额': 'sum',
            '订单ID': 'count'
        }).reset_index()
        h.columns = ['小时', '销售额', '订单数']
        return h.sort_values('小时').reset_index(drop=True)

    def get_weekly_trend(self, start_date=None, end_date=None):
        if start_date is None and end_date is None:
            return self.weekly.copy()

        df = self.df_completed.copy()
        if start_date:
            df = df[df['日期'] >= pd.to_datetime(start_date).date()]
        if end_date:
            df = df[df['日期'] <= pd.to_datetime(end_date).date()]

        weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        weekday_cn = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        w = df.groupby('星期').agg({
            '订单总金额': 'sum',
            '订单ID': 'count'
        }).reset_index()
        w.columns = ['星期', '销售额', '订单数']
        w['星期_en'] = pd.Categorical(w['星期'], categories=weekday_order, ordered=True)
        w = w.sort_values('星期_en').reset_index(drop=True)
        w['星期'] = weekday_cn
        return w.drop('星期_en', axis=1)
