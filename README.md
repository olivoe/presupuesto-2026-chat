# 💬 Presupuesto 2026 AI Chat Assistant

AI-powered chat interface for exploring insights from the Presupuesto 2026 TikTok analysis project.

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/YOUR_USERNAME/presupuesto-2026-chat)

---

## 🌟 Features

- **Intelligent Q&A** - Ask questions about the analysis in natural language
- **Context-Aware** - Remembers conversation history for follow-up questions
- **Source Attribution** - Shows which data informed each answer
- **Beautiful UI** - ChatGPT-style interface
- **Serverless** - Scales automatically, no servers to manage
- **Fast** - Global CDN delivery

---

## 📊 About the Analysis

This chat assistant provides insights on:

- **24 TikTok posts** about Guatemala's Presupuesto 2026
- **2,042 comments** with sentiment analysis
- **Interest Index rankings** for posts
- **Topic analysis** (corruption, government, infrastructure, etc.)
- **Psychosocial insights** and strategic recommendations

### Key Findings

- 🔴 **95.9% negative sentiment** (1,957 comments)
- 🟢 **2.1% positive sentiment** (43 comments)
- ⚪ **2.1% neutral sentiment** (42 comments)
- 🏆 **Top topic:** Corruption (229 mentions)

---

## 🚀 Quick Deploy to Vercel

1. **Fork this repository**

2. **Deploy to Vercel:**
   - Go to [vercel.com](https://vercel.com)
   - Import your forked repository
   - Add environment variable:
     - `OPENAI_API_KEY` = your OpenAI API key
   - Click "Deploy"

3. **Done!** Your chat is live in ~1 minute

---

## 💻 Local Development

```bash
# Install Vercel CLI
npm i -g vercel

# Set environment variable
export OPENAI_API_KEY='your_key_here'

# Run locally
vercel dev
```

Open http://localhost:3000

---

## 📁 Project Structure

```
├── api/
│   └── chat.py          # Serverless API endpoint
├── public/
│   ├── index.html       # Frontend HTML
│   ├── styles.css       # Styles
│   └── app.js           # JavaScript
├── requirements.txt     # Python dependencies
├── vercel.json          # Vercel configuration
└── README.md            # This file
```

---

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | Your OpenAI API key | Yes |

### Change LLM Model

Edit `api/chat.py` line 190:

```python
# Use GPT-3.5 (10x cheaper)
model="gpt-3.5-turbo"

# Or GPT-4 (better quality)
model="gpt-4-turbo-preview"
```

---

## 💡 Example Questions

- "What are the main findings from the sentiment analysis?"
- "Which post has the highest Interest Index?"
- "What are the most common topics in negative comments?"
- "Tell me about the psychosocial insights"
- "What are the strategic communication recommendations?"

---

## 💰 Cost Estimates

### Vercel
- **Hosting:** Free (generous limits)
- **SSL:** Free
- **CDN:** Free

### OpenAI API
- **Per query:** ~$0.02-0.05 (GPT-4)
- **100 queries:** ~$3-5
- **1000 queries:** ~$30-50

**Use GPT-3.5 for 10x cost reduction!**

---

## 🔐 Security

- ✅ HTTPS by default
- ✅ Environment variables for secrets
- ✅ Serverless architecture
- ✅ No database (stateless)
- ✅ CORS configured

---

## 📈 Monitoring

View logs and analytics in your Vercel dashboard:
- Function invocations
- Error rates
- Response times
- Traffic analytics

---

## 🛠️ Tech Stack

**Frontend:**
- HTML5, CSS3, JavaScript
- Marked.js (Markdown rendering)
- Highlight.js (Code highlighting)

**Backend:**
- Python (Serverless Functions)
- OpenAI GPT-4 Turbo
- Vercel Edge Network

---

## 📝 License

Private project - Presupuesto 2026 Analysis

---

## 🤝 Contributing

This is a private analysis project. For questions or suggestions, contact the project maintainer.

---

## 📞 Support

- **Deployment Guide:** See `VERCEL_DEPLOYMENT.md`
- **Issues:** Check Vercel dashboard logs
- **OpenAI API:** Monitor usage at platform.openai.com

---

## 🎯 Roadmap

- [ ] Add vector database for better context retrieval
- [ ] Implement conversation export
- [ ] Add analytics dashboard
- [ ] Multi-language support
- [ ] Voice input support

---

**Built with ❤️ for data-driven insights**

🌐 **Live Demo:** [ai.protosapiens.me](https://ai.protosapiens.me)

