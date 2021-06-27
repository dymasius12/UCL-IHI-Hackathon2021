import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import seaborn as sns
import plotly.express as px
import json
import altair as alt
from urllib.request import urlopen
import json
sns.set_style("whitegrid")
sns.set_palette("husl")
st.set_option('deprecation.showPyplotGlobalUse', False)
# insert at 1, 0 is the script path (or '' in REPL)
def add_US(df):
    USA = df.groupby('Year',as_index= False).mean()
    USA['State Name'] = 'All States'
    df = pd.concat([USA,df])
    df = df.set_index(['State Name','Year'])
    return df

def space():
    st.write("")
    st.write("")
    st.write("")
    st.write("")


df = pd.read_csv("combined.csv")
state_names = df['State Name'].unique()
df = add_US(df)

future_df = pd.read_csv("future.csv")
future_df = add_US(future_df)

def add_units(variable = 'Asthma'):
    if variable in diseases:
        string = ' (Death Rate)'
    else:
        string = ' (' + units[variable] + ')'
    return string

units = {'Carbon monoxide': 'Parts per mil',
 'Nitrogen dioxide (NO2)': 'Parts per bil',
 'Outdoor Temperature': 'Degrees Fahrenheit',
 'Ozone': 'Parts per mil',
 'PM10 Total 0-10um STP': 'Micrograms/cubic meter (25 C)',
 'Sulfur dioxide': 'Parts per bil'}

diseases = ['Asbestosis', 'Asthma',
       'Chronic obstructive pulmonary disease', 'Chronic respiratory diseases',
       'Coal workers pneumoconiosis',
       'Interstitial lung disease and pulmonary sarcoidosis',
       'Other chronic respiratory diseases', 'Other pneumoconiosis',
       'Pneumoconiosis', 'Silicosis']

pollution =['Carbon monoxide',
       'Nitrogen dioxide (NO2)', 'Outdoor Temperature', 'Ozone',
       'PM10 Total 0-10um STP', 'Sulfur dioxide']



############ Introduction #############

st.title("US Respiratory Illness Death Rate vs Air Quality Dashboard")
st.write("Welcome! :grin:")
st.write("This interactive website visualises the affect of air quality on respiratory health using data from the US.")

space()




####### map ####
st.write("MAP 🗺️")
st.write("You can see how the death rate of respiratory illnesses or air pollution changes over time across the US.")


with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)


code = {'Alabama': 'AL',
        'Alaska': 'AK',
        'Arizona': 'AZ',
        'Arkansas': 'AR',
        'California': 'CA',
        'Colorado': 'CO',
        'Connecticut': 'CT',
        'Delaware': 'DE',
        'District of Columbia': 'DC',
        'Florida': 'FL',
        'Georgia': 'GA',
        'Hawaii': 'HI',
        'Idaho': 'ID',
        'Illinois': 'IL',
        'Indiana': 'IN',
        'Iowa': 'IA',
        'Kansas': 'KS',
        'Kentucky': 'KY',
        'Louisiana': 'LA',
        'Maine': 'ME',
        'Maryland': 'MD',
        'Massachusetts': 'MA',
        'Michigan': 'MI',
        'Minnesota': 'MN',
        'Mississippi': 'MS',
        'Missouri': 'MO',
        'Montana': 'MT',
        'Nebraska': 'NE',
        'Nevada': 'NV',
        'New Hampshire': 'NH',
        'New Jersey': 'NJ',
        'New Mexico': 'NM',
        'New York': 'NY',
        'North Carolina': 'NC',
        'North Dakota': 'ND',
        'Ohio': 'OH',
        'Oklahoma': 'OK',
        'Oregon': 'OR',
        'Pennsylvania': 'PA',
        'Rhode Island': 'RI',
        'South Carolina': 'SC',
        'South Dakota': 'SD',
        'Tennessee': 'TN',
        'Texas': 'TX',
        'Utah': 'UT',
        'Vermont': 'VT',
        'Virginia': 'VA',
        'Washington': 'WA',
        'West Virginia': 'WV',
        'Wisconsin': 'WI',
        'Wyoming': 'WY'}

map_option = st.selectbox("What would you like to map?", diseases + pollution )
map_year = st.slider('What year?', int(df.reset_index().Year.min()), int(df.reset_index().Year.max()), key="map")

map_df = df.copy().reset_index()

map_df['Code'] = map_df['State Name'].map(code)
min_val = map_df[map_option].min()
max_val = map_df[map_option].max()
map_df = map_df.loc[map_df['Year'] == map_year]
fig = px.choropleth(map_df, #
                    locations='Code', #plot based on state code
                    color=map_option, #chose a column to show values
                    color_continuous_scale='spectral_r', #color scheme
                    range_color=(min_val , max_val),
                    hover_name='State Name', #label options
                    locationmode='USA-states', #join on state
                    scope='usa' # only show US map
                   )
