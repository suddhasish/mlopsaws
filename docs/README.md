# 📚 MLOps Documentation

## 🎯 START HERE

**Everything you need is in ONE guide:**

### [📖 COMPLETE_SETUP_GUIDE.md](./COMPLETE_SETUP_GUIDE.md)

**This is the ONLY guide you need to read.**

It contains:
- ✅ Complete end-to-end setup (nothing missing)
- ✅ Clear marking of Manual vs Automated steps
- ✅ GitHub Actions automation (recommended method)
- ✅ PowerShell scripts reference (local alternative)
- ✅ Step-by-step with exact commands
- ✅ Troubleshooting for common issues
- ✅ Production deployment guide

**Time:** 2-3 hours (one-time setup)  
**Result:** Fully automated MLOps infrastructure on AWS

---

## 📋 Other Documentation (Reference Only)

The root folder contains additional documentation for specific topics:

| File | Purpose | When to Read |
|------|---------|--------------|
| `README.md` | Project overview | After setup to understand architecture |
| `QUICKSTART.md` | 2-day hands-on learning | After deployment for practical exercises |
| `PROJECT_SUMMARY.md` | What you built | After completion to review achievements |
| `MODEL_APPROVAL_GUIDE.md` | Model registry workflow | When implementing model governance |
| `ENVIRONMENT_STRATEGY.md` | Multi-environment setup | When scaling to staging/production |

**Documentation in this folder (docs/):**

| File | Purpose | When to Read |
|------|---------|--------------|
| [COMPLETE_SETUP_GUIDE.md](./COMPLETE_SETUP_GUIDE.md) | ⭐ **THE MAIN GUIDE** | Start here (required) |
| [TRUST_POLICY_BEST_PRACTICES.md](./TRUST_POLICY_BEST_PRACTICES.md) | 🔐 Production-ready OIDC setup | Before production deployment |
| [TRUST_POLICY_QUICK_REFERENCE.md](./TRUST_POLICY_QUICK_REFERENCE.md) | 🔐 Quick decision guide | When choosing trust policy approach |
| [CONSOLIDATION_SUMMARY.md](./CONSOLIDATION_SUMMARY.md) | 📋 Documentation history | Optional - explains doc structure |

**All root folder docs are OPTIONAL and provide additional context.**

---

## 🔐 Security Note: Trust Policies

**Important:** If setting up for production or a team:

📖 **Read:** [TRUST_POLICY_BEST_PRACTICES.md](./TRUST_POLICY_BEST_PRACTICES.md)

**Why?** The default setup uses personal GitHub usernames in trust policies. When users leave:
- ❌ **Personal setup:** Requires manual AWS/GitHub updates
- ✅ **Organization setup:** No changes needed (just remove from team)

**Quick Guide:** [TRUST_POLICY_QUICK_REFERENCE.md](./TRUST_POLICY_QUICK_REFERENCE.md)

---

## 🚀 Quick Start

1. **Read:** [COMPLETE_SETUP_GUIDE.md](./COMPLETE_SETUP_GUIDE.md)
2. **Follow:** Steps 1-6 (Manual setup + Automated deployment)
3. **Monitor:** GitHub Actions for automated deployment
4. **Done:** Infrastructure deployed, model trained, endpoint live!

---

## 📞 Questions?

- **Setup issues?** → Check [COMPLETE_SETUP_GUIDE.md](./COMPLETE_SETUP_GUIDE.md) → Section 10 (Troubleshooting)
- **Architecture questions?** → See `../README.md`
- **Cost optimization?** → See [COMPLETE_SETUP_GUIDE.md](./COMPLETE_SETUP_GUIDE.md) → Section 8 (Monitoring)

---

**Last Updated:** November 4, 2025  
**Version:** 3.0 - Single Consolidated Guide
