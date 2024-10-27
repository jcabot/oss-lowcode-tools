from datetime import datetime, timedelta
import streamlit as st
import requests

# GitHub API endpoint for searching repositories
GITHUB_API_URL = "https://api.github.com/search/repositories"

# Function to fetch repositories
def fetch_low_code_repos(query="low-code", sort="stars", order="desc", per_page=100, max_pages=10):
    query += " pushed:>=" + (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
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
repos = fetch_low_code_repos()

# Display the table
st.title("Low-Code GitHub Repositories")

if repos:
    # Create a table with repository information
    table_data = []
    for repo in repos:
        table_data.append({
            "Name": repo["name"],
            "Stars": f"{repo['stargazers_count']} ⭐",
            "Description": (repo["description"] or "No description")[:200],
            "URL": repo["html_url"]
        })
    
    st.write(f"Showing {len(table_data)} repositories")
    st.table(table_data)
else:
    st.write("No repositories found or there was an error fetching data.")

st.write("end of the world")
