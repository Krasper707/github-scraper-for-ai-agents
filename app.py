# app.py (Now with Fork Detection)

import streamlit as st
import requests
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
import io

# --- Core Scraping Logic (with Fork Detection) ---

def get_all_repo_info(user_or_org_url: str) -> list:
    """
    Finds all repository info (URL and type), handling pagination.
    Returns a list of dictionaries: [{'url': str, 'type': str}]
    """
    all_repo_info = []
    current_page_url = urljoin(user_or_org_url, "?tab=repositories")
    base_url = "https://github.com"
    page_num = 1
    
    while current_page_url:
        st.info(f"Analyzing repository list: Page {page_num}...")
        try:
            response = requests.get(current_page_url, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            st.error(f"Error fetching {current_page_url}: {e}")
            break

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Select the list items that contain each repository's data
        repo_list_items = soup.select("div#user-repositories-list li")

        if not repo_list_items and page_num == 1:
            st.warning("Could not find any repositories on the first page.")
            return []
            
        for item in repo_list_items:
            # Find the main link to the repository
            repo_link = item.select_one('h3 > a')
            if not repo_link:
                continue
            
            relative_url = repo_link['href']
            full_url = urljoin(base_url, relative_url)
            
            # --- NEW: Fork Detection Logic ---
            # Check for the "Forked from" span. Its presence indicates a fork.
            fork_span = item.find('span', string=lambda text: text and 'Forked from' in text)
            repo_type = "Fork" if fork_span else "Original"
            
            all_repo_info.append({'url': full_url, 'type': repo_type})

        # Pagination logic remains the same
        next_button = soup.find('a', {'rel': 'next'})
        if next_button and 'href' in next_button.attrs:
            current_page_url = urljoin(base_url, next_button['href'])
            page_num += 1
            time.sleep(0.5)
        else:
            current_page_url = None

    return all_repo_info

def scrape_readme(repo_url: str) -> str:
    """Scrapes the text content of the README.md from a single repository page."""
    try:
        response = requests.get(repo_url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        readme_article = soup.find('article', class_='markdown-body')
        
        return readme_article.get_text(separator=' ', strip=True) if readme_article else "README not found."
    except requests.RequestException:
        return "Could not fetch README (request failed)."

@st.cache_data(show_spinner=False)
def run_scraper(github_url: str) -> pd.DataFrame:
    """The main scraping process, decorated with caching."""
    repo_info_list = get_all_repo_info(github_url)
    
    if not repo_info_list:
        st.warning("No repositories found to scrape.")
        return pd.DataFrame()

    total_repos = len(repo_info_list)
    all_projects_data = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()

    for i, repo_info in enumerate(repo_info_list):
        url = repo_info['url']
        repo_type = repo_info['type']
        project_name = url.split('/')[-1]
        
        status_text.text(f"Scraping {i+1}/{total_repos}: {project_name}")
        progress_bar.progress((i + 1) / total_repos)

        readme_content = scrape_readme(url)
        all_projects_data.append({
            "Project Name": project_name,
            "Type": repo_type,  # Add the new 'Type' field
            "URL": url,
            "README Content": readme_content
        })
        time.sleep(0.25)
    
    status_text.success(f"✅ Scraping complete! Found {total_repos} repositories.")
    progress_bar.empty()
    
    df = pd.DataFrame(all_projects_data)

    # Reorder columns for better presentation
    if not df.empty:
        df = df[["Project Name", "Type", "URL", "README Content"]]
    
    return df

# --- Streamlit User Interface (mostly unchanged) ---

st.set_page_config(page_title="GitHub Scraper", page_icon="✨", layout="wide")

st.title("✨ GitHub Project Scraper")
st.markdown(
    "Enter a GitHub user or organization URL to scrape their public projects. "
    "The app identifies original projects vs. forks."
)

with st.form("scraper_form"):
    github_url = st.text_input(
        "GitHub URL", 
        placeholder="e.g., https://github.com/Krasper707"
    )
    submit_button = st.form_submit_button("Scrape Projects")

if submit_button and github_url:
    df = run_scraper(github_url)
    
    if not df.empty:
        st.subheader("📊 Scraped Data")
        st.dataframe(df)

        with st.expander("📄 Preview CSV Content"):
            csv_preview = df.to_csv(index=False)
            st.code(csv_preview, language='text')

        st.markdown("---")
        st.subheader("💾 Download Data")

        col1, col2 = st.columns(2)

        with col1:
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='GitHub_Projects')
            excel_data = output.getvalue()
            st.download_button(
                label="📥 Download as Excel (.xlsx)",
                data=excel_data,
                file_name=f"{github_url.split('/')[-1]}_projects.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        
        with col2:
            csv_data = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download as CSV (.csv)",
                data=csv_data,
                file_name=f"{github_url.split('/')[-1]}_projects.csv",
                mime="text/csv",
                use_container_width=True
            )

else:
    st.info("Please enter a URL and click the button to start.")