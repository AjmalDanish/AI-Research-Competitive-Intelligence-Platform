"""
Integration tests for parser functionality.

These tests validate end-to-end parsing workflows with realistic HTML content.
"""

import pytest
from typing import List

from backend.parser import ParserService, BeautifulSoupParser, TrafilaturaParser
from backend.core.domain.parser import (
    ParserResult,
    ContentType,
    MetaData,
    Heading,
    Link,
    Image,
    Script,
    Stylesheet,
)


class TestEndToEndParsing:
    """Test end-to-end parsing workflows."""
    
    @pytest.mark.asyncio
    async def test_complete_article_parsing(self):
        """Test parsing a complete article with all elements."""
        service = ParserService()
        
        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>AI in Modern Web Development</title>
            <meta name="description" content="Exploring AI applications in web development">
            <meta name="keywords" content="AI, web development, artificial intelligence">
            <meta name="author" content="John Doe">
            <link rel="canonical" href="https://example.com/ai-modern-web-development">
            <meta property="og:title" content="AI in Modern Web Development">
            <meta property="og:description" content="Exploring AI applications">
            <meta property="og:image" content="https://example.com/images/ai-web.jpg">
        </head>
        <body>
            <header>
                <nav>
                    <a href="/">Home</a>
                    <a href="/about">About</a>
                    <a href="https://external.com">External</a>
                    <a href="/contact" rel="nofollow">Contact</a>
                </nav>
            </header>
            
            <main>
                <h1>AI in Modern Web Development</h1>
                <p>This article explores AI applications in modern web development.</p>
                
                <h2>Introduction</h2>
                <p>AI is transforming how we build web applications.</p>
                
                <h3>Key Benefits</h3>
                <p>AI helps with automation, personalization, and intelligent decision-making.</p>
                
                <h2>Implementation</h2>
                <p>Here's how to integrate AI into your web projects:</p>
                
                <h3>Step 1: Setup</h3>
                <p>Prepare your environment with necessary tools.</p>
                
                <h3>Step 2: Development</h3>
                <p>Implement AI features with clean architecture.</p>
                
                <blockquote>
                    <p>AI is not just hype, it's a practical tool for modern developers.</p>
                </blockquote>
                
                <p>For more information, visit the <a href="/documentation">documentation</a>.</p>
            </main>
            
            <footer>
                <a href="/privacy">Privacy</a>
                <a href="/terms">Terms</a>
                <a href="https://social.com/share" rel="nofollow">Share</a>
            </footer>
            
            <script src="/main.js" type="text/javascript"></script>
            <script>
                // Inline script
                console.log('Page loaded');
            </script>
            <link rel="stylesheet" href="/styles/main.css" media="screen">
            <link rel="stylesheet" href="https://cdn.example.com/external.css" media="print">
            <style>
                body { font-family: sans-serif; }
            </style>
        </body>
        </html>
        """
        
        result = await service.parse(html, "https://example.com/ai-modern-web-development")
        
        # Verify successful parsing
        assert result.success is True
        assert result.error is None
        
        # Verify basic extraction
        assert result.title == "AI in Modern Web Development"
        assert result.text_content is not None
        assert len(result.text_content) > 0
        
        # Verify metadata
        assert result.metadata.title == "AI in Modern Web Development"
        assert result.metadata.description == "Exploring AI applications in modern web development"
        assert result.metadata.keywords == "AI, web development, artificial intelligence"
        assert result.metadata.author == "John Doe"
        assert result.metadata.canonical_url == "https://example.com/ai-modern-web-development"
        assert result.metadata.og_title == "AI in Modern Web Development"
        assert result.metadata.og_description == "Exploring AI applications"
        assert result.metadata.og_image == "https://example.com/images/ai-web.jpg"
        
        # Verify headings
        assert len(result.headings) == 6  # h1, h2 x2, h3 x3
        main_heading = result.get_main_heading()
        assert main_heading is not None
        assert main_heading.text == "AI in Modern Web Development"
        
        # Verify links
        assert len(result.links) == 7
        internal_links = result.get_internal_links()
        external_links = result.get_external_links()
        nofollow_links = result.get_nofollow_links()
        
        assert len(internal_links) == 5  # Home, About, Contact, Documentation, Privacy, Terms
        assert len(external_links) == 2  # External and Share
        assert len(nofollow_links) == 2  # Contact and Share
        
        # Verify scripts
        assert len(result.scripts) == 2  # One external, one inline
        
        # Verify stylesheets
        assert len(result.stylesheets) == 3  # Two external, one inline
        internal_stylesheets = [s for s in result.stylesheets if s.is_internal]
        external_stylesheets = [s for s in result.stylesheets if not s.is_internal]
        inline_stylesheets = [s for s in result.stylesheets if s.content is not None]
        
        assert len(internal_stylesheets) == 1
        assert len(external_stylesheets) == 2
        assert len(inline_stylesheets) == 1
        
        # Verify metrics
        assert result.metrics is not None
        assert result.metrics.parser_type == "beautifulsoup"
        assert result.metrics.bytes_processed > 0
        assert result.metrics.elements_extracted > 0
    
    @pytest.mark.asyncio
    async def test_news_article_parsing(self):
        """Test parsing a news article."""
        service = ParserService()
        
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>BREAKING: Major Tech Announcement</title>
            <meta name="description" content="Industry leaders announce new partnership">
            <meta name="robots" content="index,follow">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <meta name="language" content="en">
            <link rel="canonical" href="https://news.example.com/breaking-announcement">
        </head>
        <body>
            <article>
                <header>
                    <h1>BREAKING: Major Tech Announcement</h1>
                    <p class="author">By <a href="/authors/jane-smith">Jane Smith</a></p>
                    <p class="date">Published: January 20, 2025</p>
                </header>
                
                <h2>Overview</h2>
                <p>Major tech companies announced a strategic partnership today.</p>
                
                <figure>
                    <img src="/images/announcement.jpg" alt="Press conference" width="1200" height="800">
                    <figcaption>Press conference announcement</figcaption>
                </figure>
                
                <h2>Key Points</h2>
                <ul>
                    <li>Joint R&D investment of $10B</li>
                    <li>Collaboration on AI safety standards</li>
                    <li>Commitment to open source initiatives</li>
                </ul>
                
                <h2>Industry Impact</h2>
                <p>This partnership will affect:</p>
                <ol>
                    <li>AI development tools</li>
                    <li>Enterprise solutions</li>
                    <li>Consumer applications</li>
                </ol>
                
                <p><a href="/related/ai-partnerships">Related: Other AI partnerships</a></p>
                <p><a href="https://technews.com">Source: TechNews</a></p>
            </article>
        </body>
        </html>
        """
        
        result = await service.parse(html, "https://news.example.com/breaking-announcement")
        
        # Verify parsing
        assert result.success is True
        assert result.title == "BREAKING: Major Tech Announcement"
        
        # Verify metadata
        assert result.metadata.description == "Industry leaders announce new partnership"
        assert result.metadata.robots == "index,follow"
        assert result.metadata.viewport == "width=device-width, initial-scale=1"
        assert result.metadata.language == "en"
        
        # Verify content structure
        assert "Major tech companies announced a strategic partnership today" in result.text_content
        
        # Verify images with dimensions
        announcement_img = next((img for img in result.images if "announcement.jpg" in img.src), None)
        assert announcement_img is not None
        assert announcement_img.width == 1200
        assert announcement_img.height == 800
        assert announcement_img.alt == "Press conference"
        
        # Verify link analysis
        author_links = [l for l in result.links if "jane-smith" in l.url]
        related_links = [l for l in result.links if "ai-partners" in l.url]
        
        assert len(author_links) == 1
        assert len(related_links) == 1
    
    @pytest.mark.asyncio
    async def test_e_commerce_parsing(self):
        """Test parsing an e-commerce product page."""
        service = ParserService()
        
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Product: Premium Wireless Headphones</title>
            <meta name="description" content="High-quality wireless headphones with noise cancellation">
        </head>
        <body>
            <nav class="breadcrumb">
                <a href="/">Home</a>
                <a href="/audio">Audio</a>
                <a href="/audio/headphones">Headphones</a>
                <span>Premium Wireless Headphones</span>
            </nav>
            
            <main>
                <h1>Premium Wireless Headphones</h1>
                
                <div class="product-images">
                    <img src="/images/main-product.jpg" alt="Main product view" class="primary">
                    <img src="/images/side-view.jpg" alt="Side view" class="secondary">
                    <img src="https://cdn.example.com/branding/watermark.png" alt="Brand watermark" class="watermark">
                </div>
                
                <div class="product-info">
                    <p class="price">$299.99</p>
                    <p class="availability">In Stock</p>
                    <p class="rating">Rating: 4.5/5 (2,847 reviews)</p>
                </div>
                
                <section class="features">
                    <h2>Features</h2>
                    <ul>
                        <li>Active Noise Cancellation</li>
                        <li>40-hour battery life</li>
                        <li>Bluetooth 5.0</li>
                        <li>Hi-Res Audio</li>
                    </ul>
                </section>
                
                <section class="reviews">
                    <h2>Customer Reviews</h2>
                    <div class="review">
                        <h3>Great product!</h3>
                        <p>These headphones exceeded my expectations.</p>
                        <p class="reviewer">John D.</p>
                    </div>
                </section>
                
                <section class="specifications">
                    <h2>Technical Specifications</h2>
                    <table>
                        <tr><th>Driver Size</th><td>50mm</td></tr>
                        <tr><th>Frequency Response</th><td>20Hz - 20kHz</td></tr>
                        <tr><th>Battery</th><td>40 hours</td></tr>
                        <tr><th>Weight</th><td>250g</td></tr>
                    </table>
                </section>
            </main>
            
            <aside class="sidebar">
                <a href="/compare" class="btn">Compare</a>
                <a href="/add-to-cart" class="btn primary">Add to Cart</a>
                <a href="/reviews" class="btn">Read Reviews</a>
            </aside>
            
            <script src="/product-page.js" defer></script>
            <link rel="stylesheet" href="/product.css">
        </body>
        </html>
        """
        
        result = await service.parse(html, "https://example.com/products/wireless-headphones")
        
        # Verify parsing
        assert result.success is True
        assert result.title == "Product: Premium Wireless Headphones"
        
        # Verify breadcrumb navigation
        breadcrumb_links = [l for l in result.links if "breadcrumb" in l.html_content or any(level in l.html_content for level in ["Home", "Audio", "Headphones"])]
        assert len(breadcrumb_links) >= 3
        
        # Verify product images
        product_images = result.images
        assert len(product_images) >= 3
        
        # Check image classifications
        internal_images = result.get_internal_images()
        external_images = result.get_external_images()
        
        assert len(internal_images) >= 2  # Main and side views
        assert len(external_images) == 1  # Watermark
        
        # Verify structure extraction
        h2_headings = result.get_headings_by_level(2)
        assert len(h2_headings) == 3  # Features, Customer Reviews, Technical Specifications
        
        # Verify scripts and stylesheets
        assert len(result.scripts) == 1  # product-page.js
        assert result.scripts[0].defer is True
        assert len(result.stylesheets) == 1  # product.css
    
    @pytest.mark.asyncio
    async def test_blog_post_parsing(self):
        """Test parsing a blog post with rich content."""
        service = ParserService()
        
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Understanding Microservices Architecture</title>
        </head>
        <body>
            <article>
                <header>
                    <h1>Understanding Microservices Architecture</h1>
                    <p>A deep dive into modern software architecture.</p>
                </header>
                
                <p class="intro">Microservices architecture has become a standard for modern applications.</p>
                
                <h2>What are Microservices?</h2>
                <p>Microservices are small, independent services that work together.</p>
                
                <h3>Key Characteristics</h3>
                <ul>
                    <li>Single responsibility</li>
                    <li>Independent deployment</li>
                    <li>Technology agnostic</li>
                </ul>
                
                <h2>Benefits</h2>
                <p>Microservices offer several advantages over monolithic architectures.</p>
                
                <h3>Scalability</h3>
                <p>Individual services can scale independently based on demand.</p>
                
                <h3>Resilience</h3>
                <p>Failure in one service doesn't crash the entire application.</p>
                
                <h2>Challenges</h2>
                <p>However, microservices come with their own set of challenges.</p>
                
                <h3>Complexity</h3>
                <p>Managing distributed systems is more complex than monolithic applications.</p>
                
                <h3>Data Consistency</h3>
                <p>Ensuring data consistency across services requires careful design.</p>
                
                <h2>Conclusion</h2>
                <p>Microservices architecture offers significant benefits but requires careful planning and execution.</p>
                
                <p><em>Looking for more architecture insights? <a href="/blog">Read our blog</a>.</em></p>
            </article>
        </body>
        </html>
        """
        
        result = await service.parse(html, "https://example.com/blog/microservices")
        
        # Verify parsing
        assert result.success is True
        assert result.title == "Understanding Microservices Architecture"
        
        # Verify heading structure
        assert result.get_main_heading() is not None
        assert result.get_main_heading().text == "Understanding Microservices Architecture"
        
        h2_headings = result.get_headings_by_level(2)
        h3_headings = result.get_headings_by_level(3)
        
        assert len(h2_headings) == 4  # What are, Benefits, Challenges, Conclusion
        assert len(h3_headings) == 6  # Key, Scalability, Resilience, Complexity, Data Consistency, Planning
        assert len(h3_headings) == 6
        
        # Verify content quality
        assert "Microservices architecture has become a standard" in result.text_content
        assert "independent deployment" in result.text_content
        assert "distributed systems" in result.text_content
        
        # Verify link extraction
        blog_link = next((l for l in result.links if "/blog" in l.url), None)
        assert blog_link is not None


