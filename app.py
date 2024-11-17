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

# List of excluded repositories
excluded_repos = {
    "JeecgBoot", "supervision", "amis", "APIJSON", "awesome-lowcode", "LoRA", "activepieces", 
    "gop", "pycaret", "viztracer", "joint", "mometa", "asmjit", "NullAway", 
    "self-hosted-ai-starter-kit", "sparrow", "smart-admin", "tracecat", "dooringx", 
    "Genie.jl", "instill-core", "metarank", "dataprep", "hyperlight", "go-streams",
    "dashpress", "lowcode-demo", "diboot", "steedos-platform", "opsli-boot", 
    "PiML-Toolbox", "marsview", "openDataV", 
    "Awesome-CVPR2024-CVPR2021-CVPR2020-Low-Level-Vision", "dart_native", 
    "low-level-programming", "vue-component-creater-ui", "ovine", "vlife", "beelzebub",
    "mtbird", "Awesome-CVPR2024-Low-Level-Vision", "create-chart", "crusher",
    "yuzi-generator", "pc-Dooring", "citrus", "Conduit", "react-admin-firebase",
    "apex", "fire-hpp", "awesome-lowcode", "karamel", "flowpipe", "fast-trade", "pd",
    "MetaLowCode", "vue-low-code", "css-text-portrait-builder", "awesome-low-code",
    "langwatch", "web-builder", "awesome-nocode-lowcode", "LLFlow", "AS-Editor",
    "mfish-nocode", "naas", "Awesome-ECCV2024-ECCV2020-Low-Level-Vision", "dataCompare",
    "AIVoiceChat", "illa", "praxis-ide", "low-level-design", "HuggingFists", "dagr",
    "pddon-win", "all-classification-templetes-for-ML", "node-red-dashboard",
    "Liuma-platform", "crudapi-admin-web", "Awesome-ICCV2023-Low-Level-Vision",
    "plugins", "LLFormer", "vue-admin", "Low-Code", "FTC-Skystone-Dark-Angels-Romania-2020",
    "WrldTmpl8", "daas-start-kit", "Meta3D", "css-selector-tool", "corebos",
    "self-hosted", "Automation-workflow", "banglanmt", "Nalu", "no-code-architects-toolkit",
    "MasteringMCU2", "Liuma-engine", "lowcode-tools", "Diff-Plugin", "mfish-nocode-view",
    "backroad", "zcbor", "powerfx-samples", "MemoryNet", "igop", "underTheHoodOfExecutables",
    "StringReloads", "lowcode-b", "EigenTrajectory", "pluto", "pixiebrix-extension",
    "qLDPC", "Visio", "Hack-SQL", "cow-Low-code", "LoRA-Pro", "OTE-GAN", "opsli-ui", "three-editor",
    "lowcode-code-generator-demo", "QuadPrior", "UIGO", "SoRA", "grid-form", "CcView",
    "DegAE_DegradationAutoencoder", "www-project-top-10-low-code-no-code-security-risks",
    "Vibration-Based-Fault-Diagnosis-with-Low-Delay", "alignment-attribution-code", "VideoUIKit-Web-React",
    "ReGitLint", "pandas-gpt", "yao-knowledge", "snac", "relora", "mettle", "Tenon", "noncode-projects-2024", "EvLight"
}

# Filter out excluded repositories
st.session_state.repos = [repo for repo in st.session_state.repos if repo['name'] not in excluded_repos]

repos = st.session_state.repos


# Display the table
st.set_page_config(layout="wide")
st.title("Low-Code Repositories in GitHub by the [BESSER team](https://github.com/BESSER-PEARL/BESSER)")
st.write("Use the sliders to filter the repositories. Click on a column header to sort the table.")
st.write("Hover over the table to search for specific reports or export the table as a CSV file.")


# Add star filter slider
min_stars = st.slider("Minimum Stars", min_value=50, max_value=100000, value=50, step=50)

#Add a date filter slider 
# Calculate date range, also storing the value in the session to avoid the slider resetting all the time due to
# streamlit thinking the min max value have changed and need to restart

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



if repos:
    # Create a table with repository information. Only repos with stars >= min_stars and last commit >= min_date are shown
    table_data = []

    filtered_repos = [repo for repo in repos if repo['stargazers_count'] >= min_stars and datetime.strptime(repo['pushed_at'].split('T')[0], '%Y-%m-%d').date() >= min_date.date()]
  
    for repo in filtered_repos:
        table_data.append({
            "Name": repo["name"],
            "Stars⭐": repo['stargazers_count'],
            "Last Updated": repo['pushed_at'].split('T')[0],
            "First Commit": repo['created_at'].split('T')[0],
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


    st.write("The selection method is based on the following inclusion criteria:")
    st.write("- Repositories that declare themselves as low-code projects")
    st.write("- Repositories with stars ≥ 50") 
    st.write("- Repositories with last commit at least 1 year ago")
    st.write("")
    st.write("and exclusion criteria:")
    st.write("- Repositories with information in other languages than English")
    st.write("- Repositories that were just created to host the source code of a published article")
    st.write("- Repositories that are awesome lists or collection of resources")


    st.write("The final list is the intersection of the above criteria. The final list has also been manually curated to remove projects that use low-code in a different sense of what we mean by low-code in software develpoment.")
    st.write("For more information about low-code see")
    st.write("- [This book](https://lowcode-book.com/)")
    st.write("- [This blog post](https://modeling-languages.com/low-code-vs-model-driven/)")
    st.write(" - And play with low-code via our open source [low-code-tool](https://github.com/BESSER-PEARL/BESSER)")
   

else:
    st.write("No repositories found or there was an error fetching data.")
