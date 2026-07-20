"""
BeautifulSoup-based HTML parser implementation.

This module provides a DOM-based parser using BeautifulSoup4 for
comprehensive HTML element extraction and analysis.
"""

import re
from typing import Optional, Dict, Any, List, Set
from urllib.parse import urlparse, urljoin

try:
    from bs4 import BeautifulSoup, Tag, Comment
    from bs4.element import ResultSet
except ImportError:
    BeautifulSoup = None  # type: ignore
    Tag = None  # type: ignore
    Comment = None  # type: ignore
    ResultSet = None  # type: ignore

from backend.core.interfaces.parser import IParser
from backend.core.domain.parser import (
    ParserResult,
    MetaData,
    Heading,
    Link,
    Image,
    Script,
    Stylesheet,
    ParsingMetrics,
)
from backend.config.logging import get_logger

logger = get_logger(__name__)


class BeautifulSoupParser(IParser):
    """
    BeautifulSoup-based HTML parser implementation.

    Provides comprehensive DOM traversal and element extraction
    using BeautifulSoup4 library.
    """

    def __init__(self, encoding: str = "utf-8"):
        """
        Initialize BeautifulSoup parser.

        Args:
            encoding: Default encoding for content
        """
        self.encoding = encoding
        self._validate_dependencies()

    def _validate_dependencies(self):
        """Validate that BeautifulSoup is installed."""
        if BeautifulSoup is None:
            raise ImportError(
                "BeautifulSoup4 is required for BeautifulSoupParser. "
                "Install with: poetry add beautifulsoup4"
            )

    @property
    def parser_name(self) -> str:
        """Get the name of this parser implementation."""
        return "beautifulsoup"

    async def parse(
        self, html_content: str, url: str, options: Optional[Dict[str, Any]] = None
    ) -> ParserResult:
        """
        Parse HTML content and extract structured data.

        Args:
            html_content: Raw HTML content to parse
            url: Source URL of the content
            options: Optional parsing options

        Returns:
            ParserResult: Structured parsing result
        """
        if not html_content:
            return ParserResult(
                url=url,
                html_content=html_content,
                success=False,
                error="Empty HTML content provided",
            )

        try:
            # Parse HTML
            soup = BeautifulSoup(html_content, "html.parser")

            # Create result object
            result = ParserResult(url=url, html_content=html_content)

            # Extract content
            result.title = self.extract_title(html_content)
            result.text_content = self.extract_text_content(html_content)
            result.language = self.detect_language(html_content)

            # Extract structured data
            result.metadata = self._extract_metadata(soup, html_content)
            result.headings = self._extract_headings(soup)
            result.links = self._extract_links(soup, url)
            result.images = self._extract_images(soup, url)
            result.scripts = self._extract_scripts(soup)
            result.stylesheets = self._extract_stylesheets(soup, url)

            # Create metrics
            result.metrics = ParsingMetrics(
                start_time=options.get("start_time", "") if options else "",
                end_time=options.get("end_time", "") if options else "",
                duration_ms=options.get("duration_ms", 0) if options else 0,
                bytes_processed=len(html_content.encode(self.encoding)),
                elements_extracted=(
                    len(result.headings)
                    + len(result.links)
                    + len(result.images)
                    + len(result.scripts)
                    + len(result.stylesheets)
                ),
                parser_type=self.parser_name,
            )

            # Validate result
            warnings = result.validate()
            if warnings:
                result.additional_data["validation_warnings"] = warnings

            logger.info(
                f"Successfully parsed URL {url}",
                title=result.title,
                elements_extracted=result.metrics.elements_extracted,
            )

            return result

        except Exception as e:
            logger.error(f"Failed to parse HTML from {url}", error=str(e))
            return ParserResult(
                url=url, html_content=html_content, success=False, error=f"Parsing failed: {str(e)}"
            )

    def can_parse(self, html_content: str) -> bool:
        """
        Check if this parser can handle the given HTML content.

        Args:
            html_content: HTML content to check

        Returns:
            bool: True if parser can handle this content
        """
        if not html_content:
            return False

        # Check if content looks like HTML
        html_indicators = [
            "<!DOCTYPE html",
            "<html",
            "<head>",
            "<body",
            "<div",
            "<p>",
        ]

        return any(indicator.lower() in html_content.lower() for indicator in html_indicators)

    def extract_title(self, html_content: str) -> Optional[str]:
        """
        Extract page title from HTML content.

        Args:
            html_content: HTML content to extract title from

        Returns:
            Optional[str]: Page title or None if not found
        """
        try:
            soup = BeautifulSoup(html_content, "html.parser")
            title_tag = soup.find("title")

            if title_tag:
                return self.clean_text(title_tag.get_text())

            return None
        except Exception as e:
            logger.error(f"Failed to extract title", error=str(e))
            return None

    def extract_text_content(self, html_content: str) -> str:
        """
        Extract clean text content from HTML.

        Args:
            html_content: HTML content to extract text from

        Returns:
            str: Clean text content
        """
        try:
            soup = BeautifulSoup(html_content, "html.parser")

            # Get text
            text = soup.get_text(separator=" ")

            # Clean up whitespace
            text = self.clean_text(text)

            return text

        except Exception as e:
            logger.error(f"Failed to extract text content", error=str(e))
            return ""

    def detect_language(self, html_content: str) -> Optional[str]:
        """
        Detect the language of the content.

        Args:
            html_content: HTML content to analyze

        Returns:
            Optional[str]: Language code (e.g., 'en', 'es', 'fr')
        """
        try:
            soup = BeautifulSoup(html_content, "html.parser")

            # Check html lang attribute
            html_tag = soup.find("html")
            if html_tag and html_tag.get("lang"):
                return html_tag.get("lang").split("-")[0]

            # Check for lang attribute in body
            body_tag = soup.find("body")
            if body_tag and body_tag.get("lang"):
                return body_tag.get("lang").split("-")[0]

            return None

        except Exception as e:
            logger.error(f"Failed to detect language", error=str(e))
            return None

    def extract_metadata(self, soup: BeautifulSoup, html_content: str) -> MetaData:
        """
        Extract HTML metadata (title, description, etc.).

        Args:
            soup: BeautifulSoup object
            html_content: Original HTML content

        Returns:
            MetaData: Extracted metadata
        """
        metadata = MetaData()

        try:
            # Title
            title_tag = soup.find("title")
            if title_tag:
                metadata.title = self.clean_text(title_tag.get_text())

            # Meta tags
            for meta_tag in soup.find_all("meta"):
                name = meta_tag.get("name", "").lower()
                property_attr = meta_tag.get("property", "").lower()
                http_equiv = meta_tag.get("http-equiv", "").lower()
                content = meta_tag.get("content", "")

                if not content:
                    continue

                # Standard meta tags
                if name == "description":
                    metadata.description = content
                elif name == "keywords":
                    metadata.keywords = content
                elif name == "author":
                    metadata.author = content
                elif name == "robots":
                    metadata.robots = content
                elif name == "charset":
                    metadata.charset = content
                elif name == "viewport":
                    metadata.viewport = content

                # Open Graph tags
                elif property_attr == "og:title":
                    metadata.og_title = content
                elif property_attr == "og:description":
                    metadata.og_description = content
                elif property_attr == "og:image":
                    metadata.og_image = content

                # Twitter card tags
                elif name == "twitter:card":
                    metadata.twitter_card = content

                # Custom meta tags
                else:
                    key = property_attr or name
                    if key and key not in metadata.custom:
                        metadata.custom[key] = content

            # Canonical URL
            canonical_tag = soup.find("link", rel="canonical")
            if canonical_tag:
                metadata.canonical_url = canonical_tag.get("href")

            # Language
            html_tag = soup.find("html")
            if html_tag and html_tag.get("lang"):
                metadata.language = html_tag.get("lang").split("-")[0]

            logger.debug("Metadata extracted successfully")

        except Exception as e:
            logger.error(f"Failed to extract metadata", error=str(e))

        return metadata

    def _extract_headings(self, soup: BeautifulSoup) -> List[Heading]:
        """
        Extract heading elements from HTML.

        Args:
            soup: BeautifulSoup object

        Returns:
            List[Heading]: Extracted headings
        """
        headings = []

        try:
            for level in range(1, 7):
                heading_tags = soup.find_all(f"h{level}")

                for tag in heading_tags:
                    heading = Heading(
                        level=level,
                        text=self.clean_text(tag.get_text()),
                        html_content=str(tag),
                        attributes=self._extract_attributes(tag),
                    )
                    headings.append(heading)

            logger.debug(f"Extracted {len(headings)} headings")

        except Exception as e:
            logger.error(f"Failed to extract headings", error=str(e))

        return headings

    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[Link]:
        """
        Extract link elements from HTML.

        Args:
            soup: BeautifulSoup object
            base_url: Base URL for resolving relative URLs

        Returns:
            List[Link]: Extracted links
        """
        links = []

        try:
            link_tags = soup.find_all("a", href=True)

            for tag in link_tags:
                href = tag.get("href", "")
                text = self.clean_text(tag.get_text())
                title = tag.get("title")
                rel = tag.get("rel")

                # Normalize URL
                normalized_url = self.normalize_url(href, base_url)

                # Determine if internal
                is_internal = self.is_internal_url(normalized_url, base_url)

                # Check if nofollow
                is_nofollow = False
                if rel:
                    if isinstance(rel, list):
                        is_nofollow = "nofollow" in rel
                    else:
                        is_nofollow = "nofollow" in str(rel).lower().split()

                link = Link(
                    url=normalized_url,
                    text=text,
                    title=title,
                    rel=rel,
                    is_internal=is_internal,
                    is_nofollow=is_nofollow,
                    html_content=str(tag),
                    attributes=self._extract_attributes(tag),
                )
                links.append(link)

            logger.debug(f"Extracted {len(links)} links")

        except Exception as e:
            logger.error(f"Failed to extract links", error=str(e))

        return links

    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> List[Image]:
        """
        Extract image elements from HTML.

        Args:
            soup: BeautifulSoup object
            base_url: Base URL for resolving relative URLs

        Returns:
            List[Image]: Extracted images
        """
        images = []

        try:
            img_tags = soup.find_all("img", src=True)

            for tag in img_tags:
                src = tag.get("src", "")
                alt = tag.get("alt")
                title = tag.get("title")
                width = tag.get("width")
                height = tag.get("height")

                # Normalize URL
                normalized_url = self.normalize_url(src, base_url)

                # Determine if internal
                is_internal = self.is_internal_url(normalized_url, base_url)

                # Parse dimensions
                parsed_width = None
                parsed_height = None
                if width:
                    try:
                        parsed_width = int(str(width))
                    except ValueError:
                        pass
                if height:
                    try:
                        parsed_height = int(str(height))
                    except ValueError:
                        pass

                image = Image(
                    src=normalized_url,
                    alt=alt,
                    title=title,
                    width=parsed_width,
                    height=parsed_height,
                    is_internal=is_internal,
                    html_content=str(tag),
                    attributes=self._extract_attributes(tag),
                )
                images.append(image)

            logger.debug(f"Extracted {len(images)} images")

        except Exception as e:
            logger.error(f"Failed to extract images", error=str(e))

        return images

    def _extract_scripts(self, soup: BeautifulSoup) -> List[Script]:
        """
        Extract script elements from HTML.

        Args:
            soup: BeautifulSoup object

        Returns:
            List[Script]: Extracted scripts
        """
        scripts = []

        try:
            script_tags = soup.find_all("script")

            for tag in script_tags:
                src = tag.get("src")
                content = tag.string
                script_type = tag.get("type")
                async_flag = tag.get("async") is not None
                defer = tag.get("defer") is not None

                script = Script(
                    src=src,
                    content=content,
                    type=script_type,
                    async_flag=async_flag,
                    defer=defer,
                    html_content=str(tag),
                )
                scripts.append(script)

            logger.debug(f"Extracted {len(scripts)} scripts")

        except Exception as e:
            logger.error(f"Failed to extract scripts", error=str(e))

        return scripts

    def _extract_stylesheets(self, soup: BeautifulSoup, base_url: str) -> List[Stylesheet]:
        """
        Extract stylesheet elements from HTML.

        Args:
            soup: BeautifulSoup object
            base_url: Base URL for resolving relative URLs

        Returns:
            List[Stylesheet]: Extracted stylesheets
        """
        stylesheets = []

        try:
            link_tags = soup.find_all("link", rel="stylesheet")

            for tag in link_tags:
                href = tag.get("href")
                media = tag.get("media", "all")

                if href:
                    # Normalize URL
                    normalized_url = self.normalize_url(href, base_url)

                    # Determine if internal
                    is_internal = self.is_internal_url(normalized_url, base_url)

                    stylesheet = Stylesheet(
                        href=normalized_url,
                        media=media,
                        is_internal=is_internal,
                        html_content=str(tag),
                    )
                    stylesheets.append(stylesheet)

            # Check for inline styles
            style_tags = soup.find_all("style")
            for tag in style_tags:
                if tag.string:
                    stylesheet = Stylesheet(content=tag.string.strip(), html_content=str(tag))
                    stylesheets.append(stylesheet)

            logger.debug(f"Extracted {len(stylesheets)} stylesheets")

        except Exception as e:
            logger.error(f"Failed to extract stylesheets", error=str(e))

        return stylesheets

    def _extract_attributes(self, tag: Tag) -> Dict[str, str]:
        """
        Extract all attributes from a tag.

        Args:
            tag: BeautifulSoup tag

        Returns:
            Dict[str, str]: Dictionary of attributes
        """
        attributes = {}
        if tag and tag.attrs:
            attributes = {k: str(v) for k, v in tag.attrs.items()}
        return attributes


# Export for easy import
__all__ = [
    "BeautifulSoupParser",
]
