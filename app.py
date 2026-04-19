from datetime import datetime, timedelta
from collections import Counter
import streamlit as st
import requests
import plotly.graph_objects as go
import pandas as pd
import os
import snapshot_utils

# Bundled CSV fallback under snapshots/ (filename reflects date added to this repo)
SNAPSHOTS_DIR = "snapshots"
SNAPSHOT_CSV_FILENAME = "snapshot-2025-06-06.csv"
SNAPSHOT_CSV_PATH = os.path.join(SNAPSHOTS_DIR, SNAPSHOT_CSV_FILENAME)

# Set page configuration FIRST - must be the very first Streamlit command
st.set_page_config(layout="wide")

# Import after set_page_config: the module imports Streamlit/plotly and avoids init-order issues
# on Streamlit Cloud. Module is named keyword_analysis (not "analysis") to avoid clashing with
# Streamlit's multipage/script registry keys.
from keyword_analysis import display_analysis

# GitHub API endpoint for searching repositories
GITHUB_API_URL = "https://api.github.com/search/repositories"

# Function to fetch repositories. Only repos with stars > 50 and updated in the last year are shown
# Returns (repos, data_from_live_api).
# Pass *github_token* so search requests use the GitHub API with auth — on Streamlit Cloud the
# shared egress IP hits the anonymous search rate limit (60/h) almost immediately; without a
# token the app falls back to bundled CSV and auto-snapshot is skipped.
def fetch_low_code_repos(
    # Quoted phrases match GitHub search *literally*, so only repos whose name/description/
    # README/topics contain one of these exact forms are returned. This avoids matches
    # coming from unrelated tokens like "low-level" + "code(s)".
    query='"low-code" OR "lowcode" OR "low code"',
    sort="stars",
    order="desc",
    per_page=100,
    max_pages=10,
    github_token=None,
):
    query += " stars:>=" + "50" + " pushed:>=" + (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
    all_repos = []
    api_failed = False

    headers = {"Accept": "application/vnd.github+json"}
    if github_token:
        headers["Authorization"] = f"Bearer {github_token}"

    for page in range(1, max_pages + 1):
        params = {
            "q": query,
            "sort": sort,
            "order": order,
            "per_page": per_page,
            "page": page
        }
        try:
            response = requests.get(GITHUB_API_URL, params=params, headers=headers, timeout=10)
            if response.status_code == 200:
                repos = response.json()["items"]
                if not repos:
                    break
                all_repos.extend(repos)
            else:
                st.error(f"Error fetching data from GitHub API: {response.status_code}")
                api_failed = True
                break
        except requests.exceptions.RequestException as e:
            st.error(f"GitHub API request failed: {str(e)}")
            api_failed = True
            break

    loaded_from_snapshot = False
    # If API failed or returned no data, load from bundled snapshot CSV
    if api_failed or not all_repos:
        loaded_from_snapshot = True
        try:
            if os.path.exists(SNAPSHOT_CSV_PATH):
                st.warning(
                    f"⚠️ GitHub API is unavailable. Loading data from {SNAPSHOT_CSV_PATH} instead."
                )
                df = pd.read_csv(SNAPSHOT_CSV_PATH, encoding='utf-8')
                
                # Convert CSV data back to GitHub API format
                all_repos = []
                for _, row in df.iterrows():
                    repo_data = {
                        "name": row["Name"],
                        "stargazers_count": row["Stars⭐"],
                        "pushed_at": row["Last Updated"] + "T00:00:00Z",
                        "created_at": row["First Commit"] + "T00:00:00Z",
                        "html_url": row["URL"],
                        "forks": row["Forks"],
                        "open_issues": row["Issues"],
                        "language": row["Language"] if row["Language"] and row["Language"] != "No language" else None,
                        "license": {"name": row["License"]} if row["License"] != "No license" else None,
                        "description": row["Description"] if row["Description"] != "No description" else None,
                        "topics": row["Topics"].split(",") if pd.notna(row["Topics"]) and row["Topics"] else []
                    }
                    all_repos.append(repo_data)
                
                st.info(f"✅ Loaded {len(all_repos)} repositories from snapshot data.")
            else:
                st.error(
                    f"GitHub API failed and {SNAPSHOT_CSV_PATH} was not found."
                )
        except Exception as e:
            st.error(f"Failed to load snapshot data: {str(e)}")

    data_from_live_api = not loaded_from_snapshot
    return all_repos, data_from_live_api


# Fetch repositories
try:
    _github_token = st.secrets.get("GITHUB_TOKEN")
except Exception:
    _github_token = None

if 'repos' not in st.session_state:
    st.session_state.repos, st.session_state.data_from_live_api = fetch_low_code_repos(
        github_token=_github_token
    )

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
    "pddon-win", "all-classification-templetes-for-ML", "node-red-dashboard", "Palu",
    "Liuma-platform", "crudapi-admin-web", "Awesome-ICCV2023-Low-Level-Vision", "pocketblocks",
    "plugins", "LLFormer", "vue-admin", "Low-Code", "FTC-Skystone-Dark-Angels-Romania-2020",
    "WrldTmpl8", "daas-start-kit", "Meta3D", "css-selector-tool", "corebos", "wave-apps",
    "self-hosted", "Automation-workflow", "banglanmt", "Nalu", "no-code-architects-toolkit",
    "MasteringMCU2", "Liuma-engine", "lowcode-tools", "Diff-Plugin", "mfish-nocode-view",
    "backroad", "zcbor", "powerfx-samples", "MemoryNet", "igop", "underTheHoodOfExecutables",
    "StringReloads", "lowcode-b", "EigenTrajectory", "pluto", "pixiebrix-extension", "dozer",
    "vite-vue3-lowcode",
    "qLDPC", "Visio", "Hack-SQL", "cow-Low-code", "LoRA-Pro", "OTE-GAN", "opsli-ui", "three-editor",
    "lowcode-code-generator-demo", "QuadPrior", "UIGO", "SoRA", "grid-form", "CcView", "verus",
    "fastgraphml", "arcane.cpp", "lowcode-engine-ext", "Liuma-platform", "lowcode-plugins", "turbo",
    "DegAE_DegradationAutoencoder", "www-project-top-10-low-code-no-code-security-risks", "lowcode-materials",
    "Vibration-Based-Fault-Diagnosis-with-Low-Delay", "alignment-attribution-code", "VideoUIKit-Web-React",
    "ReGitLint", "pandas-gpt", "yao-knowledge", "snac", "relora", "mettle", "Tenon", "noncode-projects-2024", "EvLight"
}

