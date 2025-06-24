"""
Web UI Testing Automation Plugin

This plugin provides AI-powered web UI test automation capabilities:
- URL crawling with configurable depth
- Intelligent element extraction using robust locator strategies
- LLM-powered Gherkin test case generation
- Page Object Model (POM) generation
- Test fixtures and executable Playwright test scripts
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException
from core.plugins import BasePlugin, PluginMetadata, PluginStatus
from core.llm import llm_manager, LLMMessage, MessageRole, PromptTemplate
from .crawler import AdvancedWebCrawler, CrawlResult
from .test_generator import (
    LLMTestGenerator,
    TestGenerationConfig,
    TestFramework,
    ProgrammingLanguage,
    TestType,
)


class WebTestingPlugin(BasePlugin):
    """Web UI Testing Automation Plugin"""

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.router = APIRouter()
        self._setup_routes()
        self._setup_templates()

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="web_testing",
            version="1.0.0",
            description="AI-powered web UI testing automation with Playwright",
            author="AI Base Platform",
            dependencies=["playwright", "beautifulsoup4", "selenium"],
            api_version="1.0",
            config_schema={
                "default_browser": {"type": "string", "default": "chromium"},
                "max_crawl_depth": {"type": "integer", "default": 3},
                "page_load_timeout": {"type": "integer", "default": 30000},
                "element_timeout": {"type": "integer", "default": 10000},
                "llm_provider": {"type": "string", "default": "openai"},
                "generate_visual_tests": {"type": "boolean", "default": True},
            },
        )

    async def initialize(self) -> bool:
        """Initialize the web testing plugin"""
        try:
            # Initialize crawler
            crawler_config = {
                "browser": self.config.get("default_browser", "chromium"),
                "headless": True,
                "sample_size": self.config.get("max_elements", 100),
            }
            self.crawler = AdvancedWebCrawler(crawler_config)

            # Initialize Playwright if available
            try:
                from playwright.async_api import async_playwright

                self.playwright = await async_playwright().start()
                await self.crawler.initialize(self.playwright)
            except ImportError:
                print("Playwright not installed - some features may be limited")
                self.playwright = None

            # Setup LLM templates for test generation
            await self._initialize_llm_templates()

            return True
        except Exception as e:
            print(f"Failed to initialize Web Testing plugin: {e}")
            return False

    async def cleanup(self) -> bool:
        """Cleanup resources"""
        try:
            if hasattr(self, "playwright"):
                await self.playwright.stop()
            return True
        except Exception:
            return False

    def get_api_routes(self) -> List[Dict[str, Any]]:
        """Return API routes for web testing"""
        return [{"path": "/api/v1/web-testing", "router": self.router}]

    def get_frontend_routes(self) -> List[Dict[str, Any]]:
        """Return frontend routes for web testing"""
        return [
            {
                "path": "/apps/web-testing",
                "component": "WebTestingApp",
                "name": "Web Testing",
                "icon": "Globe",
            }
        ]

    def _setup_routes(self):
        """Setup API routes"""

        @self.router.post("/crawl")
        async def crawl_website(request: Dict[str, Any]):
            """Crawl a website and extract testable elements"""
            return await self._crawl_website(
                url=request["url"],
                max_depth=request.get("max_depth", 2),
                options=request.get("options", {}),
            )

        @self.router.post("/generate-tests")
        async def generate_tests(request: Dict[str, Any]):
            """Generate test cases from crawled elements"""
            return await self._generate_test_cases(
                elements=request["elements"],
                test_type=request.get("test_type", "functional"),
                framework=request.get("framework", "playwright"),
            )

        @self.router.post("/generate-pom")
        async def generate_pom(request: Dict[str, Any]):
            """Generate Page Object Model classes"""
            return await self._generate_page_objects(
                page_data=request["page_data"],
                language=request.get("language", "python"),
            )

        @self.router.get("/health")
        async def health_check():
            """Web testing plugin health check"""
            return await self.health_check()

    def _setup_templates(self):
        """Setup LLM prompt templates"""
        # Template for generating Gherkin scenarios
        gherkin_template = PromptTemplate(
            template="""
You are an expert QA engineer. Based on the following web page elements, generate comprehensive Gherkin test scenarios.

Page URL: {page_url}
Page Title: {page_title}

Elements found:
{elements_description}

Requirements:
1. Generate realistic user scenarios using Given-When-Then format
2. Cover positive and negative test cases
3. Include accessibility and usability tests
4. Focus on user workflows and business logic
5. Use descriptive scenario names
6. Include data-driven test examples where appropriate

