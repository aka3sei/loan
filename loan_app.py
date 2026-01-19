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
# 現在の条件
current_total_payment = current_monthly * remaining_months
current_total_interest = current_total_payment - (current_balance * 10000)

# 借り換え後の条件
new_total_payment_pure = new_monthly * remaining_months
new_total_interest = new_total_payment_pure - (current_balance * 10000)
new_total_payment_with_costs = new_total_payment_pure + (costs * 10000)

# 削減額
monthly_savings = current_monthly - new_monthly
total_savings = current_total_payment - new_total_payment_with_costs

# --- 5. 診断結果の表示 ---
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

        # --- 追加：詳細比較テーブル ---
        st.write("### 📉 返済計画の比較詳細")
        
        comparison_data = {
            "項目": ["毎月の返済額", "総返済額 (諸費用込)", "利息の総額", "諸費用"],
            "借り換え前": [
                f"{round(current_monthly):,} 円",
                f"{round(current_total_payment / 10000):,} 万円",
                f"{round(current_total_interest / 10000):,} 万円",
                "0 万円"
            ],
            "借り換え後": [
                f"{round(new_monthly):,} 円",
                f"{round(new_total_payment_with_costs / 10000):,} 万円",
                f"{round(new_total_interest / 10000):,} 万円",
                f"{costs:,} 万円"
            ],
            "差額": [
                f"- {round(monthly_savings):,} 円",
                f"- {round(total_savings / 10000):,} 万円",
                f"- {round((current_total_interest - new_total_interest) / 10000):,} 万円",
                f"+ {costs:,} 万円"
            ]
        }
        st.table(pd.DataFrame(comparison_data))

        # --- 追加：利息削減のインパクト ---
        interest_cut = round((current_total_interest - new_total_interest) / 10000)
        st.info(f"📢 借り換えによって、銀行に支払う**利息を 約 {interest_cut:,} 万円 減らす**ことができます。")

        # グラフ表示（積み上げ棒グラフにすると利息の差がわかりやすい）
        chart_df = pd.DataFrame([
            {"ケース": "現在", "内訳": "元金", "金額 (万円)": current_balance},
            {"ケース": "現在", "内訳": "利息", "金額 (万円)": round(current_total_interest / 10000)},
            {"ケース": "借り換え後", "内訳": "元金", "金額 (万円)": current_balance},
            {"ケース": "借り換え後", "内訳": "利息", "金額 (万円)": round(new_total_interest / 10000)},
            {"ケース": "借り換え後", "内訳": "諸費用", "金額 (万円)": costs},
        ])
        
        st.write("### 📊 総支払額の内訳比較")
        st.bar_chart(chart_df, x="ケース", y="金額 (万円)", color="内訳", stack=True)
        
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