# Filter out excluded repositories
st.session_state.repos = [repo for repo in st.session_state.repos if repo['name'] not in excluded_repos]

# Default "Repository Table" filters (must match slider defaults below): min stars 50, last commit
# within the last year. Snapshots should store this visible list, not the raw post-search list.
if "today" not in st.session_state:
    st.session_state.today = datetime.today()
_one_year_ago = st.session_state.today - timedelta(days=365)
repos_for_default_table_view = [
    repo
    for repo in st.session_state.repos
    if repo["stargazers_count"] >= 50
    and datetime.strptime(repo["pushed_at"].split("T")[0], "%Y-%m-%d").date()
    >= _one_year_ago.date()
]

# Auto-snapshot: persist the current live list when no recent snapshot exists.
# If a GITHUB_TOKEN secret is configured the snapshot is also committed to the
# repo so it survives Streamlit Cloud restarts (ephemeral filesystem).
if not st.session_state.get('snapshot_taken'):
    if st.session_state.get('data_from_live_api'):
        saved_path = snapshot_utils.auto_snapshot(repos_for_default_table_view)
        st.session_state.snapshot_taken = True
        if saved_path:
            filename = os.path.basename(saved_path)
            try:
                gh_token = st.secrets.get("GITHUB_TOKEN")
            except Exception:
                gh_token = None

            if gh_token:
                gh_repo = st.secrets.get("GITHUB_REPO", "jcabot/oss-lowcode-tools")
                gh_branch = st.secrets.get("GITHUB_BRANCH", "main")
                ok, err_detail = snapshot_utils.commit_snapshot_to_github(
                    saved_path, gh_token, gh_repo, gh_branch
                )
                if ok:
                    st.success(
                        f"New snapshot committed to the repository: snapshots/{filename}"
                    )
                else:
                    msg = (
                        f"Snapshot saved locally but could not be committed to GitHub: "
                        f"{filename}"
                    )
                    if err_detail:
                        msg += f" ({err_detail})"
                    st.warning(msg)
            else:
                st.success(f"New snapshot saved locally: {filename}")
        elif not snapshot_utils.should_take_snapshot():
            pass  # recent snapshot already exists in snapshots/
        else:
            # should_take_snapshot but saved_path None => file exists for today (same session rerun)
            pass
    elif _github_token:
        st.info(
            "GitHub Search API fell back to bundled CSV (rate limit or HTTP error). "
            "Auto-snapshot was skipped — live API data is required. "
            "Ensure **GITHUB_TOKEN** is set in app secrets so search requests are authenticated "
            "(much higher rate limits)."
        )
    else:
        st.info(
            "GitHub Search API fell back to bundled CSV. Auto-snapshot was skipped. "
            "Add **GITHUB_TOKEN** to Streamlit secrets so searches use authenticated "
            "requests (recommended on Streamlit Cloud)."
        )