Generate 5-10 comprehensive test scenarios in Gherkin format.
""",
            variables=["page_url", "page_title", "elements_description"],
        )

        # Template for generating Page Object Model
        pom_template = PromptTemplate(
            template="""
You are a test automation expert. Generate a Page Object Model class for the following web page.

Page URL: {page_url}
Page Title: {page_title}
Programming Language: {language}
Framework: {framework}

Elements with locators:
{elements_with_locators}

Requirements:
1. Create a clean, maintainable Page Object Model class
2. Use robust locator strategies (prefer data-testid, then CSS, then XPath)
3. Include page validation methods
4. Add action methods for all interactive elements
5. Include proper error handling and waits
6. Follow {framework} best practices
7. Add comprehensive docstrings

Generate the complete Page Object Model class.
""",
            variables=[
                "page_url",
                "page_title",
                "language",
                "framework",
                "elements_with_locators",
            ],
        )

        # Template for generating test fixtures
        fixtures_template = PromptTemplate(
            template="""
You are a test automation expert. Generate test fixtures and test data for the following test scenarios.

Page URL: {page_url}
Test Framework: {framework}
Scenarios: {scenarios}

Requirements:
1. Generate realistic test data for all scenarios
2. Include both valid and invalid data sets
3. Create reusable fixtures
4. Include setup and teardown methods
5. Handle different user roles and permissions
6. Generate configuration data
7. Include test data management utilities