class TestParserComparison:
    """Test comparing different parser implementations."""
    
    @pytest.mark.asyncio
    async def test_beautifulsoup_vs_trafilatura_comparison(self):
        """Test comparison between BeautifulSoup and Trafilatura parsers."""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test Article</title>
            <meta name="description" content="Test Description">
        </head>
        <body>
            <article>
                <h1>Main Article</h1>
                <p>This is test content for parser comparison.</p>
                <p>The article has multiple paragraphs and links.</p>
                <a href="/internal">Internal link</a>
                <a href="https://external.com">External link</a>
            </article>
        </body>
        </html>
        """
        
        service = ParserService()
        
        # Parse with BeautifulSoup
        bs_result = await service.parse(html, "https://example.com", "beautifulsoup")
        
        # Parse with Trafilatura
        tf_result = await service.parse(html, "https://example.com", "trafilatura")
        
        # Both should succeed
        assert bs_result.success is True
        assert tf_result.success is True
        
        # Both should extract title
        assert bs_result.title == "Test Article"
        assert tf_result.title == "Test Article"
        
        # BeautifulSoup should extract more structure
        assert len(bs_result.headings) > 0
        assert len(bs_result.links) > 0
        
        # Trafilatura focuses on text content
        assert tf_result.text_content is not None
        assert len(tf_result.text_content) > 0
    
    @pytest.mark.asyncio
    async def test_fallback_parsing_workflow(self):
        """Test fallback parsing workflow."""
        service = ParserService()
        
        # Valid HTML - first parser succeeds
        valid_html = "<html><head><title>Test</title></head><body>Content</body></html>"
        result = await service.parse_with_fallback(
            valid_html,
            "https://example.com",
            preferred_parser="beautifulsoup",
            fallback_parser="trafilatura"
        )
        
        assert result.success is True
        assert result.metrics.parser_type == "beautifulsoup"
        
        # Potentially problematic HTML - test fallback
        empty_html = ""
        result = await service.parse_with_fallback(
            empty_html,
            "https://example.com",
            preferred_parser="beautifulsoup",
            fallback_parser="trafilatura"
        )
        
        # Both parsers should fail for empty content
        assert result.success is False


class TestParserIntegrationService:
    """Test integration between parser service and implementations."""
    
    @pytest.mark.asyncio
    async def test_service_orchestration(self):
        """Test that service properly orchestrates parsers."""
        service = ParserService()
        
        # Test that service has access to both parsers
        assert "beautifulsoup" in service.parsers
        assert "trafilatura" in service.parsers
        
        # Test that service can instantiate parsers
        bs_parser = service.parsers["beautifulsoup"]
        tf_parser = service.parsers["trafilatura"]
        
        assert bs_parser.parser_name == "beautifulsoup"
        assert tf_parser.parser_name == "trafilatura"
    
    @pytest.mark.asyncio
    async def test_service_parser_selection(self):
        """Test that service selects appropriate parser."""
        service = ParserService()
        
        # Test with different content types
        simple_html = "<html><body>Content</body></html>"
        complex_html = "<html><head><title>Test</title></head><body><div>Content</div></html>"
        
        simple_result = await service.parse(simple_html, "https://example.com", "beautifulsoup")
        complex_result = await service.parse(complex_html, "https://example.com", "beautifulsoup")
        
        # Both should succeed
        assert simple_result.success is True
        assert complex_result.success is True


class TestRealWorldScenarios:
    """Test parsing with real-world scenarios."""
    
    @pytest.mark.asyncio
    async def test_parse_with_javascript_heavy_page(self):
        """Test parsing a page with extensive JavaScript."""
        service = ParserService()
        
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>JavaScript-Heavy Application</title>
            <script src="https://cdn.example.com/react.development.js" crossorigin></script>
            <script src="https://cdn.example.com/react-dom.production.min.js" crossorigin></script>
            <script src="https://cdn.example.com/babel.min.js"></script>
            <link rel="stylesheet" href="https://cdn.example.com/tailwind.css">
            <script type="text/babel" data-presets="env">const App = () => { return <div>React App</div>; };</script>
            <script defer src="/app.js"></script>
            <script async src="/analytics.js"></script>
        </head>
        <body>
            <div id="root"></div>
            <script>console.log("Fallback content");</script>
        </body>
        </html>
        """
        
        result = await service.parse(html, "https://example.com/react-app")
        
        # Should successfully parse despite heavy JavaScript
        assert result.success is True
        assert result.title == "JavaScript-Heavy Application"
        
        # Extract scripts (important for SPA applications)
        assert len(result.scripts) >= 4
        external_scripts = [s for s in result.scripts if s.src]
        inline_scripts = [s for s in result.scripts if s.content]
        
        assert len(external_scripts) >= 3  # React, Babel, Tailwind
        assert len(inline_scripts) >= 2  # React app and fallback
        
        # Check script attributes
        deferred_script = next((s for s in result.scripts if s.defer), None)
        async_script = next((s for s in result.scripts if s.async_flag), None)
        
        assert deferred_script is not None
        assert async_script is not None
    
    @pytest.mark.asyncio
    async def test_parse_with_seo_optimized_page(self):
        """Test parsing an SEO-optimized page."""
        service = ParserService()
        
        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <title>Ultimate Guide to SEO in 2025</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <meta name="description" content="Comprehensive SEO guide for 2025">
            <meta name="keywords" content="SEO, search engine optimization, digital marketing">
            <meta name="author" content="Sarah Johnson">
            <meta name="robots" content="index, follow, max-image-preview:large">
            <link rel="canonical" href="https://example.com/ultimate-seo-guide-2025">
            
            <!-- Open Graph -->
            <meta property="og:type" content="article">
            <meta property="og:title" content="Ultimate Guide to SEO in 2025">
            <meta property="og:description" content="Comprehensive SEO guide">
            <meta property="og:url" content="https://example.com/ultimate-seo-guide-2025">
            <meta property="og:image" content="https://example.com/images/seo-guide-2025.jpg">
            <meta property="og:image:width" content="1200">
            <meta property="og:image:height" content="630">
            <meta property="og:site_name" content="Tech Insights">
            
            <!-- Twitter Card -->
            <meta name="twitter:card" content="summary_large_image">
            <meta name="twitter:title" content="Ultimate Guide to SEO in 2025">
            <meta name="twitter:description" content="Comprehensive SEO guide">
            <meta name="twitter:image" content="https://example.com/images/seo-guide-2025.jpg">
            
            <!-- Schema.org structured data -->
            <script type="application/ld+json">
            {
                "@context": "https://schema.org",
                "@type": "Article",
                "headline": "Ultimate Guide to SEO in 2025",
                "author": {
                    "@type": "Person",
                    "name": "Sarah Johnson"
                },
                "datePublished": "2025-01-20"
            }
            </script>
            
            <link rel="stylesheet" href="/css/styles.css">
        </head>
        <body>
            <article>
                <h1>Ultimate Guide to SEO in 2025</h1>
                
                <p>This comprehensive guide covers everything you need to know about SEO.</p>
                
                <h2>SEO Fundamentals</h2>
                <p>Understanding the basics of search engine optimization.</p>
                
                <h3>On-Page SEO</h3>
                <p>Optimizing your website content and HTML structure.</p>
                
                <h3>Technical SEO</h3>
                <p>Improving site speed, mobile-friendliness, and crawlability.</p>
                
                <h2>Advanced Strategies</h2>
                <p>Advanced techniques for experienced SEO professionals.</p>
                
                <p><a href="/contact">Get in touch</a> for SEO consulting.</p>
            </article>
        </body>
        </html>
        """
        
        result = await service.parse(html, "https://example.com/ultimate-seo-guide-2025")
        
        # Verify parsing
        assert result.success is True
        assert result.title == "Ultimate Guide to SEO in 2025"
        
        # Verify comprehensive metadata extraction
        assert result.metadata.description == "Comprehensive SEO guide for 2025"
        assert result.metadata.keywords == "SEO, search engine optimization, digital marketing"
        assert result.metadata.author == "Sarah Johnson"
        assert result.metadata.robots == "index, follow, max-image-preview:large"
        assert result.metadata.canonical_url == "https://example.com/ultimate-seo-guide-2025"
        
        # Verify Open Graph tags
        assert result.metadata.og_title == "Ultimate Guide to SEO in 2025"
        assert result.metadata.og_description == "Comprehensive SEO guide"
        assert result.metadata.og_image == "https://example.com/images/seo-guide-2025.jpg"
        assert result.metadata.og_type == "article"
        
        # Verify Twitter Card tags
        assert result.metadata.twitter_card == "summary_large_image"
        assert result.metadata.twitter_title == "Ultimate Guide to SEO in 2025"
        
        # Verify heading structure for SEO
        main_h1 = result.get_main_heading()
        assert main_h1 is not None
        assert "Ultimate Guide to SEO in 2025" in main_h1.text
        
        h2s = result.get_headings_by_level(2)
        h3s = result.get_headings_by_level(3)
        
        assert len(h2s) == 3  # SEO Fundamentals, Advanced Strategies, plus content from HTML
        assert len(h3s) >= 2  # On-Page, Technical, plus others
    
    @pytest.mark.asyncio
    async def test_batch_real_world_parsing(self):
        """Test batch parsing multiple real-world HTML documents."""
        service = ParserService()
        
        pages = [
            (
                """<!DOCTYPE html><html><head><title>Home Page</title></head><body><h1>Welcome</h1></body></html>""",
                "https://example.com"
            ),
            (
                """<!DOCTYPE html><html><head><title>About Us</title></head><body><h1>About Our Company</h1></body></html>""",
                "https://example.com/about"
            ),
            (
                """<!DOCTYPE html><html><head><title>Contact</title></head><body><h1>Get in Touch</h1></body></html>""",
                "https://example.com/contact"
            ),
            (
                """<!DOCTYPE html><html><head><title>Blog</title></head><body><h1>Latest Articles</h1></body></html>""",
                "https://example.com/blog"
            ),
        ]
        
        results = await service.batch_parse(pages)
        
        # All pages should parse successfully
        assert len(results) == 5
        assert all(r.success for r in results)
        
        # Each result should have its correct title
        titles = [r.title for r in results]
        assert "Home Page" in titles
        assert "About Us" in titles
        assert "Contact" in titles
        assert "Blog" in titles
        
        # Each result should have at least one heading
        assert all(len(r.headings) >= 1 for r in results)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])