repos = st.session_state.repos


# Display the table
st.title("Dashboard of Open-Source Low-Code Tools in GitHub")
st.subheader("Maintained by the [BESSER team](https://github.com/BESSER-PEARL/BESSER)")

# Add table of contents
st.markdown("""
## Table of Contents
- [Quick Notes](#quick-notes)
- [Repository Filters](#repository-filters)
- [Repository Table](#repository-table)
- [Selection Method](#selection-method)
- [Global Statistics](#global-statistics)
- [Low-code tools also mixing other related topics](#repository-analysis)
    - [Low-code and No-Code tools](#analysis-for-no-code)
    - [Low-code and Modeling tools](#analysis-for-modeling)
    - [Low-code and UML tools](#analysis-for-uml)
    - [Low-code with / for AI](#analysis-for-ai)
""")

st.markdown("<a name='quick-notes'></a>", unsafe_allow_html=True)
st.write("## Quick notes:")
st.write("- Use the sliders to filter the repositories. Click on a column header to sort the table.")
st.write("- Hover over the table to search for specific reports or export the table as a CSV file.")
st.write("- A few global stats are also available at the bottom of the page.")
st.write("- Suggest improvements via the [GitHub repository of this dashboard](https://github.com/jcabot/oss-lowcode-tools)")

# Add anchors before each section
st.markdown("<a name='repository-filters'></a>", unsafe_allow_html=True)
st.write("## Repository Filters")

# Add star filter slider
min_stars = st.slider("Minimum Stars", min_value=50, max_value=100000, value=50, step=50)

# Add a date filter slider
# Calculate date range, also storing the value in the session to avoid the slider resetting all the time due to
# streamlit thinking the min max value have changed and need to restart

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

# Same subset as the main repository table (slider filters). Analysis sections must use this list,
# not the full session list, so keyword breakdowns match what the table shows.
filtered_repos = []
if repos:
    filtered_repos = [
        repo
        for repo in repos
        if repo["stargazers_count"] >= min_stars
        and datetime.strptime(repo["pushed_at"].split("T")[0], "%Y-%m-%d").date()
        >= min_date.date()
    ]


