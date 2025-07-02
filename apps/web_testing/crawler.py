"""
Advanced Web Crawler for UI Testing

This module provides comprehensive web crawling capabilities with:
- Multi-strategy element extraction
- Smart pagination detection
- Dynamic content handling
- Performance monitoring
- Accessibility compliance checking
"""

import asyncio
import json
import hashlib
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, asdict
from enum import Enum
from urllib.parse import urljoin, urlparse
from playwright.async_api import Page, Browser, BrowserContext
import time
from datetime import datetime


class ElementType(Enum):
    """Enhanced element type classification"""

    BUTTON = "button"
    INPUT = "input"
    LINK = "link"
    FORM = "form"
    NAVIGATION = "navigation"
    TABLE = "table"
    LIST = "list"
    IMAGE = "image"
    MODAL = "modal"
    DROPDOWN = "dropdown"
    TAB = "tab"
    ACCORDION = "accordion"
    CARD = "card"
    PAGINATION = "pagination"
    SEARCH = "search"
    FILTER = "filter"
    CAROUSEL = "carousel"
    TOOLTIP = "tooltip"
    BREADCRUMB = "breadcrumb"
    SIDEBAR = "sidebar"
    HEADER = "header"
    FOOTER = "footer"


class LocatorStrategy(Enum):
    """Locator strategy priority"""

    DATA_TESTID = "data-testid"
    ID = "id"
    NAME = "name"
    ARIA_LABEL = "aria-label"
    CSS_CLASS = "css-class"
    CSS_SELECTOR = "css-selector"
    XPATH = "xpath"
    TEXT_CONTENT = "text-content"
    ROLE = "role"


@dataclass
class ElementLocator:
    """Element locator with strategy and reliability score"""

    strategy: LocatorStrategy
    value: str
    reliability_score: float  # 0.0 to 1.0
    is_unique: bool
    context: Optional[str] = None


@dataclass
class ElementData:
    """Comprehensive element data structure"""

    element_id: str  # Unique identifier
    element_type: ElementType
    tag_name: str
    text_content: str
    locators: List[ElementLocator]
    attributes: Dict[str, str]
    accessibility: Dict[str, Any]
    visual_properties: Dict[str, Any]
    behavioral_properties: Dict[str, Any]
    context: Dict[str, Any]
    interactions: List[str]  # Possible interactions
    test_scenarios: List[str]  # Suggested test scenarios
    page_url: str
    extraction_timestamp: str


@dataclass
class PageStructure:
    """Page structure analysis"""

    page_type: str
    has_navigation: bool
    has_forms: bool
    has_tables: bool
    has_modals: bool
    has_pagination: bool
    responsive_breakpoints: List[Dict[str, Any]]
    performance_metrics: Dict[str, Any]
    accessibility_score: float
    seo_elements: Dict[str, Any]


@dataclass
class CrawlResult:
    """Complete crawl result"""

    url: str
    title: str
    elements: List[ElementData]
    page_structure: PageStructure
    metadata: Dict[str, Any]
    linked_pages: List["CrawlResult"] = None
    crawl_duration: float = 0.0
    success: bool = True
    error_message: Optional[str] = None