#fig.show()
st.plotly_chart(fig)

space()


st.write("⬅️ You can change which US State you want to look at for the rest of the plots.")

space()


#### line graph plots #########
st.write("COMPARISON")
st.write("You can compare a range of different illnesses and air quality metrics and the correlation between the two will be calculated.")

state_option = st.sidebar.selectbox("Which state do you want to look at?",df.reset_index()["State Name"].unique())
resp_illness = st.selectbox("Which illness do you want to focus on?", diseases )
air_quality = st.selectbox("Which air quality metric do you want to compare against?", pollution)

comparison_df = df.loc[state_option][[resp_illness, air_quality]]
corr_df = df.corr()
correlation = corr_df .loc[resp_illness][air_quality]

sns.lineplot(x=resp_illness, y=air_quality, data=comparison_df,legend = 'auto', label='Correlation = {:.2f}'.format(correlation))
plt.xlabel(resp_illness + add_units())
plt.ylabel(air_quality + add_units(air_quality))
st.pyplot()
space()


### bubble_chart

bubble_df = df.reset_index()

bubble_df = bubble_df.loc[bubble_df["State Name"] == state_option]
bubble_df["Year"] = pd.to_datetime(bubble_df["Year"], format="%Y")
bubble_df = bubble_df[["Year", resp_illness, air_quality]]
bubble_df = bubble_df.rename(columns = {resp_illness:resp_illness + add_units(resp_illness), air_quality: air_quality + add_units(air_quality)})
# st.dataframe(bubble_df)

c = alt.Chart(bubble_df).mark_circle().encode(
       x="Year", y=resp_illness + add_units(resp_illness), size=air_quality + add_units(air_quality), color=air_quality + add_units(air_quality), tooltip=air_quality + add_units(air_quality)).properties(
       width=800, height=500, title=f"Comparison between {air_quality} and {resp_illness} for the state of {state_option}")
c.configure_title(fontSize=20,
anchor="middle", fontWeight="bold")
plt.figure()
st.altair_chart(c, use_container_width=False)
##### correlation plot #########

# Generate a mask for the upper triangle
mask = np.triu(np.ones_like(corr_df , dtype=bool))
# Set up the matplotlib figure
f, ax = plt.subplots(figsize=(11, 9))
# Generate a custom diverging colormap
cmap = sns.diverging_palette(230, 20, as_cmap=True)
# Draw the heatmap with the mask and correct aspect ratio
h = sns.heatmap(corr_df , mask=mask, cmap=cmap, vmax=.3, center=0,
            square=True, linewidths=.5, cbar_kws={"shrink": .5,'label': 'Correlation'})
h.tick_params(labelsize=15)
st.pyplot()

space()

##########  bar chart for the disease in a given year
st.write("YEARLY 📊")
st.write("You can see how respiratory illness death rate has changed over the years by sliding the time bar.")
year = st.slider('What year?', int(df.reset_index().Year.min()), int(df.reset_index().Year.max()))

bar_df = pd.DataFrame()
bar_df['Death Rate'] = df.loc[state_option,year][diseases].values
bar_df['Respiratory Disease'] = diseases
plt.figure()
sns.barplot(x='Respiratory Disease', y='Death Rate', data=bar_df)
plt.xticks(rotation=90)
plt.ylim(0,60)
st.pyplot()
space()





#### future line graph plots #########
st.write("FORECASTING 📈")
st.write("We forecasted future values using a temporal convolutional neural network that is trained on over thirty years of data to predict into 2025, the machine learning model architecture is seen below.")

image = Image.open('TCN.png')
st.image(image, caption='Sequence to sequence machine learning model used')

st.write("By selecting different metrics you can see how respiratory illness death rate and air quality will change in the future.")


air_quality_option = st.multiselect("Which future values would you like to see?", pollution + ['Chronic respiratory disease' + add_units(resp_illness)],default=['Chronic respiratory disease' + add_units(resp_illness)])
future_df = future_df.rename(columns = {'Chronic respiratory diseases':'Chronic respiratory disease' + add_units(resp_illness)})
try: ## prevents errors if there is no option selected
    line_df = future_df.loc[state_option][air_quality_option]
    for air in air_quality_option:
        if air != 'Chronic respiratory disease (Death Rate)':
            line_df = line_df.rename(columns = {air:air+add_units(air)})
    line_df.index = pd.to_datetime(line_df.index, format="%Y")
    sns.lineplot(data = line_df)
    st.pyplot()
except:
    pass
space()


## The sidebar expandable button

with st.sidebar.beta_expander("Click here to learn more about this webpage"):
       st.markdown("""This dashboard combines **data visualisation**, **machine learning** and **data analysis** to give an insight into
       air quality and respiratory illness in the US.""")

       st.markdown("You can find the Github Repo on [Dymasius12](github.com/dymasius12/UCL-IHI-Hackathontest)")