Generate comprehensive test fixtures and data.
""",
            variables=["page_url", "framework", "scenarios"],
        )

        # Register templates
        llm_manager.register_template("gherkin_generation", gherkin_template)
        llm_manager.register_template("pom_generation", pom_template)
        llm_manager.register_template("fixtures_generation", fixtures_template)

    async def _initialize_llm_templates(self):
        """Initialize LLM templates"""
        self._setup_templates()

    async def _crawl_website(
        self, url: str, max_depth: int = 2, options: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Crawl website and extract testable elements"""
        try:
            browser = await self.playwright.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()

            # Navigate to the page
            await page.goto(url, wait_until="networkidle")

            # Extract page metadata
            title = await page.title()
            page_url = page.url

            # Extract all interactive elements
            elements = await self._extract_elements(page)

            # Get page structure
            page_structure = await self._analyze_page_structure(page)

            # If max_depth > 1, crawl linked pages
            linked_pages = []
            if max_depth > 1:
                links = await page.query_selector_all("a[href]")
                for link in links[:10]:  # Limit to first 10 links
                    href = await link.get_attribute("href")
                    if href and href.startswith(("http", "/")):
                        try:
                            # Recursively crawl linked pages
                            linked_page_data = await self._crawl_website(
                                url=(
                                    href
                                    if href.startswith("http")
                                    else f"{url.rstrip('/')}/{href.lstrip('/')}"
                                ),
                                max_depth=max_depth - 1,
                                options=options,
                            )
                            linked_pages.append(linked_page_data)
                        except Exception:
                            continue  # Skip failed pages

            await browser.close()

            return {
                "url": page_url,
                "title": title,
                "elements": elements,
                "page_structure": page_structure,
                "linked_pages": linked_pages,
                "crawl_timestamp": "2025-01-01T00:00:00Z",  # Use actual timestamp
                "metadata": {
                    "total_elements": len(elements),
                    "interactive_elements": len(
                        [e for e in elements if e.get("interactive", False)]
                    ),
                    "crawl_depth": max_depth,
                },
            }

        except Exception as e:
            raise RuntimeError(f"Failed to crawl website: {str(e)}")

    async def _extract_elements(self, page) -> List[Dict[str, Any]]:
        """Extract all testable elements from a page"""
        elements = []

        # Define element selectors for different types
        selectors = {
            "buttons": "button, input[type='button'], input[type='submit'], [role='button']",
            "inputs": "input:not([type='button']):not([type='submit']), textarea, select",
            "links": "a[href]",
            "forms": "form",
            "images": "img",
            "tables": "table",
            "lists": "ul, ol",
            "headings": "h1, h2, h3, h4, h5, h6",
            "navigation": "nav, [role='navigation']",
            "modals": "[role='dialog'], .modal",
            "tabs": "[role='tab'], .tab",
            "accordions": "[role='button'][aria-expanded]",
        }

        for element_type, selector in selectors.items():
            try:
                page_elements = await page.query_selector_all(selector)

                for element in page_elements:
                    element_data = await self._extract_element_data(
                        element, element_type
                    )
                    if element_data:
                        elements.append(element_data)

            except Exception as e:
                print(f"Failed to extract {element_type}: {e}")

        return elements

    async def _extract_element_data(self, element, element_type: str) -> Dict[str, Any]:
        """Extract comprehensive data for a single element"""
        try:
            # Get basic attributes
            tag_name = await element.evaluate("el => el.tagName.toLowerCase()")
            text_content = await element.text_content()

            # Generate multiple locator strategies
            locators = await self._generate_locators(element)

            # Check if element is interactive
            is_interactive = element_type in ["buttons", "inputs", "links", "forms"]

            # Get visual properties
            bounding_box = await element.bounding_box()
            is_visible = await element.is_visible()

            # Get accessibility attributes
            accessibility = await self._extract_accessibility_info(element)

            # Get element context (parent, siblings)
            context = await self._get_element_context(element)

            return {
                "type": element_type,
                "tag": tag_name,
                "text": text_content[:100] if text_content else "",  # Limit text length
                "locators": locators,
                "interactive": is_interactive,
                "visible": is_visible,
                "bounding_box": bounding_box,
                "accessibility": accessibility,
                "context": context,
                "metadata": {"extraction_timestamp": "2025-01-01T00:00:00Z"},
            }

        except Exception as e:
            print(f"Failed to extract element data: {e}")
            return None

    async def _generate_locators(self, element) -> Dict[str, str]:
        """Generate multiple robust locator strategies for an element"""
        locators = {}

        try:
            # Data-testid (most preferred)
            test_id = await element.get_attribute("data-testid")
            if test_id:
                locators["data_testid"] = f"[data-testid='{test_id}']"

            # ID
            element_id = await element.get_attribute("id")
            if element_id:
                locators["id"] = f"#{element_id}"

            # Name
            name = await element.get_attribute("name")
            if name:
                locators["name"] = f"[name='{name}']"

            # Class (if unique enough)
            class_list = await element.get_attribute("class")
            if class_list:
                locators["class"] = f".{class_list.split()[0]}"

            # CSS selector
            css_path = await element.evaluate(
                """
                el => {
                    let path = [];
                    while (el && el.nodeType === Node.ELEMENT_NODE) {
                        let selector = el.nodeName.toLowerCase();
                        if (el.id) {
                            selector += '#' + el.id;
                            path.unshift(selector);
                            break;
                        } else if (el.className) {
                            selector += '.' + el.className.split(' ')[0];
                        }
                        path.unshift(selector);
                        el = el.parentNode;
                    }
                    return path.join(' > ');
                }
            """
            )
            if css_path:
                locators["css_path"] = css_path

            # XPath (last resort)
            xpath = await element.evaluate(
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
                                return getXPath(element.parentNode) + '/' + element.tagName.toLowerCase() + '[' + (ix + 1) + ']';
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
            if xpath:
                locators["xpath"] = xpath

        except Exception as e:
            print(f"Failed to generate locators: {e}")

        return locators

    async def _extract_accessibility_info(self, element) -> Dict[str, Any]:
        """Extract accessibility information"""
        try:
            return {
                "aria_label": await element.get_attribute("aria-label"),
                "aria_role": await element.get_attribute("role"),
                "aria_described_by": await element.get_attribute("aria-describedby"),
                "tabindex": await element.get_attribute("tabindex"),
                "alt_text": await element.get_attribute("alt"),
            }
        except Exception:
            return {}

    async def _get_element_context(self, element) -> Dict[str, Any]:
        """Get element context information"""
        try:
            parent_tag = await element.evaluate(
                "el => el.parentElement ? el.parentElement.tagName.toLowerCase() : null"
            )
            return {
                "parent_tag": parent_tag,
                "position_in_parent": (
                    await element.evaluate(
                        """
                    el => Array.from(el.parentElement.children).indexOf(el)
                """
                    )
                    if parent_tag
                    else -1
                ),
            }
        except Exception:
            return {}

    async def _analyze_page_structure(self, page) -> Dict[str, Any]:
        """Analyze overall page structure"""
        try:
            return {
                "has_navigation": bool(
                    await page.query_selector("nav, [role='navigation']")
                ),
                "has_forms": bool(await page.query_selector("form")),
                "has_tables": bool(await page.query_selector("table")),
                "has_modals": bool(
                    await page.query_selector("[role='dialog'], .modal")
                ),
                "page_type": await self._determine_page_type(page),
                "responsive_breakpoints": await self._check_responsive_design(page),
            }
        except Exception:
            return {}

    async def _determine_page_type(self, page) -> str:
        """Determine the type of page (login, dashboard, form, etc.)"""
        # Simple heuristics - can be enhanced with ML
        if await page.query_selector("input[type='password']"):
            return "login"
        elif await page.query_selector("form"):
            return "form"
        elif await page.query_selector("table"):
            return "data_table"
        elif await page.query_selector("[role='dashboard']"):
            return "dashboard"
        else:
            return "content"

    async def _check_responsive_design(self, page) -> List[Dict[str, Any]]:
        """Check responsive design breakpoints"""
        breakpoints = [
            {"name": "mobile", "width": 375, "height": 667},
            {"name": "tablet", "width": 768, "height": 1024},
            {"name": "desktop", "width": 1920, "height": 1080},
        ]

        results = []
        for bp in breakpoints:
            await page.set_viewport_size({"width": bp["width"], "height": bp["height"]})
            # Check if layout is still functional
            visible_elements = await page.query_selector_all(":visible")
            results.append(
                {
                    "breakpoint": bp["name"],
                    "dimensions": f"{bp['width']}x{bp['height']}",
                    "visible_elements": len(visible_elements),
                    "layout_issues": [],  # Could detect overlapping elements, etc.
                }
            )

        return results

    async def _generate_test_cases(
        self,
        elements: List[Dict[str, Any]],
        test_type: str = "functional",
        framework: str = "playwright",
    ) -> Dict[str, Any]:
        """Generate test cases using LLM"""
        try:
            # Prepare elements description for LLM
            elements_desc = "\n".join(
                [
                    f"- {elem['type']}: {elem['text'][:50]} (locators: {list(elem['locators'].keys())})"
                    for elem in elements[:20]  # Limit to avoid token limits
                ]
            )

            # Generate Gherkin scenarios
            gherkin_response = await llm_manager.generate(
                provider_name="openai",
                template_name="gherkin_generation",
                template_vars={
                    "page_url": elements[0]
                    .get("metadata", {})
                    .get("page_url", "Unknown"),
                    "page_title": "Web Page",  # Should come from crawl data
                    "elements_description": elements_desc,
                },
            )

            return {
                "test_type": test_type,
                "framework": framework,
                "gherkin_scenarios": gherkin_response.content,
                "elements_count": len(elements),
                "generation_metadata": {
                    "provider": gherkin_response.provider.value,
                    "model": gherkin_response.model,
                    "tokens_used": gherkin_response.tokens_used,
                    "cost": gherkin_response.cost,
                },
            }

        except Exception as e:
            raise RuntimeError(f"Failed to generate test cases: {str(e)}")

    async def _generate_page_objects(
        self, page_data: Dict[str, Any], language: str = "python"
    ) -> Dict[str, Any]:
        """Generate Page Object Model using LLM"""
        try:
            # Format elements with locators for POM generation
            elements_with_locators = "\n".join(
                [
                    f"- {elem['type']} '{elem['text'][:30]}': {elem['locators']}"
                    for elem in page_data.get("elements", [])[:15]
                ]
            )

            pom_response = await llm_manager.generate(
                provider_name="openai",
                template_name="pom_generation",
                template_vars={
                    "page_url": page_data.get("url", "Unknown"),
                    "page_title": page_data.get("title", "Unknown Page"),
                    "language": language,
                    "framework": "playwright",
                    "elements_with_locators": elements_with_locators,
                },
            )

            return {
                "language": language,
                "framework": "playwright",
                "page_object_code": pom_response.content,
                "page_url": page_data.get("url"),
                "generation_metadata": {
                    "provider": pom_response.provider.value,
                    "model": pom_response.model,
                    "tokens_used": pom_response.tokens_used,
                    "cost": pom_response.cost,
                },
            }

        except Exception as e:
            raise RuntimeError(f"Failed to generate page objects: {str(e)}")

    async def health_check(self) -> Dict[str, Any]:
        """Health check for web testing plugin"""
        try:
            # Check if Playwright is available
            playwright_available = hasattr(self, "playwright")

            # Check if LLM is available
            llm_available = len(llm_manager._providers) > 0

            status = "healthy" if playwright_available and llm_available else "degraded"

            return {
                "status": status,
                "message": f"Web Testing plugin is {status}",
                "details": {
                    "playwright_available": playwright_available,
                    "llm_available": llm_available,
                    "supported_browsers": ["chromium", "firefox", "webkit"],
                    "supported_frameworks": ["playwright", "selenium"],
                },
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Web Testing plugin error: {str(e)}",
                "details": {},
            }
