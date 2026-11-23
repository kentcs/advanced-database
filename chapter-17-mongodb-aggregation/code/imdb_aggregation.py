"""Run: python -m streamlit run imdb_aggregation.py"""
import pandas as pd
import streamlit as st
from pymongo.errors import PyMongoError
import aggregation_queries as queries

st.set_page_config(page_title="IMDb ratings by release year", layout="wide")
st.title("IMDb ratings by release year")
st.write("MongoDB filters, joins, and groups. Streamlit displays the summary.")
st.caption("Mean rating gives each qualifying movie equal weight; it is not weighted by votes.")

@st.cache_resource
def database():
    client, db = queries.connect()
    return client, db

with st.form("summary"):
    a, b, c = st.columns(3)
    start = a.number_input("First year", min_value=1800, max_value=2100, value=1990)
    end = b.number_input("Last year", min_value=1800, max_value=2100, value=1999)
    votes = c.number_input("Minimum votes per movie", min_value=0, value=1000, step=100)
    submitted = st.form_submit_button("Summarize movie ratings")

if submitted:
    try:
        pipeline = queries.build_pipeline(int(start), int(end), int(votes))
    except ValueError as error:
        st.error(str(error))
        st.stop()
    with st.expander("Pipeline executed by MongoDB", expanded=True):
        st.json(pipeline)
    try:
        with st.spinner("MongoDB is computing the summary…"):
            client, db = database()
            rows = queries.summarize(db, pipeline)
    except (RuntimeError, PyMongoError):
        st.error("Could not run the summary. Check the Chapter 16 server, MONGODB_URI, "
                 "and read access to imdb. If it timed out, try a smaller year range.")
        st.stop()
    if not rows:
        st.info("No qualifying movies. Check the imported data, year range, and vote threshold.")
    else:
        frame = pd.DataFrame(rows)[["year", "rated_movies", "mean_rating", "total_votes"]]
        st.dataframe(frame, hide_index=True)
        st.bar_chart(frame, x="year", y="mean_rating")
        st.caption("Years without qualifying movies are omitted. "
                   "Counts describe this filtered sample, not all IMDb titles.")
