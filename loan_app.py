import streamlit as st
import numpy as np
import pandas as pd

# --- 1. ページ設定とスタイル ---
st.set_page_config(page_title="AI住宅ローン借り換え診断", layout="centered")

hide_st_style = """
    <style>
    header[data-testid="stHeader"] { visibility: hidden; display: none; }
    footer { visibility: hidden; }
    .block-container { padding-top: 2rem !important; padding-bottom: 7rem !important; }
    .result-card {
        background-color: #f8fafc;
        padding: 25px;
        border-radius: 15px;
        border: 2px solid #28a745;
        text-align: center;
        margin: 10px 0;
    }
    .savings-amount { font-size: 2.8rem; font-weight: bold; color: #28a745; margin: 10px 0; }
    .detail-label { color: #64748b; font-size: 0.9rem; }
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

# --- 4. 診断ロジック & 表示 ---
if st.button("📊 借り換えメリットを診断する", use_container_width=True):
    # 計算処理（ボタン押下後に実行）
    current_monthly = calculate_monthly_payment(current_balance * 10000, current_rate, remaining_months)
    new_monthly = calculate_monthly_payment(current_balance * 10000, new_rate, remaining_months)
    
    current_total_payment = current_monthly * remaining_months
    current_total_interest = current_total_payment - (current_balance * 10000)
    
    new_total_payment_pure = new_monthly * remaining_months
    new_total_interest = new_total_payment_pure - (current_balance * 10000)
    new_total_payment_with_costs = new_total_payment_pure + (costs * 10000)
    
    total_savings = current_total_payment - new_total_payment_with_costs
    interest_savings = current_total_interest - new_total_interest

    st.divider()
    
    if total_savings > 0:
        st.subheader("分析結果: 借り換えメリットが認められます")
        
        st.markdown(f"""
            <div class="result-card">
                <p class="detail-label">諸費用を差し引いた最終的な削減額</p>
                <p class="savings-amount">約 {round(total_savings / 10000):,} 万円</p>
                <p style="color:#1e293b;">毎月の返済額も <b>{round(current_monthly - new_monthly):,} 円</b> 軽減されます</p>
            </div>
        """, unsafe_allow_html=True)

        # 1. 支払総額の詳細比較表
        st.write("### 📉 支払内訳の徹底比較")
        df_comp = pd.DataFrame({
            "比較項目": ["総支払額 (諸費用込)", "利息の総額", "毎月の返済額", "諸費用合計"],
            "借り換え前": [
                f"{round(current_total_payment / 10000):,} 万円",
                f"{round(current_total_interest / 10000):,} 万円",
                f"{round(current_monthly):,} 円",
                "0 万円"
            ],
            "借り換え後": [
                f"{round(new_total_payment_with_costs / 10000):,} 万円",
                f"{round(new_total_interest / 10000):,} 万円",
                f"{round(new_monthly):,} 円",
                f"{costs:,} 万円"
            ],
            "差額 (メリット)": [
                f"- {round(total_savings / 10000):,} 万円",
                f"- {round(interest_savings / 10000):,} 万円",
                f"- {round(current_monthly - new_monthly):,} 円",
                f"+ {costs:,} 万円"
            ]
        })
        st.table(df_comp)

        # 2. 積み上げ棒グラフ
        st.write("### 📊 コスト構造の比較")
        chart_df = pd.DataFrame([
            {"ケース": "現在", "内訳": "1.元金残高", "金額(万円)": current_balance},
            {"ケース": "現在", "内訳": "2.利息総額", "金額(万円)": round(current_total_interest / 10000)},
            {"ケース": "借り換え", "内訳": "1.元金残高", "金額(万円)": current_balance},
            {"ケース": "借り換え", "内訳": "2.利息総額", "金額(万円)": round(new_total_interest / 10000)},
            {"ケース": "借り換え", "内訳": "3.諸費用", "金額(万円)": costs},
        ])
        st.bar_chart(chart_df, x="ケース", y="金額(万円)", color="内訳", stack=True)

        st.info(f"💡 借り換えにより、銀行へ支払う余分な利息が 約 **{round(interest_savings/10000):,} 万円** 削減されます。")

    else:
        st.warning("⚠️ 諸費用(手数料)の負担が削減額を上回るため、現時点での借り換えメリットは薄いと判断されます。")
