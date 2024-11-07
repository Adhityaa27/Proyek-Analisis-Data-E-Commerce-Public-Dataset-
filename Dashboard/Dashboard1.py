#Library yang digunakan
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style="dark")

#Menyiapkan DataFrame
#Membuat beberapa helper function

#create_daily_orders_df() digunakan untuk menyiapkan daily_orders_df
def create_daily_orders_df(df):
    daily_orders_df= df.resample(rule='D',on= 'order_purchase_timestamp').agg({
        'order_id':'nunique',
        'payment_value':'sum'
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "order_id": "order_count",
        "payment_value": "revenue"
    }, inplace=True)
    return daily_orders_df

#create create_revenue_category_df() untuk menyiapkan revenue_category_df
def create_revenue_category_df(df):
    revenue_category_df= df.groupby(by='product_category_name_english').payment_value.sum().sort_values(ascending=False).reset_index()
    return revenue_category_df

#create create_bystate_df() untuk menyiapkan bystate_df
def create_bystate_df(df):
    bystate_df= df.groupby(by="customer_state").customer_id.nunique().reset_index()
    bystate_df.rename(columns={
    "customer_id": "customer_count"
    }, inplace=True)
    return bystate_df

#create_rfm_df() bertanggung jawab untuk menghasilkan rfm_df.
def create_rfm_df(df):
    rfm_df = all_df.groupby(by="customer_id", as_index=False).agg({
        "order_purchase_timestamp": "max", # mengambil tanggal order terakhir
        "order_id": "nunique", # menghitung jumlah order
        "payment_value": "sum" # menghitung jumlah revenue yang dihasilkan
    })
    rfm_df.columns = ["customer_id", "max_order_purchase_timestamp", "frequency", "monetary"]

# menghitung kapan terakhir pelanggan melakukan transaksi (hari)
    rfm_df["max_order_purchase_timestamp"] = rfm_df["max_order_purchase_timestamp"].dt.date
    recent_date = df["order_purchase_timestamp"].dt.date.max()
    rfm_df["recency"] = rfm_df["max_order_purchase_timestamp"].apply(lambda x: (recent_date - x).days)
 
    rfm_df.drop("max_order_purchase_timestamp", axis=1, inplace=True)
    return rfm_df

#load berkas all_data.csv
all_df = pd.read_csv("all_data_project1.csv")
datetime_columns = ["order_purchase_timestamp","order_delivered_carrier_date"]
all_df.sort_values(by='order_purchase_timestamp',inplace=True)
all_df.reset_index(inplace=True)

for column in datetime_columns:
    all_df[column]=pd.to_datetime(all_df[column])

#membuat konten filter
min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()

#masukkan logo
st.image(r"C:\Users\farha\Downloads\ecomerce.png")

# Mengambil start_date & end_date dari date_input
start_date, end_date = st.date_input(
    label= 'Rentang Waktu',
    min_value= min_date,
    max_value= max_date,
    value= [min_date,max_date]
)

#start_date dan end_date di atas akan digunakan untuk memfilter all_df.
#Data yang telah difilter ini selanjutnya akan disimpan dalam main_df
main_df= all_df[(all_df["order_purchase_timestamp"]>= str(start_date))&
                (all_df["order_purchase_timestamp"]<= str(end_date))]

#membuat berbagai df
daily_oreders_df = create_daily_orders_df(main_df)
revenue_category_df = create_revenue_category_df(main_df)
bystate_df = create_bystate_df(main_df)
rfm_df= create_rfm_df(main_df)

#MELENGKAPI DASHBOARD DENGAN BERBAGAI VISUALISASI DATA
#Membuat header
st.header("Brazillian E-Commerce Dashboard :sparkles:")

#menambahkan informasi terkait daily orders pada dashboard
#tiga informasi terkait daily orders, yaitu jumlah order harian serta total order dan revenue dalam range waktu tertentu
st.subheader("Daily Orders")
col1,col2 = st.columns(2)
with col1:
    total_orders = daily_oreders_df.order_count.sum()
    st.metric("Total Orders", value= total_orders)

with col2:
    total_revenue = format_currency(daily_oreders_df.revenue.sum(),"BRL",locale="es_CO")
    st.metric("Total Revenue", value= total_revenue)
    
