import time
from datetime import date

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from const import *
from risk_model import model

today = date.today()


def anti_collision_format_func(option):
    return ANTI_COLLISION[option]


def cross_object_format_func(option):
    return CROSS_OBJECT[option]


def run_with_format_func(option):
    return RUN_WITH[option]


def br_format_func(option):
    return BR_CHOISES[option]


def top_format_func(option):
    return TOP_CHOISES[option]


def face_format_func(option):
    return FACE_CHOISES[option]


def main_equip_format_func(option):
    return MAIN_EQUIP[option]


def vertical_format_func(option):
    return VERTICAL_BEAM[option]


def horizontal_format_func(option):
    return HORIZONTAL_BEAM[option]


def min_max_scaler(x, x_min, x_max):
    return (x - x_min) / (x_max - x_min)


def risk_score(srr, frr, sur, err):
    input = map(lambda x: min_max_scaler(x, 0, 3), [srr, frr, sur, err])
    y = model.predict([list(input)])
    return np.round(y[0][0] * 100, 1)


st.title("Hệ thống đánh giá rủi ro xây dựng")

selected = st.checkbox("Có sử dụng ý kiến chuyên gia", True)

if selected:
    st.subheader("Thông số kĩ thuật")

    col1, col2, col3 = st.columns(3)

    with col1:
        main_beat = st.selectbox(
            "Dạng kết cấu nhịp chính:",
            options=list(BR_CHOISES.keys()),
            format_func=br_format_func,
        )
        top = st.selectbox(
            "Lớp mủ mặt cầu:",
            options=list(TOP_CHOISES.keys()),
            format_func=top_format_func,
        )

    with col2:
        face = st.selectbox(
            "Bản mặt cầu:",
            options=list(FACE_CHOISES.keys()),
            format_func=face_format_func,
        )
        main_equip = st.selectbox(
            "Vật liệu kết cấu chịu lực chính:",
            options=list(MAIN_EQUIP.keys()),
            format_func=main_equip_format_func,
        )

    with col3:
        vertical = st.selectbox(
            "Dạng cắt mặt dầm dọc chủ:",
            options=list(VERTICAL_BEAM.keys()),
            format_func=vertical_format_func,
        )
        horizontal = st.selectbox(
            "Dạng dầm ngang:",
            options=list(HORIZONTAL_BEAM.keys()),
            format_func=horizontal_format_func,
        )

    data_bar_chart = pd.DataFrame(
        [
            ["Dạng kết cấu nhịp chính", main_beat],
            ["Lớp mủ mặt cầu", top],
            ["Bản mặt cầu", face],
            ["Vật liệu kết cấu chịu lực chính", main_equip],
            ["Dạng cắt mặt dầm dọc chủ", vertical],
            ["Dạng dầm ngang", horizontal],
        ],
        columns=["Name", "Value"],
    )
    fig = px.bar(data_bar_chart, x="Name", y="Value", barmode="group")
    fig.update_yaxes(range=[0, 5], tick0=0)

    st.write("Mức độ rủi ro theo khảo sát chuyên gia")

    st.plotly_chart(fig)

st.subheader("Yếu tố an toàn")

anti_collision = st.selectbox(
    "Kết cấu chống va xô:",
    options=list(ANTI_COLLISION.keys()),
    format_func=anti_collision_format_func,
)

col4, col5 = st.columns(2)

with col4:
    cross_object = st.selectbox(
        "Đối tượng vượt:",
        options=list(CROSS_OBJECT.keys()),
        format_func=cross_object_format_func,
    )

with col5:
    run_with = st.selectbox(
        "Chạy chung với:",
        options=list(RUN_WITH.keys()),
        format_func=run_with_format_func,
    )

st.subheader("Yếu tố khai thác vận hành")

col6, col7 = st.columns(2)

with col6:
    start_year = st.number_input(
        "Năm bắt đầu khai thác", min_value=today.year - 50, max_value=today.year
    )

with col7:
    avg_number_vechical = st.number_input(
        "Lưu lượng xe trung bình (xe/tháng)", min_value=1000, max_value=100000
    )

col8, col9 = st.columns(2)

with col8:
    max_speed = st.number_input(
        "Vận tốc khai thác (km/h)",
        min_value=50.0,
        max_value=120.0,
        step=1.0,
        format="%.2f",
    )

with col9:
    max_weight = st.number_input(
        "Tải trọng tối đa (Tấn)",
        min_value=2.5,
        max_value=50.0,
        step=1.0,
        format="%.2f",
    )

key = str(anti_collision) + str(cross_object) + str(run_with)

submit = st.button("Đánh giá rủi ro")

if submit is True:
    feature = [
        min_max_scaler(today.year - start_year, 0, 50),
        min_max_scaler(max_speed, 50, 120),
        min_max_scaler(max_weight * 1000, 2500, 50000),
        min_max_scaler(avg_number_vechical, 1000, 100000),
    ]

    with st.spinner("Đang đánh giá rủi ro..."):
        err = SAFE_MAP[key]
        sur = model.predict(np.array([feature]))[0][0]
        total = round((err + sur * 100) / 2, 2)

        st.subheader("Kết quả đánh giá")

        col9, col10, col11 = st.columns(3)
        col9.metric("Yếu tố an toàn", "{} %".format(err))
        col10.metric("Yếu tố khai thác vận hành", "{} %".format(round(sur * 100, 1)))
        col11.metric("Dộ an toàn tổng thể", "{} %".format(total))
