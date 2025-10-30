# 🚀 Vercel Deployment Guide - Presupuesto 2026 AI Chat

## Why Vercel?

✅ **Serverless** - No server management  
✅ **Auto-scaling** - Handles any traffic  
✅ **Free tier** - Generous limits  
✅ **Global CDN** - Fast worldwide  
✅ **GitHub integration** - Auto-deploy on push  
✅ **Custom domains** - Easy setup for ai.protosapiens.me  
✅ **Zero configuration** - Just deploy!  

---

## 📋 Prerequisites

1. **GitHub Account** (free)
2. **Vercel Account** (free - sign up with GitHub)
3. **OpenAI API Key**

---

## 🚀 Step-by-Step Deployment

### **Step 1: Create GitHub Repository**

1. Go to https://github.com/new

2. Create a new repository:
   - **Name:** `presupuesto-2026-chat`
   - **Description:** AI Chat Assistant for Presupuesto 2026 TikTok Analysis
   - **Visibility:** Private (recommended) or Public
   - **Initialize:** Don't add README, .gitignore, or license

3. Click "Create repository"

---

### **Step 2: Push Code to GitHub**

Open Terminal on your Mac:

```bash
cd "/Users/eos/Documents/tik tok extraction/Presupuesto 2026/chat_app/vercel"

# Initialize Git repository
git init

# Add all files
git add .

# Create first commit
git commit -m "Initial commit: Presupuesto 2026 AI Chat"

# Add your GitHub repository as remote
# Replace YOUR_USERNAME with your GitHub username
git remote add origin https://github.com/YOUR_USERNAME/presupuesto-2026-chat.git

# Push to GitHub
git branch -M main
git push -u origin main
```

**Enter your GitHub credentials when prompted.**

---

### **Step 3: Deploy to Vercel**

1. **Go to Vercel:** https://vercel.com/

2. **Sign Up / Login:**
   - Click "Sign Up" (if new)
   - Choose "Continue with GitHub"
   - Authorize Vercel to access your GitHub account

3. **Import Project:**
   - Click "Add New..." → "Project"
   - You'll see your GitHub repositories
   - Find `presupuesto-2026-chat`
   - Click "Import"

4. **Configure Project:**
   - **Framework Preset:** Other
   - **Root Directory:** `./` (leave as is)
   - **Build Command:** (leave empty)
   - **Output Directory:** `public`

5. **Add Environment Variable:**
   - Click "Environment Variables"
   - Add:
     - **Name:** `OPENAI_API_KEY`
     - **Value:** Your OpenAI API key (e.g., `sk-proj-...`)
   - Click "Add"

6. **Deploy:**
   - Click "Deploy"
   - Wait ~1 minute for deployment

7. **Success! 🎉**
   - You'll see: "🎉 Your project has been deployed!"
   - You'll get a URL like: `https://presupuesto-2026-chat.vercel.app`

---

### **Step 4: Test Your Deployment**

1. Click "Visit" or open the URL

2. You should see the chat interface

3. Try asking:
   > "What are the main findings from the sentiment analysis?"

4. You should get a response with sources!

---

### **Step 5: Add Custom Domain (ai.protosapiens.me)**

1. In Vercel dashboard, go to your project

2. Click "Settings" → "Domains"

3. Enter: `ai.protosapiens.me`

4. Click "Add"

5. Vercel will show DNS records you need to add:
   ```
   Type: A
   Name: ai
   Value: 76.76.21.21  (Vercel's IP)
   
   OR
   
   Type: CNAME
   Name: ai
   Value: cname.vercel-dns.com
   ```

6. Go to your DNS provider (e.g., GoDaddy, Cloudflare, Namecheap)

7. Add the DNS record

8. Wait 5-10 minutes for DNS propagation

9. Return to Vercel, click "Refresh"

10. Once verified: **https://ai.protosapiens.me** is live! ✅

---

## 📁 File Structure

```
vercel/
├── api/
│   └── chat.py          # Serverless API endpoint
├── public/
│   ├── index.html       # Frontend
│   ├── styles.css       # Styles
│   └── app.js           # JavaScript (updated for Vercel)
├── requirements.txt     # Python dependencies
├── vercel.json          # Vercel configuration
└── VERCEL_DEPLOYMENT.md # This file
```

---

## 🔧 How It Works

### **Frontend (Static)**
- Served from `/public` directory
- Hosted on Vercel's global CDN
- Lightning fast

### **Backend (Serverless Function)**
- `/api/chat` endpoint
- Python function runs on-demand
- Auto-scales to zero when not used
- Spins up in milliseconds

### **Knowledge Base**
- Embedded directly in the API function
- Contains summaries of all analysis
- No database needed for this approach
- Fast responses

