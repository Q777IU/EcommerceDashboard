import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from modules.data_analyzer import DataAnalyzer

st.set_page_config(
    page_title='电商数据可视化平台',
    page_icon='📊',
    layout='wide',
    initial_sidebar_state='expanded'
)

st.markdown("""
<style>
    .main-header { font-size: 2rem; font-weight: bold; color: #1f77b4; margin-bottom: 1rem; }
    .metric-card { background-color: #f8f9fa; border-radius: 10px; padding: 1rem; text-align: center; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); }
    .metric-value { font-size: 1.8rem; font-weight: bold; color: #2c3e50; }
    .metric-label { font-size: 0.9rem; color: #7f8c8d; margin-top: 0.3rem; }
    .section-title { font-size: 1.3rem; font-weight: bold; color: #34495e; margin: 1rem 0 0.5rem 0; padding-bottom: 0.5rem; border-bottom: 2px solid #3498db; }
</style>
""", unsafe_allow_html=True)

@st.cache_resource(show_spinner=False)
def get_analyzer():
    with st.spinner('正在加载数据，请稍候...'):
        return DataAnalyzer(data_dir=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data'))

analyzer = get_analyzer()

st.sidebar.title('📊 电商数据可视化平台')
st.sidebar.markdown('---')

page = st.sidebar.radio(
    '功能导航',
    ['📈 整体概况', '💰 销售分析', '👥 用户分析', '📦 商品分析', '🌍 地区分析', '⏰ 时段分析']
)

st.sidebar.markdown('---')
st.sidebar.subheader('时间筛选')

min_date = analyzer.df_orders['日期'].min()
max_date = analyzer.df_orders['日期'].max()

start_date = st.sidebar.date_input('开始日期', min_date, min_value=min_date, max_value=max_date)
end_date = st.sidebar.date_input('结束日期', max_date, min_value=min_date, max_value=max_date)

if start_date > end_date:
    st.sidebar.error('开始日期不能晚于结束日期')

st.sidebar.markdown('---')
st.sidebar.info(f'数据周期：{min_date} 至 {max_date}')


def format_number(num):
    if num >= 100000000:
        return f'{num/100000000:.2f}亿'
    elif num >= 10000:
        return f'{num/10000:.2f}万'
    else:
        return f'{num:,.2f}'


def show_overview():
    st.markdown('<div class="main-header">📈 整体概况</div>', unsafe_allow_html=True)

    with st.spinner('正在计算核心指标...'):
        stats = analyzer.get_overview_stats(start_date, end_date)

    cols = st.columns(4)
    metrics = [
        ('总销售额', f'¥{format_number(stats["总销售额"])}'),
        ('总利润', f'¥{format_number(stats["总利润"])}'),
        ('总订单数', format_number(stats['总订单数'])),
        ('客户数', format_number(stats['客户数'])),
    ]
    for col, (label, value) in zip(cols, metrics):
        col.markdown(f'<div class="metric-card"><div class="metric-value">{value}</div><div class="metric-label">{label}</div></div>', unsafe_allow_html=True)

    cols2 = st.columns(4)
    profit_rate = stats['总利润'] / stats['总销售额'] if stats['总销售额'] > 0 else 0
    avg_items = stats['总订单数'] / stats['客户数'] if stats['客户数'] > 0 else 0
    metrics2 = [
        ('客单价', f'¥{format_number(stats["客单价"])}'),
        ('利润率', f'{profit_rate:.2%}'),
        ('订单完成率', f'{stats["转化率"]:.2%}'),
        ('人均订单数', f'{avg_items:.1f}'),
    ]
    for col, (label, value) in zip(cols2, metrics2):
        col.markdown(f'<div class="metric-card"><div class="metric-value">{value}</div><div class="metric-label">{label}</div></div>', unsafe_allow_html=True)

    st.markdown('')
    st.markdown('<div class="section-title">📊 销售趋势</div>', unsafe_allow_html=True)

    with st.spinner('正在渲染图表...'):
        trend_daily = analyzer.get_sales_trend('daily', start_date, end_date)

        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.08,
            subplot_titles=('销售额趋势', '订单数趋势')
        )
        fig.add_trace(go.Scatter(
            x=trend_daily['日期'], y=trend_daily['销售额'],
            mode='lines', name='销售额', line=dict(color='#1f77b4', width=1.5),
            fill='tozeroy', fillcolor='rgba(31,119,180,0.1)'
        ), row=1, col=1)
        fig.add_trace(go.Bar(
            x=trend_daily['日期'], y=trend_daily['订单数'],
            name='订单数', marker_color='#2ecc71'
        ), row=2, col=1)
        fig.update_layout(height=450, showlegend=False, hovermode='x unified')
        st.plotly_chart(fig, width='stretch')

    st.markdown('<div class="section-title">🗓️ 月度销售对比</div>', unsafe_allow_html=True)

    with st.spinner('正在渲染图表...'):
        trend_monthly = analyzer.get_sales_trend('monthly', start_date, end_date)

        fig_monthly = go.Figure()
        fig_monthly.add_trace(go.Bar(
            x=trend_monthly['月份'], y=trend_monthly['销售额'],
            name='销售额', marker_color='#3498db'
        ))
        fig_monthly.add_trace(go.Scatter(
            x=trend_monthly['月份'], y=trend_monthly['利润'],
            name='利润', mode='lines+markers',
            line=dict(color='#e74c3c', width=2), marker=dict(size=6), yaxis='y2'
        ))
        fig_monthly.update_layout(
            xaxis=dict(title='月份'),
            yaxis=dict(title='销售额', side='left'),
            yaxis2=dict(title='利润', side='right', overlaying='y'),
            height=380, hovermode='x unified',
            legend=dict(x=0.02, y=0.98)
        )
        st.plotly_chart(fig_monthly, width='stretch')


