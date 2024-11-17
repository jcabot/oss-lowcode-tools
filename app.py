from datetime import datetime, timedelta
import streamlit as st
import requests

# GitHub API endpoint for searching repositories
GITHUB_API_URL = "https://api.github.com/search/repositories"

# Function to fetch repositories. Only repos with stars > 50 and updated in the last year are shown
def fetch_low_code_repos(query="low-code", sort="stars", order="desc", per_page=100, max_pages=10):
    query += " stars:>=" + "50" + " pushed:>=" + (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
    all_repos = []
    for page in range(1, max_pages + 1):
        params = {
            "q": query,
            "sort": sort,
            "order": order,
            "per_page": per_page,
            "page": page
        }
        response = requests.get(GITHUB_API_URL, params=params)
        if response.status_code == 200:
            repos = response.json()["items"]
            if not repos:
                break
            all_repos.extend(repos)
        else:
            st.error(f"Error fetching data from GitHub API: {response.status_code}")
            break
    return all_repos


# Fetch repositories
if 'repos' not in st.session_state:
    st.session_state.repos = fetch_low_code_repos()

repos = st.session_state.repos


# Display the table
st.set_page_config(layout="wide")
st.title("Low-Code Repositories in GitHub")


# Add star filter slider
min_stars = st.slider("Minimum Stars", min_value=50, max_value=100000, value=50, step=50)

#Add a date filter slider 
# Calculate date range
if 'today' not in st.session_state:
    st.session_state.today = datetime.today()

today = st.session_state.today
one_year_ago = today - timedelta(days=365)

# Date slider
min_date = st.slider(
    "Last Commit",
    min_value=one_year_ago,
    max_value=today,
    value=one_year_ago,
    step=timedelta(days=1)
)

#min_date = st.slider(
#    "Last Commit",
#    min_value=datetime(2023, 11, 18),
#    max_value=datetime(2024, 11, 18),
#    value=datetime(2023, 11, 18),
#    step=timedelta(days=1)
#)

if repos:
    # Create a table with repository information. Only repos with stars >= min_stars and last commit >= min_date are shown
    table_data = []
    filtered_repos = [repo for repo in repos if repo['stargazers_count'] >= min_stars and datetime.strptime(repo['pushed_at'].split('T')[0], '%Y-%m-%d').date() >= min_date.date()]
  
    for repo in filtered_repos:
        table_data.append({
            "Name": repo["name"],
            "Stars⭐": repo['stargazers_count'],
            "Last Updated": repo['pushed_at'].split('T')[0],
            "URL": repo['html_url'],
            "Forks": repo['forks'],
            "Issues": repo['open_issues'],
            "Watchers": repo['watchers'],
            "Language": repo['language'],
            "License": repo['license']['name'] if repo['license'] else "No license",
            "Description": (repo["description"] or "No description")[:200],
            "Topics": repo['topics']
        })
    
    st.write(f"Showing {len(table_data)} repositories")
    st.dataframe(
        table_data,
        column_config={
            "URL": st.column_config.LinkColumn("URL")
        },
        use_container_width=True,
        height=(len(table_data)+1)*35+3,
        hide_index=True
    )

    st.subheader("Selection method")

    #Write the selection method
    st.write("The selection method is based on the following initial criteria:")
    st.write("- Repositories that declare themselves as low-code projects stars >= 50")
    st.write("- Repositories with stars >= 50")
    st.write("- Repositories with last commit at least 1 year ago")
    st.write("- Repositories with information in English")

    st.write("The final list is the intersection of the above criteria manually curated to remove projects that use low-code in a different sense of what we mean by low-code in software develpoment.")
    st.write("For more about the meaning of low-code see")
    st.write("- [This book](https://lowcode-book.com/")
    st.write("- [This blog post](https://modeling-languages.com/low-code-vs-model-driven/)")
    st.write(" - And play with low-code via our open source [low-code-tools](https://github.com/BESSER-PEARL/BESSER)")
   

else:
    st.write("No repositories found or there was an error fetching data.")
