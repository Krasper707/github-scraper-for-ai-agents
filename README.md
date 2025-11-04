# Github Scraper for AI Agents

- This is just a tool for AI Agents to take use of. Cuz I hate it when they say "oH I cANNoT sCrApE gItHub ReADmEs, i HaVE no TooL" ; Well now you do.

- Just clone the repo

```bash
git clone https://github.com/Krasper707/github-scraper.git
cd github-scraper
```

### Create a Virtual Environment

It's highly recommended to use a virtual environment to manage project dependencies.

- **On macOS/Linux:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```
- **On Windows:**
  ```bash
  python -m venv venv
  .\venv\Scripts\activate
  ```

### Install Required Packages

The `requirements.txt` file contains all the necessary libraries.

```bash
pip install -r requirements.txt
```

---

How to Use

1.  **Enter URL:** Copy and paste the URL of the GitHub user or organization you want to scrape into the input box (e.g., `https://github.com/google` or `https://github.com/torvalds`).
2.  **Scrape:** Click the "Scrape Projects" button.
3.  **Monitor Progress:** Watch the progress bar as the app fetches repository information and scrapes each README file.
4.  **View Results:** Once complete, the data will be displayed in an interactive table.
5.  **Preview & Download:**
    - Click the "Preview CSV Content" expander to see the raw text data.
    - Click the "Download as Excel (.xlsx)" or "Download as CSV (.csv)" button to save the data to your computer.

- It's not Rocket Science.

## 📄 License

This project is licensed under the MIT License. See the `LICENSE` file for details.