def show_sales_analysis():
    st.markdown('<div class="main-header">💰 销售分析</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-title">品类销售占比</div>', unsafe_allow_html=True)
        with st.spinner('加载中...'):
            category_sales = analyzer.get_category_sales(start_date, end_date)
        fig_pie = px.pie(category_sales, values='销售额', names='商品类别',
                         hole=0.4, color_discrete_sequence=px.colors.qualitative.Set3)
        fig_pie.update_layout(height=380, legend=dict(orientation='h', yanchor='bottom', y=-0.1))
        st.plotly_chart(fig_pie, width='stretch')

    with col2:
        st.markdown('<div class="section-title">品类销售排行</div>', unsafe_allow_html=True)
        with st.spinner('加载中...'):
            category_sales = analyzer.get_category_sales(start_date, end_date)
        fig_bar = px.bar(category_sales, x='商品类别', y='销售额', color='利润率',
                         color_continuous_scale='RdYlGn', text_auto='.2s')
        fig_bar.update_layout(height=380, xaxis_tickangle=-30)
        st.plotly_chart(fig_bar, width='stretch')

    st.markdown('<div class="section-title">📊 品类详细数据</div>', unsafe_allow_html=True)
    with st.spinner('加载中...'):
        category_sales = analyzer.get_category_sales(start_date, end_date)
    display_df = category_sales.copy()
    display_df['销售额'] = display_df['销售额'].apply(lambda x: f'¥{x:,.2f}')
    display_df['成本'] = display_df['成本'].apply(lambda x: f'¥{x:,.2f}')
    display_df['利润'] = display_df['利润'].apply(lambda x: f'¥{x:,.2f}')
    display_df['利润率'] = display_df['利润率'].apply(lambda x: f'{x:.2%}')
    display_df['销量'] = display_df['销量'].apply(lambda x: f'{x:,}')
    display_df['订单数'] = display_df['订单数'].apply(lambda x: f'{x:,}')
    st.dataframe(display_df, width='stretch', hide_index=True)

    st.markdown('')
    st.markdown('<div class="section-title">💳 支付方式分布</div>', unsafe_allow_html=True)
    col3, col4 = st.columns(2)
    with col3:
        with st.spinner('加载中...'):
            pay_stats = analyzer.get_payment_method_stats(start_date, end_date)
        fig_pay = px.pie(pay_stats, values='销售额', names='支付方式',
                         color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_pay.update_layout(height=350)
        st.plotly_chart(fig_pay, width='stretch')
    with col4:
        with st.spinner('加载中...'):
            pay_stats = analyzer.get_payment_method_stats(start_date, end_date)
        fig_pay_bar = px.bar(pay_stats, x='支付方式', y='订单数',
                             color='销售额', color_continuous_scale='Blues', text_auto='.2s')
        fig_pay_bar.update_layout(height=350)
        st.plotly_chart(fig_pay_bar, width='stretch')


def show_user_analysis():
    st.markdown('<div class="main-header">👥 用户分析</div>', unsafe_allow_html=True)

    with st.spinner('正在加载用户数据...'):
        user_stats = analyzer.get_user_analysis()
        member_stats = analyzer.get_member_level_stats()
        age_stats, gender_stats = analyzer.get_age_gender_analysis()

    col1, col2, col3, col4 = st.columns(4)
    col1.markdown(f'<div class="metric-card"><div class="metric-value">{len(user_stats):,}</div><div class="metric-label">付费用户数</div></div>', unsafe_allow_html=True)
    col2.markdown(f'<div class="metric-card"><div class="metric-value">¥{user_stats["消费总额"].mean():,.2f}</div><div class="metric-label">人均消费</div></div>', unsafe_allow_html=True)
    col3.markdown(f'<div class="metric-card"><div class="metric-value">{user_stats["订单数"].mean():.2f}</div><div class="metric-label">人均订单数</div></div>', unsafe_allow_html=True)
    col4.markdown(f'<div class="metric-card"><div class="metric-value">¥{format_number(user_stats["贡献利润"].sum())}</div><div class="metric-label">用户贡献利润</div></div>', unsafe_allow_html=True)

    st.markdown('')
    col5, col6 = st.columns(2)
    with col5:
        st.markdown('<div class="section-title">会员等级分布</div>', unsafe_allow_html=True)
        fig_member = px.pie(member_stats, values='客户数', names='会员等级',
                            hole=0.5, color_discrete_sequence=px.colors.qualitative.Set2)
        fig_member.update_layout(height=380)
        st.plotly_chart(fig_member, width='stretch')
    with col6:
        st.markdown('<div class="section-title">会员等级销售贡献</div>', unsafe_allow_html=True)
        fig_member_bar = px.bar(member_stats, x='会员等级', y='总销售额',
                                color='客单价', color_continuous_scale='Viridis', text_auto='.2s')
        fig_member_bar.update_layout(height=380)
        st.plotly_chart(fig_member_bar, width='stretch')

    st.markdown('')
    col7, col8 = st.columns(2)
    with col7:
        st.markdown('<div class="section-title">性别消费分布</div>', unsafe_allow_html=True)
        fig_gender = px.bar(gender_stats, x='性别', y=['消费总额', '贡献利润'],
                            barmode='group', color_discrete_sequence=['#3498db', '#e74c3c'], text_auto='.2s')
        fig_gender.update_layout(height=350, legend_title='指标')
        st.plotly_chart(fig_gender, width='stretch')
    with col8:
        st.markdown('<div class="section-title">年龄段分布</div>', unsafe_allow_html=True)
        fig_age = px.bar(age_stats, x='年龄段', y='用户数',
                         color='消费总额', color_continuous_scale='RdBu', text_auto=True)
        fig_age.update_layout(height=350)
        st.plotly_chart(fig_age, width='stretch')

    st.markdown('<div class="section-title">🏆 消费TOP用户</div>', unsafe_allow_html=True)
    top_users = user_stats.sort_values('消费总额', ascending=False).head(20).reset_index(drop=True)
    top_users_display = top_users[['用户ID', '性别', '年龄', '省份', '会员等级', '消费总额', '订单数', '贡献利润']].copy()
    top_users_display['消费总额'] = top_users_display['消费总额'].apply(lambda x: f'¥{x:,.2f}')
    top_users_display['贡献利润'] = top_users_display['贡献利润'].apply(lambda x: f'¥{x:,.2f}')
    st.dataframe(top_users_display, width='stretch', hide_index=True)


def show_product_analysis():
    st.markdown('<div class="main-header">📦 商品分析</div>', unsafe_allow_html=True)

    top_n = st.selectbox('商品排行数量', [10, 20, 30, 50], index=0)

    st.markdown(f'<div class="section-title">🏆 销售额TOP{top_n}商品</div>', unsafe_allow_html=True)
    with st.spinner('正在计算...'):
        top_products = analyzer.get_top_products(top_n, start_date, end_date)

    fig_top = px.bar(top_products.sort_values('销售额', ascending=True),
                     x='销售额', y='商品名称', color='商品类别',
                     orientation='h', text_auto='.2s',
                     color_discrete_sequence=px.colors.qualitative.Set3)
    fig_top.update_layout(
        height=max(350, top_n * 25),
        xaxis_title='销售额', yaxis_title='',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
    )
    st.plotly_chart(fig_top, width='stretch')

    st.markdown('<div class="section-title">📊 商品详细数据</div>', unsafe_allow_html=True)
    display_df = top_products.copy()
    display_df['销售额'] = display_df['销售额'].apply(lambda x: f'¥{x:,.2f}')
    display_df['成本'] = display_df['成本'].apply(lambda x: f'¥{x:,.2f}')
    display_df['利润'] = display_df['利润'].apply(lambda x: f'¥{x:,.2f}')
    display_df['利润率'] = display_df['利润率'].apply(lambda x: f'{x:.2%}')
    display_df['销量'] = display_df['销量'].apply(lambda x: f'{x:,}')
    display_df['订单数'] = display_df['订单数'].apply(lambda x: f'{x:,}')
    st.dataframe(display_df, width='stretch', hide_index=True)

    st.markdown('')
    col3, col4 = st.columns(2)
    with col3:
        st.markdown('<div class="section-title">品类销量对比</div>', unsafe_allow_html=True)
        with st.spinner('加载中...'):
            category_sales = analyzer.get_category_sales(start_date, end_date)
        fig_qty = px.bar(category_sales, x='商品类别', y='销量',
                         color='利润率', color_continuous_scale='Greens', text_auto='.2s')
        fig_qty.update_layout(height=350, xaxis_tickangle=-30)
        st.plotly_chart(fig_qty, width='stretch')
    with col4:
        st.markdown('<div class="section-title">利润-销量散点图</div>', unsafe_allow_html=True)
        fig_scatter = px.scatter(top_products, x='销量', y='利润',
                                 size='销售额', color='商品类别',
                                 hover_data=['商品名称', '利润率'], size_max=40)
        fig_scatter.update_layout(height=350)
        st.plotly_chart(fig_scatter, width='stretch')


def show_region_analysis():
    st.markdown('<div class="main-header">🌍 地区分析</div>', unsafe_allow_html=True)

    with st.spinner('正在加载地区数据...'):
        region_sales = analyzer.get_region_sales(start_date, end_date)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-title">省份销售额排行</div>', unsafe_allow_html=True)
        fig_region = px.bar(region_sales.sort_values('销售额', ascending=True),
                            x='销售额', y='省份', orientation='h',
                            color='客户数', color_continuous_scale='Blues', text_auto='.2s')
        fig_region.update_layout(height=500, xaxis_title='销售额', yaxis_title='')
        st.plotly_chart(fig_region, width='stretch')
    with col2:
        st.markdown('<div class="section-title">销售额占比</div>', unsafe_allow_html=True)
        top10 = region_sales.head(10).copy()
        if len(region_sales) > 10:
            others = pd.DataFrame({'省份': ['其他'], '销售额': [region_sales.iloc[10:]['销售额'].sum()]})
            top10 = pd.concat([top10, others], ignore_index=True)
        fig_region_pie = px.pie(top10, values='销售额', names='省份',
                                color_discrete_sequence=px.colors.qualitative.Pastel2)
        fig_region_pie.update_layout(height=500)
        st.plotly_chart(fig_region_pie, width='stretch')

    st.markdown('<div class="section-title">📊 地区详细数据</div>', unsafe_allow_html=True)
    display_df = region_sales.copy()
    display_df['销售额'] = display_df['销售额'].apply(lambda x: f'¥{x:,.2f}')
    display_df['利润'] = display_df['利润'].apply(lambda x: f'¥{x:,.2f}')
    display_df['订单数'] = display_df['订单数'].apply(lambda x: f'{x:,}')
    display_df['客户数'] = display_df['客户数'].apply(lambda x: f'{x:,}')
    st.dataframe(display_df, width='stretch', hide_index=True)


def show_time_analysis():
    st.markdown('<div class="main-header">⏰ 时段分析</div>', unsafe_allow_html=True)

    with st.spinner('正在加载时段数据...'):
        hourly = analyzer.get_hourly_trend(start_date, end_date)
        weekly = analyzer.get_weekly_trend(start_date, end_date)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-title">24小时销售分布</div>', unsafe_allow_html=True)
        fig_hourly = go.Figure()
        fig_hourly.add_trace(go.Bar(
            x=hourly['小时'], y=hourly['销售额'], name='销售额',
            marker_color='#3498db', opacity=0.7
        ))
        fig_hourly.add_trace(go.Scatter(
            x=hourly['小时'], y=hourly['订单数'], name='订单数',
            mode='lines+markers', line=dict(color='#e74c3c', width=2), yaxis='y2'
        ))
        fig_hourly.update_layout(
            height=350, xaxis=dict(title='小时', dtick=1),
            yaxis=dict(title='销售额', side='left'),
            yaxis2=dict(title='订单数', side='right', overlaying='y'),
            hovermode='x unified', legend=dict(x=0.02, y=0.98)
        )
        st.plotly_chart(fig_hourly, width='stretch')
    with col2:
        st.markdown('<div class="section-title">星期销售分布</div>', unsafe_allow_html=True)
        fig_weekly = go.Figure()
        fig_weekly.add_trace(go.Bar(
            x=weekly['星期'], y=weekly['销售额'], name='销售额',
            marker_color='#2ecc71', opacity=0.7
        ))
        fig_weekly.add_trace(go.Scatter(
            x=weekly['星期'], y=weekly['订单数'], name='订单数',
            mode='lines+markers', line=dict(color='#9b59b6', width=2), yaxis='y2'
        ))
        fig_weekly.update_layout(
            height=350, xaxis=dict(title='星期'),
            yaxis=dict(title='销售额', side='left'),
            yaxis2=dict(title='订单数', side='right', overlaying='y'),
            hovermode='x unified', legend=dict(x=0.02, y=0.98)
        )
        st.plotly_chart(fig_weekly, width='stretch')

    st.markdown('')
    st.markdown('<div class="section-title">📈 销售趋势（日粒度）</div>', unsafe_allow_html=True)
    with st.spinner('正在渲染...'):
        trend_daily = analyzer.get_sales_trend('daily', start_date, end_date)
    fig_daily = make_subplots(
        rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.05,
        subplot_titles=('销售额', '利润', '订单数')
    )
    fig_daily.add_trace(go.Scatter(
        x=trend_daily['日期'], y=trend_daily['销售额'], mode='lines',
        line=dict(color='#1f77b4', width=1.5),
        fill='tozeroy', fillcolor='rgba(31,119,180,0.1)'
    ), row=1, col=1)
    fig_daily.add_trace(go.Scatter(
        x=trend_daily['日期'], y=trend_daily['利润'], mode='lines',
        line=dict(color='#2ecc71', width=1.5),
        fill='tozeroy', fillcolor='rgba(46,204,113,0.1)'
    ), row=2, col=1)
    fig_daily.add_trace(go.Bar(
        x=trend_daily['日期'], y=trend_daily['订单数'], marker_color='#e74c3c'
    ), row=3, col=1)
    fig_daily.update_layout(height=600, showlegend=False, hovermode='x unified')
    st.plotly_chart(fig_daily, width='stretch')


if page == '📈 整体概况':
    show_overview()
elif page == '💰 销售分析':
    show_sales_analysis()
elif page == '👥 用户分析':
    show_user_analysis()
elif page == '📦 商品分析':
    show_product_analysis()
elif page == '🌍 地区分析':
    show_region_analysis()
elif page == '⏰ 时段分析':
    show_time_analysis()

st.markdown('---')
st.caption('📊 电商数据可视化平台 | 数据仅供演示使用')