fig, ax=plt.subplots(figsize = (16,8))
ax.plot(
    daily_oreders_df["order_purchase_timestamp"],
    daily_oreders_df["order_count"],
    marker = "o",
    linewidth = 2,
    color = "#90CAF9"
)
ax.tick_params(axis= 'y',labelsize= 20)
ax.tick_params(axis= 'x',labelsize= 15)

st.pyplot(fig)

#Menampilkan menampilkan 5 produk paling laris dan paling sedikit terjual melalui sebuah visualisasi data
st.subheader("Best and Worst Performing Product")

fig, ax = plt.subplots(nrows=1, ncols=2,figsize=(35,15))

colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

sns.barplot(
    x= "payment_value",
    y= "product_category_name_english",
    data= revenue_category_df.sort_values(by="payment_value", ascending=False).head(5),
    palette= colors,
    ax=ax[0]
)

ax[0].set_ylabel(None)
ax[0].set_xlabel("Million", fontsize= 30)
ax[0].set_title("Best Performing Product", loc= "center", fontsize= 50)
ax[0].tick_params(axis= 'y',labelsize= 35)
ax[0].tick_params(axis= 'x',labelsize= 30)

sns.barplot(
    x="payment_value",
    y="product_category_name_english",
    data= revenue_category_df.sort_values(by="payment_value", ascending=True).head(5),
    palette= colors,
    ax=ax[1] 
)
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Worst Performing Product", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize= 35)
ax[1].tick_params(axis= 'x',labelsize= 30)

st.pyplot(fig)

#Sub header demografi customer
st.subheader("Customer Demographics")
fig, ax = plt.subplots(figsize=(20,10))

colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

sns.barplot(
    x="customer_state", 
    y="customer_count",
    data=bystate_df.sort_values(by="customer_count", ascending=False),
    palette=colors,
    ax=ax
)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.set_title("Number of Customer by States", loc="center", fontsize=30)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
st.pyplot(fig)

#sub header RFM
st.subheader("Best Customer Based on RFM Parameters")

col1,col2,col3 = st.columns(3)

with col1:
    avg_recency = round(rfm_df.recency.mean(),1)
    st.metric("Average Recency (days)", value= avg_recency)

with col2:
    avg_frequency = round(rfm_df.frequency.mean(),2)
    st.metric("Average Frequency", value= avg_frequency)

with col3:
    avg_monetery= format_currency(rfm_df.monetary.mean(), "BRL",locale= "es_CO")
    st.metric("Average Monetary", value= avg_monetery)

fig, ax = plt.subplots(nrows=1,ncols=3,figsize=(35,15))
colors= ["#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9"]
 
#chart recency
sns.barplot(
    y="recency",
    x="customer_id",
    data= rfm_df.sort_values(by="recency",ascending=False).head(5),
    palette= colors,
    ax= ax[0]   
)
ax[0].set_ylabel(None)
ax[0].set_xlabel("customer_id",fontsize=30)
ax[0].set_title("By Recency (days)", loc= "center", fontsize= 50)
ax[0].tick_params(axis= "y", labelsize=30)
ax[0].tick_params(axis= "x", labelsize=35)

#chart Frequency
sns.barplot(
    y="frequency",
    x="customer_id",
    data= rfm_df.sort_values(by="frequency",ascending=False).head(5),
    palette= colors,
    ax= ax[1]   
)
ax[1].set_ylabel(None)
ax[1].set_xlabel("customer_id",fontsize=30)
ax[1].set_title("By Frequency", loc= "center", fontsize= 50)
ax[1].tick_params(axis= "y", labelsize=30)
ax[1].tick_params(axis= "x", labelsize=35)

#chart Monetory
sns.barplot(
    y="monetary",
    x="customer_id",
    data= rfm_df.sort_values(by="monetary",ascending=False).head(5),
    palette= colors,
    ax= ax[2]   
)
ax[2].set_ylabel(None)
ax[2].set_xlabel("customer_id",fontsize=30)
ax[2].set_title("By Monetary", loc= "center", fontsize= 50)
ax[2].tick_params(axis= "y", labelsize=30)
ax[2].tick_params(axis= "x", labelsize=35)

st.pyplot(fig)

#caption
st.caption("Copyright (c) Farhan 2024")