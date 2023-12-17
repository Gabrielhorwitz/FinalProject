"""
Class: CS230--Section 1
Name: Gabriel Horwitz
Description: Final Project
I pledge that I have completed the programming assignment
independently.
I have not copied the code from a student or any source.
I have not given my code to any student.
"""

import streamlit as st
import pandas as pd
import pydeck as pdk
import matplotlib.pyplot as plt

"""Function to display the homepage"""
def show_homepage():
    """Loads snow when the page is opened...using streamlit docs"""
    st.snow()
    st.markdown("<h1 style='text-align: center; color: green;'>Dispensary Map - Boston</h1>", unsafe_allow_html=True)
    st.image("main_image")
    st.markdown("<h4 style='text-align: center;'>by Gabe Horwitz</h4>", unsafe_allow_html=True)

    """Additional information"""
    st.subheader("Additional Information")
    st.write("This Streamlit application allows users to explore various aspects of the cannabis business registry. \
                     Users can filter data by business type, equity program participation, and owner's name. \
                     The map provides a geographical view of the businesses, while the visualizations offer insights into the distribution of business types.")

"""Load the dataset"""
"""@st.cache_data was recommended on streamlit website"""
@st.cache_data
def load_data():
    data = pd.read_excel('Cannabis_Registry.xlsx')
    return data

df = load_data()

"""Function to filter data"""
"""else is for the 'other' choice"""
def filter_data(selected_type):

    specific_types = ['Retail', 'Courier', 'Operator', 'Co-Located']
    if selected_type == 'All':
        return df
    elif selected_type in specific_types:
        return df[df['app_license_category'] == selected_type]
    else:
        return df[~df['app_license_category'].isin(specific_types)]

"""Function to plot the distribution of business types"""
def plot_business_type_distribution(data):
    business_counts = data['app_license_category'].value_counts()
    business_counts_df = business_counts.reset_index()
    business_counts_df.columns = ['business_type', 'count']
    business_counts_df['business_type'] = business_counts_df.apply(
        lambda x: 'Other' if x['count'] < 10 else x['business_type'], axis=1)
    business_counts_grouped = business_counts_df.groupby('business_type').sum().sort_values(by='count', ascending=False)
    fig, ax = plt.subplots()
    ax.pie(business_counts_grouped['count'], labels=business_counts_grouped.index, autopct=lambda p: f'{p:.1f}%',
           startangle=90)
    ax.axis('equal')
    plt.title('Distribution of Business Types')
    st.pyplot(fig)

def plot_business_type_bar_chart(data):
    business_counts = data['app_license_category'].value_counts()
    fig, ax = plt.subplots()
    business_counts.plot(kind='bar', ax=ax)
    ax.set_title('Number of Each Business Type')
    ax.set_xlabel('Business Type')
    ax.set_ylabel('Count')
    st.pyplot(fig)

"""Function to display the data explorer page"""
def show_data_page():
    st.markdown("<h1 style='text-align: center; color: green;'>Map to Cannabis Dispensaries</h1>", unsafe_allow_html=True)
    st.sidebar.header("Filter by Business Type")

    """Dropdown for selecting business type"""
    business_types = ['All', 'Retail', 'Co-Located', 'Operator', 'Courier', 'Other']
    selected_type = st.sidebar.selectbox("Select Business Type", options=business_types)

    """Toggle for active licenses"""
    only_active = st.sidebar.checkbox("Show only active licenses", value=False)

    """Apply filters based on what is chosen by user"""
    filtered_data = df.copy()
    if selected_type != "All":
        filtered_data = filtered_data[filtered_data['app_license_category'] == selected_type]
    if only_active:
        filtered_data = filtered_data[filtered_data['app_license_status'] == 'Active']

    """Found on streamlit website & stackoverflow"""
    map_data = filtered_data[['latitude', 'longitude', 'app_business_name']].dropna()
    view_state = pdk.ViewState(latitude=42.3601, longitude=-71.0589, zoom=11)
    tooltip = {
        "html": "<b>Business Name:</b> {app_business_name}",
        "style": {
            "backgroundColor": "green",
            "color": "white"
        }
    }
    """Dark green color"""
    layer = pdk.Layer(
        'ScatterplotLayer',
        data=map_data,
        get_position='[longitude, latitude]',
        get_color='[0, 100, 0, 160]',
        get_radius=100,
        pickable=True,
    )
    st.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mapbox/light-v9',
        initial_view_state=view_state,
        layers=[layer],
        tooltip=tooltip
    ))


"""Function to display the business types page"""
def show_business_page():
    st.markdown("<h1 style='text-align: center; color: green;'># of Businesses</h1>", unsafe_allow_html=True)

    """Side-by-side buttons for chart type selection"""
    pie_chart, bar_chart = False, False
    col1, col2 = st.columns(2)
    with col1:
        pie_chart = st.button('Pie Chart')
    with col2:
        bar_chart = st.button('Bar Chart')
    """Small notification at bottom of page"""
    """Found on streamlit website"""
    if pie_chart:
        st.toast('Pie Chart!', icon='🎉')
        st.session_state.chart_type = 'Pie Chart'
    if bar_chart:
        st.toast('Bar Chart!', icon='🎉')
        st.session_state.chart_type = 'Bar Chart'

    """Show the selected chart"""
    if st.session_state.get('chart_type', 'Pie Chart') == 'Pie Chart':
        plot_business_type_distribution(df)
    elif st.session_state.chart_type == 'Bar Chart':
        plot_business_type_bar_chart(df)

def plot_active_inactive_distribution(data):
    status_counts = data['app_license_status'].value_counts()
    fig, ax = plt.subplots()
    status_counts.plot(kind='barh', color=['green' if status == 'Active' else 'grey' for status in status_counts.index])
    ax.set_xlabel('Number of Licenses')
    ax.set_ylabel('License Status')
    ax.set_title('Active vs Inactive Licenses', color='green')
    st.pyplot(fig)

"""Function to display the active businesses page with the chart"""
def show_active_page(df):
    st.markdown("<h1 style='text-align: center; color: green;'>Active Businesses</h1>", unsafe_allow_html=True)
    plot_active_inactive_distribution(df)

"""Main app logic"""
def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Select a page:", ["Homepage", "Map", "Num of Businesses", "Active"])

    if page == "Homepage":
        show_homepage()
    elif page == "Map":
        show_data_page()
    elif page == "Num of Businesses":
        show_business_page()
    elif page == "Active":
        show_active_page(df)

"""Run the main function"""
if __name__ == "__main__":
    main()
