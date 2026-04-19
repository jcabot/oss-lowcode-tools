import re

import streamlit as st
import plotly.graph_objects as go

# Whole-word / phrase matching for software "modeling" — substring "model" matches inside
# unrelated words (e.g. remodel, remodeling) and is far too noisy for descriptions.
_MODELING_PHRASE = re.compile(
    r'\b(?:model-driven|model-based|modeling)\b|\bunified\s+modeling\s+language\b',
    re.I,
)
_MODEL_WORD = re.compile(r'\bmodels?\b', re.I)


def _matches_modeling(description: str, name: str, topics: list[str]) -> bool:
    """True if name/description/topics suggest MDE / software modeling (not substring 'model' in 'remodel')."""
    text = f"{description} {name}"
    if _MODELING_PHRASE.search(text):
        return True
    if _MODEL_WORD.search(text):
        return True
    for raw in topics:
        t = (raw or '').lower().strip()
        if not t:
            continue
        if t in {'model-driven', 'model-based', 'modeling', 'mda', 'mde'}:
            return True
        if 'model-driven' in t or 'model-based' in t or 'modeling' in t:
            return True
    return False


def analyze_repos_multiple_keywords(repos, keywords, category_name):
    """Analyze repositories for multiple keywords within a category"""
    matching_repos = []
    non_matching_repos = []
    
    for repo in repos:
        description = (repo.get('description', '') or '').lower()
        name = (repo.get('name', '') or '').lower()
        topics = [t.lower() for t in repo.get('topics', [])]

        if category_name == 'modeling':
            matches = _matches_modeling(description, name, topics)
        else:
            # Check if any of the keywords match
            matches = any(
                (keyword in description if keyword != 'ai' else (' ai ' in description or ' ai-' in description)) or
                (keyword in name if keyword != 'ai' else (' ai ' in name or ' ai-' in name)) or
                any(keyword == topic.strip() for topic in topics)
                for keyword in keywords
            )
        
        if matches:
            matching_repos.append(repo)
        else:
            non_matching_repos.append(repo)
            
    return matching_repos, non_matching_repos

def display_analysis(table_repos, category):
    """Pie chart + table for *category*. *table_repos* must be the same list as the main repository table."""
    # Define keyword sets for each category
    keyword_sets = {
        'no-code': ['nocode', 'no-code'],
        'modeling': ['model', 'modeling', 'model-driven', 'model-based'],
        'uml': ['uml', 'unified modeling language'],
        'ai': ['ai', 'artificial intelligence']
    }
    
    # Define excluded repos for modeling category
    modeling_exclusions = {'langflow', 'ludwig', 'alan-sdk-web', 'otto-m8'}
    
    # Filter out specific repos for modeling category
    repos_to_analyze = table_repos
    if category == 'modeling':
        repos_to_analyze = [
            repo for repo in table_repos if repo["name"] not in modeling_exclusions
        ]

    allowed_urls = frozenset(
        r.get("html_url") for r in table_repos if r.get("html_url")
    )

    matching_repos, _non_matching_repos = analyze_repos_multiple_keywords(
        repos_to_analyze,
        keyword_sets[category],
        category,
    )

    # Hard guarantee: listed rows are only repos from the table list (same slider-filtered set).
    matching_repos = [r for r in matching_repos if r.get("html_url") in allowed_urls]
    n_match = len(matching_repos)
    n_non_match = len(repos_to_analyze) - n_match
    
    fig = go.Figure(data=[go.Pie(
        labels=[f'Mentions {category}', f'No {category} mention'],
        values=[n_match, n_non_match],
        hole=0.3,
        marker_colors=['#2ecc71', '#e74c3c']
    )])
    
    fig.update_layout(
        title=f'Distribution of {category} mentions in Low-Code Tools',
        showlegend=True,
        width=700,
        height=500,
        annotations=[{
            'text': f'Total: {len(repos_to_analyze)}',
            'x': 0.5,
            'y': 0.5,
            'font_size': 20,
            'showarrow': False
        }]
    )
    
    st.plotly_chart(fig)
    
    if matching_repos:
        st.write(f"### Low-Code Tools Mentioning '{category}'")
        data = [{
            'Name': repo['name'],
            'Description': repo.get('description', 'No description'),
            'Stars': repo.get('stargazers_count', 0)
        } for repo in matching_repos]
        st.table(data)
    else:
        st.write(f"No repositories found mentioning '{category}'")