---

## 💰 Cost Breakdown

### **Vercel (Free Tier)**
- 100 GB bandwidth/month
- Unlimited API calls
- Automatic SSL
- **Cost: $0**

### **OpenAI API**
- Embeddings: ~$0.02 per query
- GPT-4: ~$0.03-0.05 per query
- **Est. 100 queries: ~$3-5**
- **Est. 1000 queries: ~$30-50**

### **Total**
- Setup: $0
- Monthly: $0 (Vercel) + OpenAI usage
- Much cheaper than VPS!

---

## 🔄 Auto-Deploy on Updates

Every time you push to GitHub, Vercel auto-deploys!

```bash
# Make changes to your code
# Then:
git add .
git commit -m "Update: improved responses"
git push

# Vercel automatically deploys the new version!
# Live in ~1 minute
```

---

## 🎨 Customization

### **Change LLM Model** (lower cost)

Edit `api/chat.py`:

```python
# Line ~190
model="gpt-3.5-turbo",  # Was: gpt-4-turbo-preview
```

Save, commit, push → Auto-deploys!

**GPT-3.5 is 10x cheaper** (~$0.002/query vs ~$0.02/query)

### **Update Frontend**

Edit files in `public/`  
Commit and push → Live!

### **Add More Context**

Edit the `_retrieve_context` method in `api/chat.py`  
Add more summary contexts from your analysis

---

## 📊 Monitoring

### **View Logs**

1. Go to Vercel dashboard
2. Click your project
3. Click "Functions"
4. Click any function call to see logs

### **Analytics**

Vercel provides:
- Traffic analytics
- Function invocations
- Error rates
- Response times

All in the dashboard!

---

## 🔐 Security

✅ **HTTPS by default** - All traffic encrypted  
✅ **Environment variables** - API key never exposed  
✅ **Serverless** - No server to hack  
✅ **DDoS protection** - Built-in  
✅ **Rate limiting** - Can add easily  

---

## 🆘 Troubleshooting

### **Deployment Failed**

Check:
1. `requirements.txt` has correct packages
2. `vercel.json` is valid JSON
3. Environment variable is set

### **API Returns Error**

Check logs in Vercel:
- Dashboard → Project → Functions → View logs
- Look for OpenAI API errors
- Verify API key is correct

### **"Cannot connect to API"**

1. Check browser console (F12)
2. Verify `/api/chat` endpoint exists
3. Check CORS headers in `chat.py`

### **Slow Responses**

- Cold start (first request after idle): ~2-3 seconds
- Warm requests: ~500ms-1s
- Normal for serverless!

---

## 🚀 Advanced: Use Vector Database

For better context retrieval, integrate with:

### **Option A: Pinecone** (Easiest)
```bash
pip install pinecone-client

# In Vercel, add environment variables:
# PINECONE_API_KEY
# PINECONE_INDEX_NAME
```

### **Option B: Supabase** (Free tier)
```bash
pip install supabase

# Add SUPABASE_URL and SUPABASE_KEY
```

### **Option C: Upstash Vector** (Serverless)
```bash
pip install upstash-vector

# Add UPSTASH_VECTOR_URL and UPSTASH_VECTOR_TOKEN
```

---

## ✅ Deployment Checklist

- [ ] GitHub repository created
- [ ] Code pushed to GitHub
- [ ] Vercel account created
- [ ] Project imported to Vercel
- [ ] OPENAI_API_KEY environment variable set
- [ ] Deployment successful
- [ ] Tested chat functionality
- [ ] Custom domain added (optional)
- [ ] DNS configured (if using custom domain)

---

## 🎉 You're Done!

Your AI Chat Assistant is now:

✅ **Live** at https://your-project.vercel.app (or ai.protosapiens.me)  
✅ **Serverless** - No servers to manage  
✅ **Auto-scaling** - Handles any load  
✅ **Auto-deploying** - Push to GitHub → Live in 1 minute  
✅ **Free hosting** - Only pay for OpenAI API usage  
✅ **Global CDN** - Fast everywhere  
✅ **HTTPS** - Secure by default  

---

## 📞 Next Steps

1. **Share the link** with your team/stakeholders
2. **Monitor usage** in Vercel dashboard
3. **Track OpenAI costs** at platform.openai.com/usage
4. **Iterate** - Push updates as needed

---

## 💡 Tips

1. **Vercel CLI** for local testing:
   ```bash
   npm i -g vercel
   vercel dev  # Runs locally on localhost:3000
   ```

2. **Preview deployments** - Every PR gets its own URL

3. **Rollback** - Instant rollback to previous deployments

4. **Environment per branch** - Different API keys for dev/prod

---

**🚀 Much simpler than traditional deployment, and scales infinitely!**