class AdvancedWebCrawler:
    """Advanced web crawler with AI-powered element extraction"""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.visited_urls: Set[str] = set()
        self.crawl_stats = {"pages_crawled": 0, "elements_extracted": 0, "errors": 0}

    async def initialize(self, playwright):
        """Initialize browser and context"""
        browser_type = self.config.get("browser", "chromium")
        headless = self.config.get("headless", True)

        if browser_type == "chromium":
            self.browser = await playwright.chromium.launch(headless=headless)
        elif browser_type == "firefox":
            self.browser = await playwright.firefox.launch(headless=headless)
        elif browser_type == "webkit":
            self.browser = await playwright.webkit.launch(headless=headless)

        # Create context with enhanced settings
        self.context = await self.browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            java_script_enabled=True,
            accept_downloads=False,
            ignore_https_errors=True,
        )

    async def crawl_website(
        self, url: str, max_depth: int = 2, max_pages: int = 50
    ) -> CrawlResult:
        """Main crawling method with comprehensive analysis"""
        start_time = time.time()

        try:
            # Reset stats
            self.visited_urls.clear()
            self.crawl_stats = {
                "pages_crawled": 0,
                "elements_extracted": 0,
                "errors": 0,
            }

            # Crawl the main page
            result = await self._crawl_single_page(url, max_depth, max_pages)
            result.crawl_duration = time.time() - start_time

            return result

        except Exception as e:
            return CrawlResult(
                url=url,
                title="",
                elements=[],
                page_structure=PageStructure(
                    page_type="unknown",
                    has_navigation=False,
                    has_forms=False,
                    has_tables=False,
                    has_modals=False,
                    has_pagination=False,
                    responsive_breakpoints=[],
                    performance_metrics={},
                    accessibility_score=0.0,
                    seo_elements={},
                ),
                metadata=self.crawl_stats,
                crawl_duration=time.time() - start_time,
                success=False,
                error_message=str(e),
            )

    async def _crawl_single_page(
        self, url: str, max_depth: int, max_pages: int
    ) -> CrawlResult:
        """Crawl a single page with full analysis"""
        if url in self.visited_urls or len(self.visited_urls) >= max_pages:
            return None

        self.visited_urls.add(url)
        page = await self.context.new_page()

        try:
            # Navigate with performance monitoring
            start_nav = time.time()
            response = await page.goto(url, wait_until="networkidle", timeout=30000)
            nav_time = time.time() - start_nav

            # Wait for dynamic content
            await asyncio.sleep(1)
            await page.wait_for_load_state("domcontentloaded")

            # Extract page metadata
            title = await page.title()
            current_url = page.url

            # Extract all elements
            elements = await self._extract_all_elements(page)

            # Analyze page structure
            page_structure = await self._analyze_page_structure(page)

            # Get performance metrics
            performance_metrics = await self._get_performance_metrics(page, nav_time)
            page_structure.performance_metrics = performance_metrics

            # Calculate accessibility score
            page_structure.accessibility_score = (
                await self._calculate_accessibility_score(elements)
            )

            # Extract SEO elements
            page_structure.seo_elements = await self._extract_seo_elements(page)

            # Crawl linked pages if depth allows
            linked_pages = []
            if max_depth > 1:
                links = await self._extract_valid_links(page, url)
                for link_url in links[:10]:  # Limit links per page
                    linked_result = await self._crawl_single_page(
                        link_url, max_depth - 1, max_pages
                    )
                    if linked_result and linked_result.success:
                        linked_pages.append(linked_result)

            # Update stats
            self.crawl_stats["pages_crawled"] += 1
            self.crawl_stats["elements_extracted"] += len(elements)

            return CrawlResult(
                url=current_url,
                title=title,
                elements=elements,
                page_structure=page_structure,
                metadata={
                    "response_status": response.status if response else None,
                    "page_size": len(await page.content()),
                    "crawl_timestamp": datetime.now().isoformat(),
                    **self.crawl_stats,
                },
                linked_pages=linked_pages,
                success=True,
            )

        except Exception as e:
            self.crawl_stats["errors"] += 1
            raise e
        finally:
            await page.close()

    async def _extract_all_elements(self, page: Page) -> List[ElementData]:
        """Extract all elements with comprehensive analysis"""
        elements = []

        # Enhanced selectors with better categorization
        element_selectors = {
            ElementType.BUTTON: [
                "button",
                "input[type='button']",
                "input[type='submit']",
                "[role='button']",
                "a[onclick]",
                ".btn",
                ".button",
            ],
            ElementType.INPUT: [
                "input:not([type='button']):not([type='submit'])",
                "textarea",
                "select",
                "[contenteditable='true']",
            ],
            ElementType.LINK: ["a[href]", "[role='link']"],
            ElementType.FORM: ["form", "[role='form']"],
            ElementType.NAVIGATION: [
                "nav",
                "[role='navigation']",
                ".navbar",
                ".nav",
                ".menu",
            ],
            ElementType.TABLE: ["table", "[role='table']", ".table", ".data-table"],
            ElementType.MODAL: ["[role='dialog']", ".modal", ".popup", ".overlay"],
            ElementType.DROPDOWN: [
                "select",
                "[role='combobox']",
                ".dropdown",
                ".select",
            ],
            ElementType.TAB: ["[role='tab']", ".tab", ".tab-item"],
            ElementType.PAGINATION: [
                ".pagination",
                ".pager",
                "[aria-label*='pagination']",
            ],
            ElementType.SEARCH: [
                "input[type='search']",
                "input[placeholder*='search']",
                ".search-box",
                ".search-input",
            ],
        }

        for element_type, selectors in element_selectors.items():
            for selector in selectors:
                try:
                    page_elements = await page.query_selector_all(selector)

                    for element in page_elements:
                        element_data = await self._extract_element_data(
                            element, element_type, page
                        )
                        if element_data:
                            elements.append(element_data)

                except Exception as e:
                    print(
                        f"Failed to extract {element_type} with selector {selector}: {e}"
                    )

        # Remove duplicates based on element_id
        unique_elements = {}
        for element in elements:
            unique_elements[element.element_id] = element

        return list(unique_elements.values())

    async def _extract_element_data(
        self, element, element_type: ElementType, page: Page
    ) -> Optional[ElementData]:
        """Extract comprehensive data for a single element"""
        try:
            # Generate unique element ID
            element_id = await self._generate_element_id(element)

            # Basic properties
            tag_name = await element.evaluate("el => el.tagName.toLowerCase()")
            text_content = (await element.text_content() or "").strip()[:200]

            # Extract attributes
            attributes = await self._extract_all_attributes(element)

            # Generate locators with reliability scores
            locators = await self._generate_robust_locators(element, page)

            # Extract accessibility information
            accessibility = await self._extract_accessibility_data(element)

            # Get visual properties
            visual_properties = await self._extract_visual_properties(element)

            # Analyze behavioral properties
            behavioral_properties = await self._analyze_behavioral_properties(
                element, element_type
            )

            # Get element context
            context = await self._get_element_context(element)

            # Determine possible interactions
            interactions = await self._determine_interactions(element, element_type)

            # Generate test scenarios
            test_scenarios = await self._generate_test_scenarios(
                element, element_type, text_content
            )

            return ElementData(
                element_id=element_id,
                element_type=element_type,
                tag_name=tag_name,
                text_content=text_content,
                locators=locators,
                attributes=attributes,
                accessibility=accessibility,
                visual_properties=visual_properties,
                behavioral_properties=behavioral_properties,
                context=context,
                interactions=interactions,
                test_scenarios=test_scenarios,
                page_url=page.url,
                extraction_timestamp=datetime.now().isoformat(),
            )

        except Exception as e:
            print(f"Failed to extract element data: {e}")
            return None

    async def _generate_element_id(self, element) -> str:
        """Generate unique element identifier"""
        try:
            # Get unique properties
            tag = await element.evaluate("el => el.tagName.toLowerCase()")
            text = (await element.text_content() or "").strip()[:50]
            id_attr = await element.get_attribute("id") or ""
            class_attr = await element.get_attribute("class") or ""

            # Create hash-based unique ID
            unique_string = f"{tag}:{text}:{id_attr}:{class_attr}"
            return hashlib.md5(unique_string.encode()).hexdigest()[:12]

        except Exception:
            return f"elem_{int(time.time() * 1000)}"

    async def _extract_all_attributes(self, element) -> Dict[str, str]:
        """Extract all element attributes"""
        try:
            return await element.evaluate(
                """
                el => {
                    const attrs = {};
                    for (let attr of el.attributes) {
                        attrs[attr.name] = attr.value;
                    }
                    return attrs;
                }
            """
            )
        except Exception:
            return {}

    async def _generate_robust_locators(
        self, element, page: Page
    ) -> List[ElementLocator]:
        """Generate multiple locator strategies with reliability scores"""
        locators = []

        try:
            # Data-testid (highest reliability)
            test_id = await element.get_attribute("data-testid")
            if test_id:
                is_unique = await self._check_locator_uniqueness(
                    page, f"[data-testid='{test_id}']"
                )
                locators.append(
                    ElementLocator(
                        strategy=LocatorStrategy.DATA_TESTID,
                        value=f"[data-testid='{test_id}']",
                        reliability_score=0.95 if is_unique else 0.7,
                        is_unique=is_unique,
                    )
                )

            # ID attribute
            element_id = await element.get_attribute("id")
            if element_id:
                is_unique = await self._check_locator_uniqueness(page, f"#{element_id}")
                locators.append(
                    ElementLocator(
                        strategy=LocatorStrategy.ID,
                        value=f"#{element_id}",
                        reliability_score=0.9 if is_unique else 0.5,
                        is_unique=is_unique,
                    )
                )

            # Name attribute
            name = await element.get_attribute("name")
            if name:
                is_unique = await self._check_locator_uniqueness(
                    page, f"[name='{name}']"
                )
                locators.append(
                    ElementLocator(
                        strategy=LocatorStrategy.NAME,
                        value=f"[name='{name}']",
                        reliability_score=0.8 if is_unique else 0.4,
                        is_unique=is_unique,
                    )
                )

            # ARIA label
            aria_label = await element.get_attribute("aria-label")
            if aria_label:
                is_unique = await self._check_locator_uniqueness(
                    page, f"[aria-label='{aria_label}']"
                )
                locators.append(
                    ElementLocator(
                        strategy=LocatorStrategy.ARIA_LABEL,
                        value=f"[aria-label='{aria_label}']",
                        reliability_score=0.75 if is_unique else 0.4,
                        is_unique=is_unique,
                    )
                )

            # Role attribute
            role = await element.get_attribute("role")
            if role:
                is_unique = await self._check_locator_uniqueness(
                    page, f"[role='{role}']"
                )
                locators.append(
                    ElementLocator(
                        strategy=LocatorStrategy.ROLE,
                        value=f"[role='{role}']",
                        reliability_score=0.6 if is_unique else 0.3,
                        is_unique=is_unique,
                    )
                )

            # CSS selector (context-aware)
            css_selector = await self._generate_css_selector(element)
            if css_selector:
                is_unique = await self._check_locator_uniqueness(page, css_selector)
                locators.append(
                    ElementLocator(
                        strategy=LocatorStrategy.CSS_SELECTOR,
                        value=css_selector,
                        reliability_score=0.7 if is_unique else 0.3,
                        is_unique=is_unique,
                    )
                )

            # Text content (if unique and meaningful)
            text = (await element.text_content() or "").strip()
            if text and len(text) > 2 and len(text) < 50:
                text_selector = f":text('{text}')"
                is_unique = await self._check_locator_uniqueness(page, text_selector)
                if is_unique:
                    locators.append(
                        ElementLocator(
                            strategy=LocatorStrategy.TEXT_CONTENT,
                            value=text_selector,
                            reliability_score=0.8,
                            is_unique=True,
                        )
                    )

            # XPath (last resort)
            xpath = await self._generate_xpath(element)
            if xpath:
                locators.append(
                    ElementLocator(
                        strategy=LocatorStrategy.XPATH,
                        value=xpath,
                        reliability_score=0.5,
                        is_unique=False,
                        context="Generated XPath",
                    )
                )

        except Exception as e:
            print(f"Failed to generate locators: {e}")

        # Sort by reliability score
        locators.sort(key=lambda x: x.reliability_score, reverse=True)
        return locators

    async def _check_locator_uniqueness(self, page: Page, selector: str) -> bool:
        """Check if a locator is unique on the page"""
        try:
            elements = await page.query_selector_all(selector)
            return len(elements) == 1
        except Exception:
            return False

    async def _generate_css_selector(self, element) -> str:
        """Generate smart CSS selector"""
        try:
            return await element.evaluate(
                """
                el => {
                    function generateSelector(element) {
                        if (element.id) return '#' + element.id;
                        
                        let path = [];
                        while (element && element.nodeType === Node.ELEMENT_NODE) {
                            let selector = element.nodeName.toLowerCase();
                            
                            if (element.className) {
                                let classes = element.className.split(' ').filter(c => c && !c.includes(' '));
                                if (classes.length > 0) {
                                    selector += '.' + classes[0];
                                }
                            }
                            
                            // Add position if needed for uniqueness
                            let siblings = Array.from(element.parentNode?.children || [])
                                .filter(sibling => sibling.nodeName === element.nodeName);
                            if (siblings.length > 1) {
                                let index = siblings.indexOf(element) + 1;
                                selector += ':nth-of-type(' + index + ')';
                            }
                            
                            path.unshift(selector);
                            element = element.parentElement;
                            
                            // Stop at container elements to keep selector shorter
                            if (path.length >= 4) break;
                        }
                        
                        return path.join(' > ');
                    }
                    
                    return generateSelector(el);
                }
            """
            )
        except Exception:
            return ""

    async def _generate_xpath(self, element) -> str:
        """Generate XPath for element"""
        try:
            return await element.evaluate(
                """
                el => {
                    function getXPath(element) {
                        if (element.id) return "//*[@id='" + element.id + "']";
                        if (element === document.body) return '/html/body';
                        
                        let ix = 0;
                        let siblings = element.parentNode.childNodes;
                        for (let i = 0; i < siblings.length; i++) {
                            let sibling = siblings[i];
                            if (sibling === element) {
                                return getXPath(element.parentNode) + '/' + 
                                       element.tagName.toLowerCase() + '[' + (ix + 1) + ']';
                            }
                            if (sibling.nodeType === 1 && sibling.tagName === element.tagName) {
                                ix++;
                            }
                        }
                    }
                    return getXPath(el);
                }
            """
            )
        except Exception:
            return ""

    async def cleanup(self):
        """Cleanup browser resources"""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()

    async def _extract_accessibility_data(self, element) -> Dict[str, Any]:
        """Extract comprehensive accessibility information"""
        try:
            return {
                "aria_label": await element.get_attribute("aria-label"),
                "aria_role": await element.get_attribute("role"),
                "aria_described_by": await element.get_attribute("aria-describedby"),
                "aria_labelled_by": await element.get_attribute("aria-labelledby"),
                "aria_expanded": await element.get_attribute("aria-expanded"),
                "aria_hidden": await element.get_attribute("aria-hidden"),
                "aria_disabled": await element.get_attribute("aria-disabled"),
                "tabindex": await element.get_attribute("tabindex"),
                "alt_text": await element.get_attribute("alt"),
                "title": await element.get_attribute("title"),
                "focusable": await element.evaluate("el => el.tabIndex >= 0"),
                "has_aria_label": bool(await element.get_attribute("aria-label")),
                "has_accessible_name": await element.evaluate(
                    """
                    el => {
                        return !!(el.getAttribute('aria-label') || 
                                el.getAttribute('aria-labelledby') ||
                                el.getAttribute('title') ||
                                el.textContent?.trim());
                    }
                """
                ),
            }
        except Exception:
            return {}

    async def _extract_visual_properties(self, element) -> Dict[str, Any]:
        """Extract visual properties and positioning"""
        try:
            bounding_box = await element.bounding_box()
            is_visible = await element.is_visible()

            # Get computed styles
            styles = await element.evaluate(
                """
                el => {
                    const computed = window.getComputedStyle(el);
                    return {
                        display: computed.display,
                        visibility: computed.visibility,
                        opacity: computed.opacity,
                        position: computed.position,
                        zIndex: computed.zIndex,
                        backgroundColor: computed.backgroundColor,
                        color: computed.color,
                        fontSize: computed.fontSize,
                        fontFamily: computed.fontFamily,
                        border: computed.border,
                        margin: computed.margin,
                        padding: computed.padding
                    };
                }
            """
            )

            return {
                "bounding_box": bounding_box,
                "is_visible": is_visible,
                "is_in_viewport": await element.is_visible()
                and bounding_box is not None,
                "computed_styles": styles,
                "screenshot_path": None,  # Could implement element screenshots
            }
        except Exception:
            return {"is_visible": False, "bounding_box": None}

    async def _analyze_behavioral_properties(
        self, element, element_type: ElementType
    ) -> Dict[str, Any]:
        """Analyze element behavioral properties"""
        try:
            properties = {
                "is_clickable": await element.is_enabled()
                and await element.is_visible(),
                "is_editable": await element.is_editable(),
                "is_enabled": await element.is_enabled(),
                "is_checked": False,
                "is_selected": False,
                "has_focus": False,
                "accepts_files": False,
                "is_required": False,
                "is_readonly": False,
                "max_length": None,
                "pattern": None,
                "placeholder": None,
            }

            # Input-specific properties
            if element_type == ElementType.INPUT:
                input_type = await element.get_attribute("type") or "text"
                properties.update(
                    {
                        "input_type": input_type,
                        "is_required": bool(await element.get_attribute("required")),
                        "is_readonly": bool(await element.get_attribute("readonly")),
                        "max_length": await element.get_attribute("maxlength"),
                        "pattern": await element.get_attribute("pattern"),
                        "placeholder": await element.get_attribute("placeholder"),
                        "accepts_files": input_type == "file",
                        "is_checked": (
                            await element.is_checked()
                            if input_type in ["checkbox", "radio"]
                            else False
                        ),
                    }
                )

            # Form-specific properties
            elif element_type == ElementType.FORM:
                properties.update(
                    {
                        "method": await element.get_attribute("method") or "GET",
                        "action": await element.get_attribute("action"),
                        "enctype": await element.get_attribute("enctype"),
                        "novalidate": bool(await element.get_attribute("novalidate")),
                    }
                )

            # Link-specific properties
            elif element_type == ElementType.LINK:
                properties.update(
                    {
                        "href": await element.get_attribute("href"),
                        "target": await element.get_attribute("target"),
                        "download": await element.get_attribute("download"),
                        "is_external": await element.evaluate(
                            """
                        el => {
                            const href = el.getAttribute('href');
                            return href && (href.startsWith('http') && !href.includes(window.location.hostname));
                        }
                    """
                        ),
                    }
                )

            return properties
        except Exception:
            return {"is_clickable": False, "is_editable": False}

    async def _get_element_context(self, element) -> Dict[str, Any]:
        """Get element context and relationships"""
        try:
            context = await element.evaluate(
                """
                el => {
                    const parent = el.parentElement;
                    const siblings = parent ? Array.from(parent.children) : [];
                    const children = Array.from(el.children);
                    
                    return {
                        parent_tag: parent?.tagName?.toLowerCase(),
                        parent_class: parent?.className,
                        parent_id: parent?.id,
                        siblings_count: siblings.length,
                        children_count: children.length,
                        position_in_parent: siblings.indexOf(el),
                        has_form_ancestor: !!el.closest('form'),
                        has_table_ancestor: !!el.closest('table'),
                        has_nav_ancestor: !!el.closest('nav'),
                        nesting_level: (() => {
                            let level = 0;
                            let current = el.parentElement;
                            while (current && level < 10) {
                                level++;
                                current = current.parentElement;
                            }
                            return level;
                        })()
                    };
                }
            """
            )

            return context
        except Exception:
            return {}

    async def _determine_interactions(
        self, element, element_type: ElementType
    ) -> List[str]:
        """Determine possible interactions with the element"""
        interactions = []

        try:
            is_clickable = await element.is_enabled() and await element.is_visible()
            is_editable = await element.is_editable()
            tag_name = await element.evaluate("el => el.tagName.toLowerCase()")

            # Basic interactions
            if is_clickable:
                interactions.append("click")
                interactions.append("double_click")
                interactions.append("right_click")

            if is_editable:
                interactions.extend(["type", "fill", "clear"])

            # Element-type specific interactions
            if element_type == ElementType.INPUT:
                input_type = await element.get_attribute("type") or "text"

                if input_type in ["checkbox", "radio"]:
                    interactions.extend(["check", "uncheck"])
                elif input_type == "file":
                    interactions.append("upload_file")
                elif input_type in ["text", "email", "password", "search"]:
                    interactions.extend(["focus", "blur", "select_all"])
                elif input_type in ["number", "range"]:
                    interactions.extend(["increment", "decrement"])

            elif element_type == ElementType.DROPDOWN:
                interactions.extend(
                    ["select_option", "open_dropdown", "close_dropdown"]
                )

            elif element_type == ElementType.LINK:
                interactions.extend(["navigate", "open_in_new_tab"])

            elif element_type == ElementType.FORM:
                interactions.extend(["submit", "reset"])

            elif element_type == ElementType.TAB:
                interactions.extend(["activate_tab", "keyboard_navigate"])

            elif element_type == ElementType.MODAL:
                interactions.extend(["open_modal", "close_modal", "escape_close"])

            # Keyboard interactions
            if await element.evaluate("el => el.tabIndex >= 0"):
                interactions.extend(["focus", "blur", "keyboard_navigate"])

            # Drag and drop
            if tag_name in ["div", "span", "img"]:
                interactions.extend(["drag", "drop"])

            # Hover interactions
            interactions.append("hover")

        except Exception:
            pass

        return list(set(interactions))  # Remove duplicates

    async def _generate_test_scenarios(
        self, element, element_type: ElementType, text_content: str
    ) -> List[str]:
        """Generate test scenario suggestions for the element"""
        scenarios = []

        try:
            # Basic scenarios for all interactive elements
            if element_type in [ElementType.BUTTON, ElementType.LINK]:
                scenarios.extend(
                    [
                        f"Verify {text_content or 'element'} is clickable",
                        f"Verify {text_content or 'element'} click triggers expected action",
                        f"Verify {text_content or 'element'} is accessible via keyboard",
                        f"Verify {text_content or 'element'} has proper focus indicators",
                    ]
                )

            elif element_type == ElementType.INPUT:
                input_type = await element.get_attribute("type") or "text"
                field_name = (
                    text_content
                    or await element.get_attribute("placeholder")
                    or "input field"
                )

                if input_type in ["text", "email", "password"]:
                    scenarios.extend(
                        [
                            f"Verify {field_name} accepts valid input",
                            f"Verify {field_name} validates input format",
                            f"Verify {field_name} handles special characters",
                            f"Verify {field_name} required field validation",
                            f"Verify {field_name} maximum length validation",
                        ]
                    )
                elif input_type in ["checkbox", "radio"]:
                    scenarios.extend(
                        [
                            f"Verify {field_name} can be selected/deselected",
                            f"Verify {field_name} maintains state correctly",
                            f"Verify {field_name} keyboard accessibility",
                        ]
                    )

            elif element_type == ElementType.FORM:
                scenarios.extend(
                    [
                        "Verify form submission with valid data",
                        "Verify form validation with invalid data",
                        "Verify form reset functionality",
                        "Verify form accessibility",
                        "Verify form error handling",
                    ]
                )

            elif element_type == ElementType.NAVIGATION:
                scenarios.extend(
                    [
                        "Verify navigation menu is accessible",
                        "Verify navigation links work correctly",
                        "Verify navigation keyboard accessibility",
                        "Verify navigation responsive behavior",
                    ]
                )

            elif element_type == ElementType.TABLE:
                scenarios.extend(
                    [
                        "Verify table data displays correctly",
                        "Verify table sorting functionality",
                        "Verify table pagination if present",
                        "Verify table accessibility with screen readers",
                    ]
                )

            elif element_type == ElementType.MODAL:
                scenarios.extend(
                    [
                        "Verify modal opens correctly",
                        "Verify modal closes with close button",
                        "Verify modal closes with escape key",
                        "Verify modal focus management",
                        "Verify modal backdrop click behavior",
                    ]
                )

            # Add accessibility scenarios for all elements
            scenarios.extend(
                [
                    f"Verify {text_content or 'element'} screen reader compatibility",
                    f"Verify {text_content or 'element'} high contrast mode",
                    f"Verify {text_content or 'element'} keyboard-only navigation",
                ]
            )

        except Exception:
            pass

        return scenarios

    async def _analyze_page_structure(self, page: Page) -> PageStructure:
        """Comprehensive page structure analysis"""
        try:
            # Check for major structural elements
            has_navigation = bool(await page.query_selector("nav, [role='navigation']"))
            has_forms = bool(await page.query_selector("form"))
            has_tables = bool(await page.query_selector("table"))
            has_modals = bool(await page.query_selector("[role='dialog'], .modal"))
            has_pagination = bool(await page.query_selector(".pagination, .pager"))

            # Determine page type
            page_type = await self._determine_page_type(page)

            # Check responsive breakpoints
            responsive_breakpoints = await self._check_responsive_design(page)

            # Get performance metrics (placeholder - would need actual implementation)
            performance_metrics = {}

            # Calculate accessibility score (placeholder)
            accessibility_score = 0.0

            # Extract SEO elements
            seo_elements = await self._extract_seo_elements(page)

            return PageStructure(
                page_type=page_type,
                has_navigation=has_navigation,
                has_forms=has_forms,
                has_tables=has_tables,
                has_modals=has_modals,
                has_pagination=has_pagination,
                responsive_breakpoints=responsive_breakpoints,
                performance_metrics=performance_metrics,
                accessibility_score=accessibility_score,
                seo_elements=seo_elements,
            )

        except Exception as e:
            print(f"Failed to analyze page structure: {e}")
            return PageStructure(
                page_type="unknown",
                has_navigation=False,
                has_forms=False,
                has_tables=False,
                has_modals=False,
                has_pagination=False,
                responsive_breakpoints=[],
                performance_metrics={},
                accessibility_score=0.0,
                seo_elements={},
            )

    async def _determine_page_type(self, page: Page) -> str:
        """Determine the type of page using enhanced heuristics"""
        try:
            # Check for authentication pages
            if await page.query_selector("input[type='password']"):
                if await page.query_selector(
                    "input[type='email'], input[name*='email']"
                ):
                    return "login"
                elif await page.query_selector(
                    "input[name*='confirm'], input[name*='repeat']"
                ):
                    return "registration"
                else:
                    return "authentication"

            # Check for e-commerce pages
            if await page.query_selector(
                ".price, .cart, .checkout, [data-testid*='price']"
            ):
                if await page.query_selector(".product-list, .products-grid"):
                    return "product_listing"
                elif await page.query_selector(".product-detail, .product-info"):
                    return "product_detail"
                elif await page.query_selector(".cart, .shopping-cart"):
                    return "shopping_cart"
                elif await page.query_selector(".checkout, .payment"):
                    return "checkout"
                else:
                    return "ecommerce"

            # Check for admin/dashboard pages
            if await page.query_selector(".dashboard, .admin-panel, .sidebar"):
                return "dashboard"

            # Check for form pages
            form_elements = await page.query_selector_all("form")
            if len(form_elements) > 1:
                return "multi_form"
            elif len(form_elements) == 1:
                return "form"

            # Check for data display pages
            if await page.query_selector("table"):
                return "data_table"

            # Check for content pages
            if await page.query_selector("article, .article, .post, .blog"):
                return "content"

            # Check for search pages
            if await page.query_selector("input[type='search'], .search-results"):
                return "search"

            # Check for profile pages
            if await page.query_selector(".profile, .user-info, .account"):
                return "profile"

            # Default to landing page
            return "landing"

        except Exception:
            return "unknown"

    async def _check_responsive_design(self, page: Page) -> List[Dict[str, Any]]:
        """Check responsive design at different breakpoints"""
        breakpoints = [
            {"name": "mobile", "width": 375, "height": 667},
            {"name": "mobile_large", "width": 414, "height": 896},
            {"name": "tablet", "width": 768, "height": 1024},
            {"name": "desktop", "width": 1024, "height": 768},
            {"name": "desktop_large", "width": 1920, "height": 1080},
        ]

        results = []
        original_viewport = await page.viewport_size()

        for bp in breakpoints:
            try:
                await page.set_viewport_size(
                    {"width": bp["width"], "height": bp["height"]}
                )
                await asyncio.sleep(0.5)  # Wait for layout to adjust

                # Check for common responsive issues
                layout_analysis = await page.evaluate(
                    """
                    () => {
                        const issues = [];
                        
                        // Check for horizontal overflow
                        if (document.body.scrollWidth > window.innerWidth) {
                            issues.push('horizontal_overflow');
                        }
                        
                        // Check for overlapping elements (simplified)
                        const elements = document.querySelectorAll('*');
                        let overlapping = 0;
                        // This would need more sophisticated overlap detection
                        
                        // Check for very small text
                        const smallText = Array.from(document.querySelectorAll('*'))
                            .filter(el => {
                                const style = window.getComputedStyle(el);
                                const fontSize = parseInt(style.fontSize);
                                return fontSize > 0 && fontSize < 12;
                            }).length;
                        
                        if (smallText > 0) {
                            issues.push('small_text');
                        }
                        
                        return {
                            issues,
                            viewport_width: window.innerWidth,
                            viewport_height: window.innerHeight,
                            document_width: document.body.scrollWidth,
                            document_height: document.body.scrollHeight,
                            small_text_elements: smallText
                        };
                    }
                """
                )

                results.append(
                    {
                        "breakpoint": bp["name"],
                        "dimensions": f"{bp['width']}x{bp['height']}",
                        "layout_analysis": layout_analysis,
                        "responsive_score": 1.0
                        - (len(layout_analysis["issues"]) * 0.2),
                    }
                )

            except Exception as e:
                results.append(
                    {
                        "breakpoint": bp["name"],
                        "dimensions": f"{bp['width']}x{bp['height']}",
                        "error": str(e),
                        "responsive_score": 0.0,
                    }
                )

        # Restore original viewport
        if original_viewport:
            await page.set_viewport_size(original_viewport)

        return results

    async def _extract_seo_elements(self, page: Page) -> Dict[str, Any]:
        """Extract SEO-related elements"""
        try:
            return await page.evaluate(
                """
                () => {
                    const seo = {};
                    
                    // Meta tags
                    seo.title = document.title;
                    seo.meta_description = document.querySelector('meta[name="description"]')?.content;
                    seo.meta_keywords = document.querySelector('meta[name="keywords"]')?.content;
                    seo.canonical = document.querySelector('link[rel="canonical"]')?.href;
                    
                    // Open Graph tags
                    seo.og_title = document.querySelector('meta[property="og:title"]')?.content;
                    seo.og_description = document.querySelector('meta[property="og:description"]')?.content;
                    seo.og_image = document.querySelector('meta[property="og:image"]')?.content;
                    seo.og_url = document.querySelector('meta[property="og:url"]')?.content;
                    
                    // Twitter Card tags
                    seo.twitter_card = document.querySelector('meta[name="twitter:card"]')?.content;
                    seo.twitter_title = document.querySelector('meta[name="twitter:title"]')?.content;
                    seo.twitter_description = document.querySelector('meta[name="twitter:description"]')?.content;
                    
                    // Headings structure
                    seo.headings = {
                        h1: Array.from(document.querySelectorAll('h1')).map(h => h.textContent?.trim()),
                        h2: Array.from(document.querySelectorAll('h2')).map(h => h.textContent?.trim()),
                        h3: Array.from(document.querySelectorAll('h3')).map(h => h.textContent?.trim())
                    };
                    
                    // Links
                    seo.internal_links = Array.from(document.querySelectorAll('a[href]'))
                        .filter(a => a.href.includes(window.location.hostname)).length;
                    seo.external_links = Array.from(document.querySelectorAll('a[href]'))
                        .filter(a => !a.href.includes(window.location.hostname) && a.href.startsWith('http')).length;
                    
                    // Images
                    const images = Array.from(document.querySelectorAll('img'));
                    seo.images_without_alt = images.filter(img => !img.alt).length;
                    seo.total_images = images.length;
                    
                    return seo;
                }
            """
            )
        except Exception:
            return {}

    async def _get_performance_metrics(
        self, page: Page, nav_time: float
    ) -> Dict[str, Any]:
        """Get basic performance metrics"""
        try:
            # Get basic timing information
            timing = await page.evaluate(
                """
                () => {
                    const perfData = performance.getEntriesByType('navigation')[0];
                    if (perfData) {
                        return {
                            dom_content_loaded: perfData.domContentLoadedEventEnd - perfData.domContentLoadedEventStart,
                            load_complete: perfData.loadEventEnd - perfData.loadEventStart,
                            first_paint: performance.getEntriesByType('paint')
                                .find(entry => entry.name === 'first-paint')?.startTime,
                            first_contentful_paint: performance.getEntriesByType('paint')
                                .find(entry => entry.name === 'first-contentful-paint')?.startTime
                        };
                    }
                    return {};
                }
            """
            )

            # Page size information
            content = await page.content()
            page_size = len(content.encode("utf-8"))

            # Resource counts
            resource_counts = await page.evaluate(
                """
                () => {
                    const resources = performance.getEntriesByType('resource');
                    const counts = {
                        total: resources.length,
                        scripts: resources.filter(r => r.initiatorType === 'script').length,
                        stylesheets: resources.filter(r => r.initiatorType === 'css').length,
                        images: resources.filter(r => r.initiatorType === 'img').length,
                        fonts: resources.filter(r => r.initiatorType === 'other' && r.name.match(/\\.woff2?$/)).length
                    };
                    return counts;
                }
            """
            )

            return {
                "navigation_time": nav_time,
                "page_size_bytes": page_size,
                "dom_timing": timing,
                "resource_counts": resource_counts,
                "performance_score": min(
                    1.0, max(0.0, (5.0 - nav_time) / 5.0)
                ),  # Simple score
            }

        except Exception:
            return {"navigation_time": nav_time}

    async def _calculate_accessibility_score(
        self, elements: List[ElementData]
    ) -> float:
        """Calculate basic accessibility score based on elements"""
        if not elements:
            return 0.0

        total_score = 0.0
        interactive_elements = [
            e
            for e in elements
            if e.element_type
            in [ElementType.BUTTON, ElementType.INPUT, ElementType.LINK]
        ]

        if not interactive_elements:
            return 0.5  # Neutral score for non-interactive pages

        for element in interactive_elements:
            element_score = 0.0

            # Check for accessible name
            if (
                element.accessibility.get("has_accessible_name")
                or element.text_content.strip()
                or element.accessibility.get("aria_label")
            ):
                element_score += 0.3

            # Check for proper role
            if element.accessibility.get("aria_role"):
                element_score += 0.2

            # Check for focusable
            if element.accessibility.get("focusable"):
                element_score += 0.2

            # Check for keyboard accessibility
            if element.behavioral_properties.get("is_clickable"):
                element_score += 0.2

            # Check for visibility
            if element.visual_properties.get("is_visible"):
                element_score += 0.1

            total_score += min(1.0, element_score)

        return total_score / len(interactive_elements)

    async def _extract_valid_links(self, page: Page, base_url: str) -> List[str]:
        """Extract valid internal links for crawling"""
        try:
            links = await page.evaluate(
                """
                (baseUrl) => {
                    const links = Array.from(document.querySelectorAll('a[href]'));
                    const validLinks = [];
                    const baseHostname = new URL(baseUrl).hostname;
                    
                    for (const link of links) {
                        try {
                            const href = link.href;
                            const url = new URL(href);
                            
                            // Only include same-domain links
                            if (url.hostname === baseHostname && 
                                !href.includes('#') &&  // Skip anchors
                                !href.includes('mailto:') &&  // Skip email links
                                !href.includes('tel:') &&  // Skip phone links
                                !href.includes('javascript:') &&  // Skip javascript links
                                !href.match(/\\.(pdf|doc|xls|zip|exe)$/i)) {  // Skip file downloads
                                validLinks.push(href);
                            }
                        } catch (e) {
                            // Skip invalid URLs
                        }
                    }
                    
                    // Remove duplicates
                    return [...new Set(validLinks)];
                }
            """,
                base_url,
            )

            return links[:20]  # Limit to prevent excessive crawling

        except Exception:
            return []

