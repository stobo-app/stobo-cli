"""Sample response data for CLI tests."""

SAMPLE_AUDIT = {
    "id": "aaaa-bbbb-cccc",
    "url": "https://example.com/blog/test",
    "domain": "example.com",
    "article_title": "Test Article",
    "status": "completed",
    "overall_score": 240,
    "max_points": 335,
    "percentage": 71.6,
    "grade": "C",
    "seo_audit": {"category_scores": {"content": 80, "links": 60, "technical": 55}},
    "aeo_audit": {},
    "recommendations": ["Add meta description", "Improve heading hierarchy"],
    "created_at": "2026-02-08T12:00:00Z",
    "completed_at": "2026-02-08T12:00:30Z",
}

SAMPLE_TONE = {
    "customer_id": "example-com",
    "profile": {
        "brand_personality": {"archetype": "The Sage", "voice_summary": "Professional yet approachable"},
        "writing_style": {"formality": "semi-formal", "sentence_length": "medium"},
        "tone_descriptors": ["professional", "conversational", "data-driven"],
    },
    "articles_analyzed": 8,
    "message": "Brand voice extracted.",
}

SAMPLE_JOB = {
    "job_id": "dddd-eeee-ffff",
    "url": "https://example.com/blog/test",
    "status": "completed",
    "rewrite_result": {
        "tone_alignment_score": 0.92,
        "issues_addressed": ["meta_description", "h1"],
        "issues_skipped": [],
    },
    "started_at": "2026-02-08T12:00:00Z",
    "completed_at": "2026-02-08T12:02:00Z",
}

SAMPLE_SITE_AUDIT = {
    "url": "https://phantombuster.com",
    "domain": "phantombuster.com",
    "cached": False,
    "seo_audit": {
        "id": "site-aaaa-bbbb",
        "grade": "B",
        "overall_score": 78,
        "total_points": 260,
        "max_points": 335,
        "checks": {
            "title": {"status": "excellent", "score": 15, "max_points": 15, "message": "Good title length", "details": {}},
            "meta_description": {"status": "good", "score": 12, "max_points": 15, "message": "Meta description present", "details": {}},
        },
        "category_scores": {
            "Content": {"score": 80, "max_points": 95, "percentage": 84},
            "Links": {"score": 55, "max_points": 70, "percentage": 79},
            "Technical": {"score": 60, "max_points": 70, "percentage": 86},
            "Performance": {"score": 30, "max_points": 45, "percentage": 67},
            "Security": {"score": 10, "max_points": 10, "percentage": 100},
            "Social": {"score": 15, "max_points": 15, "percentage": 100},
            "Accessibility": {"score": 10, "max_points": 30, "percentage": 33},
        },
        "recommendations": [
            {"check": "accessibility", "priority": "high", "message": "Add ARIA labels to interactive elements"},
            {"check": "image_alt", "priority": "high", "message": "12 images missing alt text"},
            {"check": "core_web_vitals", "priority": "medium", "message": "LCP above 2.5s threshold"},
        ],
    },
    "seo_error": None,
    "aeo_audit": {
        "robots_ai": {"status": "excellent", "score": 25, "max_points": 25, "message": "AI crawlers allowed", "details": {}},
        "llms_txt": {"status": "critical", "score": 0, "max_points": 25, "message": "No llms.txt file found", "details": {}},
        "freshness": {"status": "good", "score": 20, "max_points": 25, "message": "Content updated within 90 days", "details": {}},
        "faqs": {"status": "excellent", "score": 10, "max_points": 10, "message": "FAQ section found", "details": {}},
        "faq_schema": {"status": "needs_improvement", "score": 5, "max_points": 15, "message": "FAQ schema incomplete", "details": {}},
        "direct_answer": {"status": "good", "score": 20, "max_points": 25, "message": "Opening paragraph answers query", "details": {}},
        "sitemap": {"status": "excellent", "score": 10, "max_points": 10, "message": "Sitemap found and valid", "details": {}},
        "score": 90,
        "max_points": 135,
        "percentage": 66.7,
    },
    "aeo_error": None,
    "blog_detection": {
        "has_blog": True,
        "blog_url": "https://phantombuster.com/blog",
        "blog_path": "/blog",
        "sitemap_url": "https://phantombuster.com/sitemap.xml",
        "article_count": 47,
    },
    "sitemap_discovery": {
        "total_urls": 324,
        "categories": [
            {"slug": "blog", "name": "Blog Articles", "urls": ["https://phantombuster.com/blog/a", "https://phantombuster.com/blog/b"]},
            {"slug": "product", "name": "Product Pages", "urls": ["https://phantombuster.com/pricing"]},
        ],
        "blog_article_count": 47,
        "other_urls": [],
    },
    "combined_percentage": 72.4,
}

SAMPLE_ME = {"email": "user@example.com", "full_name": "Test User"}

SAMPLE_CREDITS = {
    "used": 500,
    "total": 10000,
    "remaining": 9500,
    "plan": "starter",
    "reset_date": "2026-03-01",
    "breakdown": [{"action": "tone_extraction", "credits": 500, "count": 1}],
}

SAMPLE_LLMS_TXT = {
    "domain": "phantombuster.com",
    "title": "PhantomBuster",
    "content": "# PhantomBuster\n> Cloud-based automation platform.\n\n## Docs\n- API Reference\n",
    "word_count": 245,
    "sections": 4,
}

SAMPLE_ROBOTS_TXT = {
    "domain": "scorejam.ai",
    "content": "User-agent: GPTBot\nAllow: /\n\nUser-agent: ClaudeBot\nAllow: /\n",
    "crawlers_added": ["GPTBot", "ClaudeBot"],
    "crawlers_kept": [],
    "crawlers_with_custom_rules": [],
    "had_existing": False,
    "existing_score": 0,
    "new_score": 25,
    "sitemaps_added": [],
}
