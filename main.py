from flask import Flask, render_template, request, url_for, redirect
from pymongo import MongoClient
import plotly.express as px
import plotly
import pandas as pd
import json
app = Flask(__name__)

client = MongoClient("mongodb+srv://netclan:netclan@cluster0.btiod7t.mongodb.net/?retryWrites=true&w=majority")
db = client.Netclan
rawdata = pd.DataFrame(db.jsondata.find())


def plot1(df):
	data = df.drop(df[(df['sector']=='')|(df['likelihood']=='')].index,inplace=False)
	fig = px.scatter(data, x="sector", y="intensity", color='likelihood')
	
	# fig.show()
	return fig

def plot2(df):
	data = df.drop(df[(df['region']=='') | (df['pestle']=='') | (df['region']=='world')].index,inplace=False)
	fig = px.density_heatmap(data, x="region", y="pestle")
	# fig.show()
	return fig

def plot3(df):
	data = df.drop(df[(df['topic']=='') | (df['country']=='') | (df['likelihood']=='') | (df['relevance']=='')].index,inplace=False)
	data['likelihood'] = pd.to_numeric(data['likelihood'])
	fig = px.scatter(data, x="topic", y="country", color='relevance', size='likelihood')
	# fig.show()
	return fig

def plot4(df):
	data = df.drop(df[(df['country']=='') | (df['sector']=='')].index,inplace=False)
	co = data['country'].unique()
	co = pd.DataFrame(co, columns = ['country'])
	cnt = []
	sec = []
	for x in co['country']:
		arr = data[data['country']==x]['sector'].unique()
		cnt.append(len(arr))
		sec.append(', '.join(arr))
	co['sector_count'] = cnt
	co['sectors'] = sec
	# print(co);
	fig = px.choropleth(co, locations="country",locationmode="country names",
                    color="sector_count", # lifeExp is a column of gapminder
                    hover_name="country",hover_data=["sectors"], # column to add to hover information
                    color_continuous_scale=px.colors.sequential.Plasma)
	# fig.show()
	return fig


def getarray(column):
	return rawdata.drop(rawdata[(rawdata[column]=='')].index,inplace=False)[column].unique()


tags = ['end_year', 'topic', 'sector', 'region', 'pestle']
data = []
for x in tags:
	data.append(getarray(x))

@app.route('/', methods=('GET', 'POST'))
def hello():
	df = rawdata
	if request.method == "POST":
		for x in tags:
			fltr = request.form.get(x)
			if fltr!="select":
				if x=='end_year':
					df = df[df[x]==int(fltr)]
				else:	
					df = df[df[x]==fltr]
				# print(df)
				# print(fltr)	
	chart1 = json.dumps(plot1(df), cls=plotly.utils.PlotlyJSONEncoder)
	chart2 = json.dumps(plot2(df), cls=plotly.utils.PlotlyJSONEncoder)
	chart3 = json.dumps(plot3(df), cls=plotly.utils.PlotlyJSONEncoder)
	chart4 = json.dumps(plot4(df), cls=plotly.utils.PlotlyJSONEncoder)
	
	return render_template("index.html",data=data,graph1=chart1,graph2=chart2,graph3=chart3,graph4=chart4);

if __name__ == "__main__":
	app.run(debug=True)









































