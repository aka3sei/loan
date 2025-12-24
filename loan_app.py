import streamlit as st
import numpy as np
import pandas as pd

# --- 1. ページ設定とスタイル（これまでのアプリと統一） ---
st.set_page_config(page_title="AI住宅ローン借り換え診断", layout="centered")

hide_st_style = """
    <style>
    header[data-testid="stHeader"] { visibility: hidden; display: none; }
    footer { visibility: hidden; }
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 7rem !important;
    }
    h1 { margin-top: 0px !important; }
    /* 診断カードのデザイン */
    .result-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 15px;
        border: 2px solid #28a745;
        text-align: center;
        margin: 10px 0;
    }
    .savings-amount {
        font-size: 2.5rem;
        font-weight: bold;
        color: #28a745;
    }
    </style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

# --- 2. 住宅ローン計算関数 ---
def calculate_monthly_payment(principal, annual_interest_rate, months):
    if annual_interest_rate == 0:
        return principal / months
    monthly_rate = annual_interest_rate / 12 / 100
    return principal * monthly_rate * (1 + monthly_rate)**months / ((1 + monthly_rate)**months - 1)

# --- 3. メイン画面 ---
st.title("🏦 AI住宅ローン借り換え診断")
st.caption("現在のローンと新しい条件を比較し、削減できる金額を算出します。")

# 入力フォーム
with st.expander("📝 現在のローンの条件を入力", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        current_balance = st.number_input("ローン残高 (万円)", min_value=100, max_value=20000, value=3000, step=100)
        current_rate = st.number_input("現在の金利 (%)", min_value=0.1, max_value=5.0, value=1.2, step=0.01, format="%.2f")
    with col2:
        remaining_years = st.slider("残り期間 (年)", 1, 35, 20)
        remaining_months = remaining_years * 12

with st.expander("✨ 借り換え後の条件を入力", expanded=True):
    col3, col4 = st.columns(2)
    with col3:
        new_rate = st.number_input("借り換え後の金利 (%)", min_value=0.1, max_value=5.0, value=0.45, step=0.01, format="%.2f")
    with col4:
        costs = st.number_input("諸費用（手数料など） (万円)", min_value=0, max_value=500, value=60)

# --- 4. 診断ロジック ---
current_monthly = calculate_monthly_payment(current_balance * 10000, current_rate, remaining_months)
new_monthly = calculate_monthly_payment(current_balance * 10000, new_rate, remaining_months)

monthly_savings = current_monthly - new_monthly
total_savings = (monthly_savings * remaining_months) - (costs * 10000)

# 診断ボタン
st.write("")
if st.button("📊 借り換えメリットを診断する", use_container_width=True):
    st.divider()
    
    if total_savings > 0:
        st.balloons()
        st.subheader("🎉 借り換えメリットがあります！")
        
        # メリット総額の表示
        st.markdown(f"""
            <div class="result-card">
                <p>総返済額の削減（諸費用引後）</p>
                <p class="savings-amount">約 {round(total_savings / 10000):,} 万円</p>
            </div>
        """, unsafe_allow_html=True)
        
        # 詳細メトリクス
        m1, m2 = st.columns(2)
        m1.metric("毎月の返済軽減額", f"{round(monthly_savings):,} 円")
        m2.metric("総削減額 (期間全体)", f"{round((monthly_savings * remaining_months)/10000):,} 万円")
        
        st.success(f"💡 毎月 {round(monthly_savings):,} 円、余裕が生まれます。")
    else:
        st.warning("⚠️ 現在の条件では、諸費用を含めると借り換えメリットが出ない可能性があります。")

    # グラフ表示（比較）
    chart_data = pd.DataFrame({
        "項目": ["現在", "借り換え後"],
        "総返済額 (万円)": [
            round((current_monthly * remaining_months) / 10000),
            round((new_monthly * remaining_months) / 10000 + costs)
        ]
    })
    st.bar_chart(chart_data, x="項目", y="総返済額 (万円)")