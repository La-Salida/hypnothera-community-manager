# Hypnothera Subreddit Community Manager

Manages your r/Hypnotheraai community with regular content, engagement, and growth.

## Why This is Different (Safer)

Unlike the "Reply Guy" bot that posts in other subreddits:
- **It's YOUR community** — You can be promotional
- **Lower ban risk** — You're the creator posting in your own space
- **More transparent** — Users know it's official
- **Sustainable** — Building your own audience, not gaming someone else's

## What It Does

### Daily Routine

1. **Weekly Threads** (scheduled by day)
   - Monday: Manifestation thread
   - Wednesday: Sleep support
   - Friday: Featured session

2. **Daily Content** (1 post per day)
   - Tips & tricks
   - Success stories
   - Questions for engagement
   - Feature highlights

3. **Community Engagement**
   - Replies to 3 unanswered comments daily
   - Friendly, supportive tone
   - Low-key mentions of Hypnothera features

## Setup

Same as Reply Guy:

```bash
# Install dependencies
pip install selenium webdriver-manager

# Set credentials
export REDDIT_USERNAME="your_username"
export REDDIT_PASSWORD="your_password"
export PACKETSTREAM_PROXY="your_proxy"  # optional
```

## Run

```bash
# Run daily routine once
python hypnothera_community_manager.py

# Or set up as daily cron
0 10 * * * cd /path/to/hypnothera-community-manager && python hypnothera_community_manager.py
```

## Content Strategy

### Weekly Threads

**Monday Manifestation**
- Community discussion about goals
- Success stories
- Accountability
- Pinned all week

**Wednesday Sleep Support**
- Mid-week check-in
- Sleep tips
- Session recommendations

**Friday Featured Session**
- Highlights a specific Hypnothera session
- Drives traffic to app
- Pinned over weekend

### Daily Posts

Rotates between:
1. **Tips** — Quick actionable advice
2. **Success Stories** — User testimonials (you provide these)
3. **Questions** — Engagement bait to drive comments
4. **Feature Highlights** — Showcase app capabilities

## Customization

### Add Your Success Stories

Edit `DAILY_CONTENT_TEMPLATES` in the code:

```python
{
    'type': 'success_story',
    'title': 'Success Story: Real User Results',
    'content': '''"{testimonial}" — {user_name}

{context}

Start your journey at hypnothera.ai''',
    'flair': 'Success Story'
}
```

### Add More Tips

Edit the `TIPS` list:

```python
TIPS = [
    {
        'title': 'Your Tip Title',
        'content': 'Detailed explanation of the tip...'
    },
    # Add more...
]
```

### Change Weekly Schedule

Edit `WEEKLY_THREADS`:

```python
WEEKLY_THREADS = [
    {
        'day': 'tuesday',  # Change day
        'title': 'Your Thread Title',
        'content': 'Thread content...',
        'flair': 'Discussion',
        'pin': True  # Pin it?
    },
]
```

## Monitoring

Check logs:
```bash
tail -f hypnothera_community.log
```

Expected output:
```
2026-02-12 10:00:15 - INFO - 🚀 Starting daily community routine
2026-02-12 10:00:20 - INFO - ✅ Login successful
2026-02-12 10:00:35 - INFO - Posted weekly thread: Weekly Manifestation Thread
2026-02-12 10:05:42 - INFO - Posted daily content: Quick Hypnosis Tip: Start with 60 seconds
2026-02-12 10:08:15 - INFO - ✅ Replied to comment (1/3)
2026-02-12 10:12:30 - INFO - ✅ Daily routine complete. Made 2 posts.
```

## Growth Strategy

This bot grows your community by:

1. **Consistent Content** — Daily posts keep community active
2. **Engagement** — Replying to every comment builds relationships
3. **Value First** — Tips and stories, not just promotion
4. **Soft Promotion** — Hypnothera links in context, not spam

### Cross-Posting Strategy

Manually cross-post your best community posts to:
- r/selfimprovement (if relevant)
- r/sleep (for sleep content)
- r/lawofattraction (for manifestation content)

This drives traffic TO your community.

## Safety

Even in your own sub:
- Don't spam (1-2 posts/day max)
- Don't over-promote (80% value, 20% promotion)
- Reply genuinely, not robotically
- Use the bot as a helper, not replacement

## Manual Override

The bot won't:
- Pin posts if you're not a mod
- Delete anything
- Ban users
- Change subreddit settings

You stay in full control.

## Future Enhancements

- [ ] Pull real success stories from your database
- [ ] Auto-feature top posts from the week
- [ ] Welcome message for new subscribers
- [ ] Cross-post detection and auto-engagement
- [ ] Analytics tracking (subscriber growth, engagement rates)
