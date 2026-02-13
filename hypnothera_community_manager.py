#!/usr/bin/env python3
"""
Hypnothera Subreddit Community Manager

Manages the r/Hypnotheraai community with regular content,
engagement, and growth tactics.

This is SAFER than the reply guy because:
- It's YOUR subreddit
- You can be promotional (it's your product)
- Lower risk of ban
- More transparent
"""

import os
import sys
import time
import json
import random
import logging
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('hypnothera_community.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class CommunityPost:
    """A post to make in the community"""
    title: str
    content: str
    post_type: str  # 'announcement', 'featured', 'discussion', 'tip'
    flair: str
    pin: bool = False


class HypnotheraCommunityManager:
    """Manages the r/Hypnotheraai subreddit"""
    
    SUBREDDIT = "Hypnotheraai"
    STATE_FILE = Path('community_manager_state.json')
    
    # Timing constants
    SHORT_WAIT = 3
    MEDIUM_WAIT = 6
    LOGIN_WAIT = 5
    LOGIN_WAIT_MAX = 8
    REPLY_WAIT_MIN = 60
    REPLY_WAIT_MAX = 180
    POST_WAIT_MIN = 300
    POST_WAIT_MAX = 600
    MAX_POSTS_TO_CHECK = 10
    
    # Typing delays
    TYPING_DELAY_MIN = 0.01
    TYPING_DELAY_MAX = 0.15
    TITLE_TYPING_DELAY_MIN = 0.03
    TITLE_TYPING_DELAY_MAX = 0.1
    
    # Content templates
    WEEKLY_THREADS = [
        {
            'day': 'monday',
            'title': 'Weekly Manifestation Thread - What are you working on?',
            'content': '''Welcome to the weekly manifestation thread!

This is a space to share:
- What you're working on manifesting
- Success stories from the past week
- Challenges you're facing
- Tips that have worked for you

Let's support each other in achieving our goals. 🎯''',
            'flair': 'Discussion',
            'pin': True
        },
        {
            'day': 'wednesday',
            'title': 'Sleep Support Wednesday - Share your sleep wins',
            'content': '''Mid-week check in! How's your sleep been?

Share:
- Sleep wins from this week
- Sessions that helped you
- Questions about sleep hypnosis
- Tips for better rest

Sleep is the foundation of everything. Let's talk about it. 💤''',
            'flair': 'Discussion',
            'pin': False
        },
        {
            'day': 'friday',
            'title': 'Free Session Friday - Featured hypnosis of the week',
            'content': '''Happy Friday! Here's this week's featured free session:

🎙 **Session Title**
*Category: [Category]*
*Duration: [X] minutes*

This session focuses on [description].

Try it this weekend and let us know how it goes!

[Link to session]

---

Want more? Check out our full library at hypnothera.ai''',
            'flair': 'Featured',
            'pin': True
        },
    ]
    
    DAILY_CONTENT_TEMPLATES = [
        {
            'type': 'tip',
            'title': 'Quick Hypnosis Tip: {tip_title}',
            'content': '''{tip_content}

What's your favorite hypnosis tip? Share in the comments!

---

New to hypnosis? Try Hypnothera free at hypnothera.ai''',
            'flair': 'Tips & Tricks'
        },
        {
            'type': 'success_story',
            'title': 'Success Story: {story_title}',
            'content': '''{story_content}

Have you had success with hypnosis? We'd love to hear your story!

---

Start your own success story at hypnothera.ai''',
            'flair': 'Success Story'
        },
        {
            'type': 'question',
            'title': 'Question of the Day: {question}',
            'content': '''{context}

Drop your answers in the comments!

---

Want personalized hypnosis? Check out hypnothera.ai''',
            'flair': 'Discussion'
        },
        {
            'type': 'feature_highlight',
            'title': 'Feature Spotlight: {feature_name}',
            'content': '''Did you know Hypnothera has {feature_name}?

{feature_description}

Try it out: hypnothera.ai

---

What feature would you like to see next? Let us know!''',
            'flair': 'Announcement'
        }
    ]
    
    TIPS = [
        {
            'title': 'Start with 60 seconds',
            'content': 'Don\'t try to jump into 20-minute sessions. Start with 60 seconds. Make it so easy you can\'t say no. Once that sticks, scale up.'
        },
        {
            'title': 'Same time, same place',
            'content': 'Your brain loves patterns. Do your hypnosis at the same time and place every day. It becomes a trigger for relaxation.'
        },
        {
            'title': 'Stack your habits',
            'content': 'Attach hypnosis to an existing habit. "After I brush my teeth, I\'ll do 5 minutes of hypnosis." This is habit stacking.'
        },
        {
            'title': 'Track it visibly',
            'content': 'Use a calendar. Put an X on every day you do hypnosis. Don\'t break the chain. Visual feedback is powerful.'
        },
        {
            'title': 'Headphones matter',
            'content': 'Good headphones make a huge difference. Noise-canceling is ideal, but even basic earbuds work better than phone speakers.'
        }
    ]
    
    def __init__(self, dry_run: bool = False):
        self.driver = None
        self.proxy_url = os.getenv('PACKETSTREAM_PROXY')
        self.dry_run = dry_run
        self.errors: List[str] = []
        
    def load_state(self) -> Dict:
        """Load persistent state from file"""
        if self.STATE_FILE.exists():
            try:
                return json.loads(self.STATE_FILE.read_text())
            except Exception as e:
                logger.warning(f"Could not load state: {e}")
        return {}
    
    def save_state(self, state: Dict) -> None:
        """Save persistent state to file"""
        try:
            self.STATE_FILE.write_text(json.dumps(state, indent=2))
        except Exception as e:
            logger.error(f"Could not save state: {e}")
    
    def setup_browser(self) -> webdriver.Chrome:
        """Setup Chrome with proxy"""
        logger.info("Setting up Chrome...")
        
        chrome_options = Options()
        
        if self.proxy_url:
            chrome_options.add_argument(f'--proxy-server={self.proxy_url}')
        
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''Object.defineProperty(navigator, 'webdriver', {get: () => undefined})'''
        })
        
        return driver
    
    def login(self, username: str, password: str) -> bool:
        """Login to Reddit"""
        logger.info("Logging in...")  # Don't log username
        
        self.driver.get('https://www.reddit.com/login/')
        time.sleep(random.uniform(self.SHORT_WAIT, self.MEDIUM_WAIT))
        
        try:
            # Username
            username_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, 'login-username'))
            )
            username_field.click()
            time.sleep(0.5)
            
            for char in username:
                username_field.send_keys(char)
                time.sleep(random.uniform(0.05, 0.15))
            
            time.sleep(0.5)
            
            # Password
            password_field = self.driver.find_element(By.ID, 'login-password')
            password_field.click()
            time.sleep(0.5)
            
            for char in password:
                password_field.send_keys(char)
                time.sleep(random.uniform(0.05, 0.15))
            
            time.sleep(1)
            password_field.send_keys(Keys.RETURN)
            time.sleep(random.uniform(self.LOGIN_WAIT, self.LOGIN_WAIT_MAX))
            
            if 'reddit.com' in self.driver.current_url and 'login' not in self.driver.current_url:
                logger.info("✅ Login successful")
                return True
            return False
            
        except Exception as e:
            logger.error(f"❌ Login error: {e}")
            return False
    
    def create_post(self, post: CommunityPost) -> Tuple[bool, Optional[str]]:
        """Create a post in r/Hypnotheraai"""
        logger.info(f"Creating post: {post.title[:50]}...")
        
        if self.dry_run:
            logger.info("DRY RUN - Would create post:")
            logger.info(f"  Title: {post.title}")
            logger.info(f"  Type: {post.post_type}")
            logger.info(f"  Flair: {post.flair}")
            return True, None
        
        try:
            # Navigate to submit page
            submit_url = f"https://www.reddit.com/r/{self.SUBREDDIT}/submit/"
            self.driver.get(submit_url)
            time.sleep(random.uniform(self.SHORT_WAIT, self.MEDIUM_WAIT))
            
            # Enter title
            title_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="post-title-text"]'))
            )
            title_field.click()
            time.sleep(0.5)
            
            for char in post.title:
                title_field.send_keys(char)
                time.sleep(random.uniform(self.TITLE_TYPING_DELAY_MIN, self.TITLE_TYPING_DELAY_MAX))
            
            time.sleep(1)
            
            # Enter content
            content_field = self.driver.find_element(By.CSS_SELECTOR, '[data-testid="comment-submission-form-richtext"]')
            content_field.click()
            time.sleep(0.5)
            
            # Type content
            for char in post.content:
                content_field.send_keys(char)
                time.sleep(random.uniform(self.TYPING_DELAY_MIN, self.TYPING_DELAY_MAX * 0.3))
            
            time.sleep(2)
            
            # Select flair if provided
            if post.flair:
                try:
                    flair_btn = self.driver.find_element(By.CSS_SELECTOR, '[data-testid="post-form-flair-button"]')
                    flair_btn.click()
                    time.sleep(1)
                    
                    # Find and click the flair
                    flair_option = self.driver.find_element(By.XPATH, f"//span[contains(text(), '{post.flair}')]")
                    flair_option.click()
                    time.sleep(1)
                    
                    apply_btn = self.driver.find_element(By.CSS_SELECTOR, '[data-testid="flair-selector-apply"]')
                    apply_btn.click()
                    time.sleep(1)
                except Exception as e:
                    logger.warning(f"Could not set flair: {e}")
            
            # Submit
            submit_btn = self.driver.find_element(By.CSS_SELECTOR, '[data-testid="post-submit-button"]')
            submit_btn.click()
            time.sleep(random.uniform(4, 7))
            
            # Check if posted
            if '/comments/' in self.driver.current_url:
                logger.info("✅ Post created successfully")
                
                # Pin if requested
                if post.pin:
                    self.pin_post()
                
                return True, None
            else:
                error_msg = "Post may not have been created - URL check failed"
                logger.error(f"❌ {error_msg}")
                return False, error_msg
                
        except Exception as e:
            error_msg = f"Error creating post: {e}"
            logger.error(f"❌ {error_msg}")
            self.errors.append(error_msg)
            return False, error_msg
    
    def pin_post(self) -> None:
        """Pin the current post"""
        logger.info("Pinning post...")
        
        if self.dry_run:
            logger.info("DRY RUN - Would pin post")
            return
        try:
            # Click mod actions
            mod_btn = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="moderator-actions-menu"]'))
            )
            mod_btn.click()
            time.sleep(1)
            
            # Click pin
            pin_option = self.driver.find_element(By.XPATH, "//span[contains(text(), 'Pin')]")
            pin_option.click()
            time.sleep(2)
            
            logger.info("✅ Post pinned")
        except Exception as e:
            logger.warning(f"Could not pin post: {e}")
    
    def reply_to_comments(self, max_replies: int = 5) -> None:
        """Reply to unanswered comments in the sub"""
        logger.info(f"Looking for comments to reply to (max {max_replies})...")
        
        if self.dry_run:
            logger.info("DRY RUN - Would look for comments to reply to")
            return
        
        # Go to subreddit
        self.driver.get(f"https://www.reddit.com/r/{self.SUBREDDIT}/new/")
        time.sleep(random.uniform(3, 6))
        
        replies_made = 0
        
        try:
           # Find posts and extract their URLs first to avoid stale element references
            post_elements = self.driver.find_elements(By.CSS_SELECTOR, '[data-testid="post-container"]')[:10]
            post_urls = []
            
            # Extract URLs from posts
            for post in post_elements:
                try:
                    # Find the link element within the post
                    link_element = post.find_element(By.CSS_SELECTOR, 'a[data-click-id="body"]')
                    post_url = link_element.get_attribute('href')
                    if post_url and not post_url.startswith('http'):
                        # Convert relative URLs to absolute
                        post_url = f"https://www.reddit.com{post_url}"
                    post_urls.append(post_url)
                except Exception as e:
                    logger.debug(f"Could not extract URL from post: {e}")
                    continue
            
            logger.info(f"Found {len(post_urls)} posts to check for comments")
            
            # Process each post by navigating directly to its URL
            for post_url in post_urls:
                if replies_made >= max_replies:
                    break
                
                try:
                    # Navigate directly to post URL
                    self.driver.get(post_url)
                    time.sleep(random.uniform(3, 5))
                    
                    # Find comments without replies
                    comments = self.driver.find_elements(By.CSS_SELECTOR, '[data-testid="comment"]')
                    
                    for comment in comments:
                        # Check if it's our comment (skip)
                        try:
                            author = comment.find_element(By.CSS_SELECTOR, '[data-testid="comment_author_link"]').text
                            if author == os.getenv('REDDIT_USERNAME'):
                                continue
                        except:
                            pass
                        
                        # Check if already replied
                        replies = comment.find_elements(By.CSS_SELECTOR, '[data-testid="comment-replies"]')
                        if replies:
                            continue
                        
                        # Reply
                        reply_btn = comment.find_element(By.CSS_SELECTOR, '[data-testid="comment-reply-button"]')
                        reply_btn.click()
                        time.sleep(1)
                        
                        # Type reply
                        reply_box = comment.find_element(By.CSS_SELECTOR, '[data-testid="comment-submission-form-richtext"]')
                        reply_text = self.generate_reply()
                        
                        for char in reply_text:
                            reply_box.send_keys(char)
                            time.sleep(random.uniform(0.03, 0.1))
                        
                        time.sleep(1)
                        
                        # Submit
                        submit_btn = comment.find_element(By.CSS_SELECTOR, '[data-testid="comment-submission-form-submit"]')
                        submit_btn.click()
                        time.sleep(random.uniform(3, 5))
                        
                        replies_made += 1
                        logger.info(f"✅ Replied to comment ({replies_made}/{max_replies})")
                        
                        if replies_made >= max_replies:
                            break
                        
                        # Wait between replies
                        time.sleep(random.uniform(60, 180))
                
                except Exception as e:
                    logger.debug(f"Error processing post {post_url}: {e}")
                    continue
            
            logger.info(f"Made {replies_made} replies")
            
        except Exception as e:
            logger.error(f"Error replying to comments: {e}")
    
    def generate_reply(self) -> str:
        """Generate a friendly reply"""
        replies = [
            "Thanks for sharing! This is exactly what this community is for.",
            "Great insight! Have you noticed any other patterns?",
            "Love this! Keep us posted on your progress.",
            "Thanks for being part of the community! 🎯",
            "This resonates with a lot of people here. Appreciate you sharing.",
            "Have you tried [related feature/session]? Might help with this.",
            "Solid advice! Thanks for contributing to the discussion.",
        ]
        return random.choice(replies)
    
    def run_daily_routine(self) -> None:
        """Run the daily community management routine"""
        logger.info("🚀 Starting daily community routine")
        
        # Check state to prevent duplicate posts
        state = self.load_state()
        today = datetime.now().strftime('%Y-%m-%d')
        
        if state.get('last_run') == today and not self.dry_run:
            logger.info("Already ran today, skipping to avoid duplicates")
            return
        
        # Check what day it is
        today_name = datetime.now().strftime('%A').lower()
        
        # Setup browser with try-finally for cleanup
        try:
            self.driver = self.setup_browser()
            
            # Login
            username = os.getenv('REDDIT_USERNAME')
            password = os.getenv('REDDIT_PASSWORD')
            
            if not self.login(username, password):
                logger.error("Login failed")
                return
        
            posts_made = 0
            
            # Check for weekly thread
            for weekly in self.WEEKLY_THREADS:
                if weekly['day'] == today_name and datetime.now().hour < 12:
                    # Post weekly thread
                    post = CommunityPost(
                      title=weekly['title'],
                        content=weekly['content'],
                        post_type='weekly',
                        flair=weekly['flair'],
                        pin=weekly['pin']
                    )
                    
                    success, error = self.create_post(post)
                    if success:
                        posts_made += 1
                        logger.info(f"Posted weekly thread: {weekly['title']}")
                    else:
                        logger.error(f"Failed to post weekly thread: {error}")
                    
                    time.sleep(random.uniform(self.POST_WAIT_MIN, self.POST_WAIT_MAX))  # 5-10 min break
            
            # Post daily content (only if no weekly thread posted, or if it's afternoon)
            if posts_made == 0 or datetime.now().hour >= 14:
                daily_post = self.generate_daily_post()
                success, error = self.create_post(daily_post)
                if success:
                    posts_made += 1
                    logger.info("Posted daily content")
                else:
                    logger.error(f"Failed to post daily content: {error}")
            
            # Reply to comments
            self.reply_to_comments(max_replies=3)
            
            # Update state
            state['last_run'] = today
            state['posts_made'] = posts_made
            state['weekly_threads'] = state.get('weekly_threads', {})
            
            # Track weekly threads
            for weekly in self.WEEKLY_THREADS:
                if weekly['day'] == today_name and posts_made > 0:
                    state['weekly_threads'][weekly['day']] = datetime.now().isoformat()
            
            self.save_state(state)
            
            # Cleanup
            logger.info(f"✅ Daily routine complete. Made {posts_made} posts.")
        
        finally:
            if self.driver:
                self.driver.quit()
    
    def generate_daily_post(self) -> CommunityPost:
        """Generate a daily post"""
        template = random.choice(self.DAILY_CONTENT_TEMPLATES)
        
        if template['type'] == 'tip':
            tip = random.choice(self.TIPS)
            title = template['title'].format(tip_title=tip['title'])
            content = template['content'].format(tip_content=tip['content'])
        
        elif template['type'] == 'success_story':
            # You'd want to pull real success stories from your DB
            title = template['title'].format(story_title="From Insomnia to Restful Sleep")
            content = template['content'].format(
                story_content="One of our users shared: 'I hadn't slept through the night in 3 years. After 2 weeks of nightly sleep hypnosis sessions, I'm sleeping 7 hours straight. It's changed my life.'"
            )
        
        elif template['type'] == 'question':
            questions = [
                ("What's your biggest challenge with hypnosis?", "We all hit roadblocks. What's been your biggest challenge with hypnosis or manifestation?"),
                ("How did you discover hypnosis?", "Everyone has an origin story. How did you first get into hypnosis?"),
                ("What's your favorite hypnosis category?", "Sleep? Confidence? Manifestation? What's your go-to?"),
                ("What time of day do you prefer hypnosis?", "Morning routine or evening wind-down? When do you find hypnosis most effective?"),
                ("Share your 'aha' moment", "When did hypnosis finally click for you? What made it all make sense?"),
                ("What's one myth about hypnosis you believed?", "Let's bust some myths together. What misconception did you have?"),
                ("How do you track your progress?", "Journals? Apps? Dreams? How do you know hypnosis is working for you?"),
                ("What's your pre-hypnosis ritual?", "Do you have a routine before sessions? Share your setup!"),
                ("Hypnosis fails - let's talk about them", "Not every session works. What hasn't worked for you and why?"),
                ("Partner reactions to hypnosis?", "How did your friends/family react when you started hypnosis?"),
            ]
            q, context = random.choice(questions)
            title = template['title'].format(question=q)
            content = template['content'].format(context=context)
        
        else:  # feature highlight
            features = [
                ('AI-Powered Personalization', 'Every session is customized to your specific needs using advanced AI. No generic scripts.'),
                ('Voice Selection', 'Choose from dozens of voices across multiple languages. Find the voice that resonates with you.'),
                ('Progress Tracking', 'Track your hypnosis journey with detailed stats and insights.'),
            ]
            feature_name, feature_desc = random.choice(features)
            title = template['title'].format(feature_name=feature_name)
            content = template['content'].format(
                feature_name=feature_name,
                feature_description=feature_desc
            )
        
        return CommunityPost(
            title=title,
            content=content,
            post_type=template['type'],
            flair=template['flair'],
            pin=False
        )


def main():
    """Main entry"""
    parser = argparse.ArgumentParser(description='Hypnothera Subreddit Community Manager')
    parser.add_argument('--dry-run', action='store_true', help='Run in dry-run mode without making actual posts')
    args = parser.parse_args()
    
    # Check env vars
    required = ['REDDIT_USERNAME', 'REDDIT_PASSWORD']
    missing = [v for v in required if not os.getenv(v)]
    
    if missing:
        logger.error(f"Missing environment variables: {missing}")
        return
    
    if args.dry_run:
        logger.info("Running in DRY RUN mode - no posts will be made")
    
    manager = HypnotheraCommunityManager(dry_run=args.dry_run)
    manager.run_daily_routine()


if __name__ == "__main__":
    main()
