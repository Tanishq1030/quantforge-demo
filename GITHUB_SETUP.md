# 🚀 GitHub Setup - Quick Commands

## Step 1: Create GitHub Repo (DO THIS FIRST)

1. Go to: https://github.com/new
2. Repository name: `quantforge-demo`
3. Description: `Multi-Agent AI for Financial Markets - GSoC 2026 Demo`
4. Visibility: **PUBLIC** ✅
5. Do NOT check "Initialize with README"
6. Click "Create repository"

---

## Step 2: Connect & Push (Copy-paste these commands)

### IMPORTANT: Replace YOUR_USERNAME with your GitHub username!

```bash
cd d:\QuantForge-ai\quantforge-demo

# Add remote (CHANGE YOUR_USERNAME!)
git remote add origin https://github.com/YOUR_USERNAME/quantforge-demo.git

# Push to GitHub
git branch -M main
git push -u origin main
```

**Example:**
If your GitHub is `johndoe`, use:
```bash
git remote add origin https://github.com/johndoe/quantforge-demo.git
```

---

## Step 3: Update README with Your Info

Open `README.md` and replace:

1. Line 282: `[Your Name]` → Your actual name
2. Line 283: `your.email@example.com` → Your email
3. Line 284: `[Your Profile]` → Your LinkedIn URL
4. Header section: Replace `YOUR_USERNAME` with your GitHub username

Then commit the changes:

```bash
git add README.md
git commit -m "Update author info"
git push
```

---

## Step 4: Verify on GitHub

Visit: `https://github.com/YOUR_USERNAME/quantforge-demo`

You should see:
- ✅ Professional README with demo instructions
- ✅ All files (connectors.py, demo.py, etc.)
- ✅ "Public" badge

---

## Step 5: Add Repository Topics (for discoverability)

On GitHub repo page:
1. Click ⚙️ next to "About"
2. Add topics: `python`, `machine-learning`, `finance`, `gsoc`, `gsoc2026`, `apache-beam`, `ai-agents`
3. Save

---

## Step 6: Test the Public Link

Share with a friend or open incognito:
`https://github.com/YOUR_USERNAME/quantforge-demo`

Should be publicly viewable! 🎉

---

## Troubleshooting

**Error: "remote origin already exists"**
```bash
git remote remove origin
# Then run the git remote add command again
```

**Error: "Permission denied"**
- Use GitHub Desktop OR
- Set up SSH keys: https://docs.github.com/en/authentication

**Need to change repo name?**
- GitHub repo Settings → Rename

---

## Next: Email Template

Once repo is live, use this for Beam outreach:

```
Subject: GSoC 2026 Interest - QuantForge Multi-Agent AI + Beam ML Pipelines

Hi Beam community,

I'm [Your Name], building QuantForge—a multi-agent AI for financial analysis.
Just open-sourced the demo: https://github.com/YOUR_USERNAME/quantforge-demo

Try it (5 seconds):
  git clone https://github.com/YOUR_USERNAME/quantforge-demo.git
  cd quantforge-demo
  pip install -r requirements.txt
  python demo.py

Features:
- 7 data sources with auto-fallback
- Designed for Apache Beam integration (ML pipelines for multi-asset streaming)
- Production-ready (rate limiting, retries, logging)

Currently learning DS/algo (12-week intensive) while building this solo.
Looking for good-first-issues in sdks/python to start contributing!

Background: Python, PyTorch, FastAPI, PostgreSQL, Weaviate, Redis
GitHub: https://github.com/YOUR_USERNAME
LinkedIn: [Your Profile]

Thanks,
[Your Name]
```

---

## Timeline

- ✅ **Now:** Repo created
- ✅ **Tonight:** Update README, send email to dev@beam.apache.org
- 📅 **Dec 29-Jan 5:** Find & claim first issue
- 📅 **Jan 6-15:** Submit first PR
- 📅 **Feb 10:** Pitch GSoC proposal ideas
- 📅 **Mar 24-Apr 8:** Submit GSoC proposal

You're on track! 🎯
