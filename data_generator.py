import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import os

random.seed(42)
np.random.seed(42)

def generate_data(output_dir='data'):
    os.makedirs(output_dir, exist_ok=True)
    
    categories = ['电子产品', '服装鞋帽', '家居用品', '食品饮料', '美妆护肤', '运动户外', '母婴用品', '图书文具']
    subcategories = {
        '电子产品': ['手机', '电脑', '耳机', '平板', '智能手表'],
        '服装鞋帽': ['男装', '女装', '童装', '运动鞋', '箱包'],
        '家居用品': ['家具', '厨具', '床上用品', '灯具', '收纳'],
        '食品饮料': ['零食', '饮料', '生鲜', '粮油', '保健品'],
        '美妆护肤': ['护肤', '彩妆', '香水', '洗护', '美容工具'],
        '运动户外': ['健身器材', '户外装备', '运动服饰', '球类运动', '游泳用品'],
        '母婴用品': ['奶粉', '纸尿裤', '婴儿车', '玩具', '童装'],
        '图书文具': ['小说', '教材', '文具', '办公用品', '乐器']
    }
    
    provinces = ['北京', '上海', '广东', '江苏', '浙江', '山东', '四川', '湖北', '湖南', '福建',
                 '河南', '河北', '安徽', '辽宁', '陕西', '江西', '重庆', '云南', '广西', '山西']
    
    cities = {
        '北京': ['北京市'],
        '上海': ['上海市'],
        '广东': ['广州', '深圳', '东莞', '佛山'],
        '江苏': ['南京', '苏州', '无锡', '常州'],
        '浙江': ['杭州', '宁波', '温州', '嘉兴'],
        '山东': ['济南', '青岛', '烟台', '潍坊'],
        '四川': ['成都', '绵阳', '德阳', '宜宾'],
        '湖北': ['武汉', '宜昌', '襄阳', '荆州'],
        '湖南': ['长沙', '株洲', '湘潭', '衡阳'],
        '福建': ['福州', '厦门', '泉州', '漳州'],
        '河南': ['郑州', '洛阳', '开封', '新乡'],
        '河北': ['石家庄', '唐山', '邯郸', '保定'],
        '安徽': ['合肥', '芜湖', '蚌埠', '马鞍山'],
        '辽宁': ['沈阳', '大连', '鞍山', '抚顺'],
        '陕西': ['西安', '咸阳', '宝鸡', '渭南'],
        '江西': ['南昌', '赣州', '九江', '吉安'],
        '重庆': ['重庆市'],
        '云南': ['昆明', '大理', '丽江', '玉溪'],
        '广西': ['南宁', '柳州', '桂林', '梧州'],
        '山西': ['太原', '大同', '运城', '临汾']
    }
    
    products = []
    product_id = 10001
    for cat in categories:
        for sub in subcategories[cat]:
            for i in range(random.randint(8, 15)):
                base_price = random.uniform(20, 5000)
                products.append({
                    '商品ID': f'P{product_id}',
                    '商品名称': f'{sub}商品{i+1}',
                    '商品类别': cat,
                    '商品子类': sub,
                    '原价': round(base_price, 2),
                    '成本价': round(base_price * random.uniform(0.3, 0.6), 2),
                    '库存': random.randint(100, 5000),
                    '上架时间': (datetime(2025, 1, 1) + timedelta(days=random.randint(0, 200))).strftime('%Y-%m-%d')
                })
                product_id += 1
    
    df_products = pd.DataFrame(products)
    df_products.to_excel(os.path.join(output_dir, '商品数据.xlsx'), index=False)
    print(f'已生成 {len(df_products)} 条商品数据')
    
    users = []
    user_id = 100001
    for i in range(5000):
        province = random.choice(provinces)
        city = random.choice(cities[province])
        age = random.randint(16, 65)
        gender = random.choice(['男', '女'])
        register_date = datetime(2024, 1, 1) + timedelta(days=random.randint(0, 540))
        level = random.choices(['普通会员', '银卡会员', '金卡会员', '钻石会员'], weights=[60, 25, 10, 5])[0]
        
        users.append({
            '用户ID': f'U{user_id}',
            '用户名': f'用户{user_id}',
            '性别': gender,
            '年龄': age,
            '省份': province,
            '城市': city,
            '注册时间': register_date.strftime('%Y-%m-%d'),
            '会员等级': level,
            '手机号': f'1{random.choice([3,5,7,8,9])}{random.randint(100000000, 999999999)}'
        })
        user_id += 1
    
    df_users = pd.DataFrame(users)
    df_users.to_excel(os.path.join(output_dir, '用户数据.xlsx'), index=False)
    print(f'已生成 {len(df_users)} 条用户数据')
    
    orders = []
    order_items = []
    order_id = 2025000001
    
    start_date = datetime(2025, 1, 1)
    end_date = datetime(2026, 6, 30)
    total_days = (end_date - start_date).days
    
    for day in range(total_days + 1):
        current_date = start_date + timedelta(days=day)
        date_str = current_date.strftime('%Y-%m-%d')
        
        month_factor = 1 + 0.3 * np.sin(2 * np.pi * (current_date.month - 1) / 12 + np.pi)
        weekend_factor = 1.2 if current_date.weekday() >= 5 else 1.0
        daily_orders = int(random.randint(80, 200) * month_factor * weekend_factor)
        
        for _ in range(daily_orders):
            user = random.choice(users)
            order_date = current_date + timedelta(
                hours=random.randint(8, 22),
                minutes=random.randint(0, 59),
                seconds=random.randint(0, 59)
            )
            
            num_items = random.randint(1, 5)
            selected_products = random.sample(products, num_items)
            
            total_amount = 0
            total_cost = 0
            
            for prod in selected_products:
                quantity = random.randint(1, 3)
                discount = random.uniform(0.7, 1.0)
                unit_price = round(prod['原价'] * discount, 2)
                item_amount = round(unit_price * quantity, 2)
                item_cost = round(prod['成本价'] * quantity, 2)
                
                total_amount += item_amount
                total_cost += item_cost
                
                order_items.append({
                    '订单ID': f'O{order_id}',
                    '商品ID': prod['商品ID'],
                    '商品名称': prod['商品名称'],
                    '商品类别': prod['商品类别'],
                    '商品子类': prod['商品子类'],
                    '单价': unit_price,
                    '数量': quantity,
                    '商品金额': item_amount,
                    '商品成本': item_cost
                })
            
            shipping_fee = 0 if total_amount > 99 else random.choice([0, 8, 12, 15])
            discount_amount = round(total_amount * random.uniform(0, 0.1), 2)
            final_amount = round(total_amount + shipping_fee - discount_amount, 2)
            profit = round(total_amount - total_cost - shipping_fee, 2)
            
            pay_methods = ['支付宝', '微信支付', '银行卡', '货到付款']
            pay_method = random.choices(pay_methods, weights=[40, 35, 20, 5])[0]
            
            statuses = ['已完成', '待收货', '已取消', '退款中']
            status = random.choices(statuses, weights=[85, 8, 4, 3])[0]
            
            orders.append({
                '订单ID': f'O{order_id}',
                '用户ID': user['用户ID'],
                '会员等级': user['会员等级'],
                '省份': user['省份'],
                '城市': user['城市'],
                '下单时间': order_date.strftime('%Y-%m-%d %H:%M:%S'),
                '商品数量': num_items,
                '商品总金额': round(total_amount, 2),
                '运费': shipping_fee,
                '优惠金额': discount_amount,
                '订单总金额': final_amount,
                '订单成本': round(total_cost, 2),
                '订单利润': profit,
                '支付方式': pay_method,
                '订单状态': status
            })
            
            order_id += 1
    
    df_orders = pd.DataFrame(orders)
    df_order_items = pd.DataFrame(order_items)
    
    df_orders.to_excel(os.path.join(output_dir, '订单数据.xlsx'), index=False)
    df_order_items.to_excel(os.path.join(output_dir, '订单明细.xlsx'), index=False)
    
    print(f'已生成 {len(df_orders)} 条订单数据')
    print(f'已生成 {len(df_order_items)} 条订单明细数据')
    
    print('\n数据生成完成！文件保存在', output_dir, '目录下')

if __name__ == '__main__':
    generate_data()