if repos:
    # Create a table with repository information. Only repos with stars >= min_stars and last commit >= min_date are shown
    table_data = []
  
    for repo in filtered_repos:
        table_data.append({
            "Name": repo["name"],
            "Stars⭐": repo['stargazers_count'],
            "Last Updated": repo['pushed_at'].split('T')[0],
            "First Commit": repo['created_at'].split('T')[0],
            "URL": repo['html_url'],
            "Forks": repo['forks'],
            "Issues": repo['open_issues'],
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

    st.markdown("<a name='selection-method'></a>", unsafe_allow_html=True)
    st.subheader("Selection method")

    #Write the selection method


    st.write("The selection method is based on the following inclusion criteria:")
    st.write("- Repositories that declare themselves as low-code projects")
    st.write("- Repositories with more than 50 stars")
    st.write("- Active repositories (last commit is no more than 1 year ago")
    st.write("- Tool aims to generate any component of a software application, including AI components, dashboards or full applications")
    st.write("and exclusion criteria:")
    st.write("- Repositories with no information in English")
    st.write("- Repositories that were just created to host the source code of a published article")
    st.write("- Repositories that are awesome lists or collection of resources")

    st.write("The final list is the intersection of the above criteria. The final list has also been manually curated to remove projects that use low-code in a different sense of what we mean by low-code in software development.")
    st.write("For more information about low-code see")
    st.write("- [This book](https://lowcode-book.com/)")
    st.write("- [This blog post](https://modeling-languages.com/low-code-vs-model-driven/)")
    st.write(" - And play with low-code via our open source [low-code-tool](https://github.com/BESSER-PEARL/BESSER)")

    st.markdown("<a name='global-statistics'></a>", unsafe_allow_html=True)
    st.subheader("Some global stats")

    # Create a list of first commit dates
    first_commit_dates = [datetime.strptime(repo['created_at'].split('T')[0], '%Y-%m-%d').date() for repo in
                          filtered_repos]

    # Grouping the data by year
    years = [date.year for date in first_commit_dates]
    year_counts = Counter(years)

    # Plotting the distribution of first commit dates by year
    year_bar_chart = go.Figure(
        data=[
            go.Bar(
                x=list(year_counts.keys()),
                y=list(year_counts.values()),
            )
        ]
    )
    year_bar_chart.update_layout(
        title="Distribution of First Commit Dates by Year",
        xaxis_title="Year of First Commit",
        yaxis_title="Number of Repositories",
        xaxis=dict(tickangle=45)
    )

    # Create a list of star counts
    star_counts = [repo['stargazers_count'] for repo in filtered_repos]

    # Plotting the distribution of repositories by star count using a boxplot
    star_box_plot = go.Figure(
        data=[
            go.Box(
                x=star_counts,
                boxpoints="outliers",  # Show only outliers as points
                jitter=0.5,
            )
        ]
    )
    star_box_plot.update_layout(
        title="Distribution of Repositories by Star Count",
        xaxis_title="",
        yaxis_title="Number of Stars",
        xaxis=dict(showticklabels=False)
    )

    # Create a list of languages from filtered_repos
    languages = [repo['language'] for repo in filtered_repos if repo['language']]

    # Count the occurrences of each language
    language_counts = Counter(languages)

    # Plotting the aggregation of repositories by language
    language_bar_chart = go.Figure(
        data=[
            go.Bar(
                x=list(language_counts.keys()),
                y=list(language_counts.values()),
            )
        ]
    )
    language_bar_chart.update_layout(
        title="Aggregation of Repositories by Language",
        xaxis_title="Programming Language",
        yaxis_title="Number of Repositories",
        xaxis=dict(tickangle=45)
    )

    cols = st.columns(2)
    with cols[0]:
        st.plotly_chart(year_bar_chart, use_container_width=True)
        st.plotly_chart(language_bar_chart, use_container_width=True)
    with cols[1]:
        st.plotly_chart(star_box_plot, use_container_width=True)

    # Keyword breakdowns use *only* filtered_repos — the same objects as the dataframe above
    # for this run (same slider values). Nested here so analysis never runs without the table.
    st.markdown("<a name='repository-analysis'></a>", unsafe_allow_html=True)
    st.write("## Repository Analysis")
    st.caption(
        "Only repositories that appear in the repository table above (with your current "
        "Minimum Stars and Last Commit settings) are included; each subsection is a subset of that list."
    )
    for keyword in ["no-code", "modeling", "uml", "ai"]:
        st.write(f"### Analysis for '{keyword}'")
        display_analysis(filtered_repos, keyword)
        st.markdown("---")

else:
    st.write("No repositories found or there was an error fetching data.")
