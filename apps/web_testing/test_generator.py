"""
LLM-Powered Test Generation

This module provides comprehensive AI-powered test generation capabilities:
- Gherkin scenario generation from crawled elements
- Page Object Model (POM) generation
- Test fixtures and data generation
- Executable test code generation for multiple frameworks
- Test strategy recommendations
"""

import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum
from core.llm import llm_manager, PromptTemplate, LLMMessage, MessageRole


class TestFramework(Enum):
    """Supported test frameworks"""

    PLAYWRIGHT = "playwright"
    SELENIUM = "selenium"
    CYPRESS = "cypress"
    WEBDRIVER_IO = "webdriverio"


class TestType(Enum):
    """Types of tests to generate"""

    FUNCTIONAL = "functional"
    ACCESSIBILITY = "accessibility"
    PERFORMANCE = "performance"
    VISUAL = "visual"
    API = "api"
    E2E = "e2e"
    SMOKE = "smoke"
    REGRESSION = "regression"


class ProgrammingLanguage(Enum):
    """Supported programming languages"""

    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    CSHARP = "csharp"


@dataclass
class TestGenerationConfig:
    """Configuration for test generation"""

    framework: TestFramework
    language: ProgrammingLanguage
    test_types: List[TestType]
    include_data_driven: bool = True
    include_visual_tests: bool = False
    include_performance_tests: bool = False
    include_accessibility_tests: bool = True
    parallel_execution: bool = True
    generate_fixtures: bool = True
    generate_page_objects: bool = True
    test_data_format: str = "json"  # json, yaml, csv
    naming_convention: str = "snake_case"  # snake_case, camelCase, PascalCase


@dataclass
class GeneratedTest:
    """Generated test artifact"""

    test_type: TestType
    framework: TestFramework
    language: ProgrammingLanguage
    file_name: str
    content: str
    dependencies: List[str]
    metadata: Dict[str, Any]


@dataclass
class TestSuite:
    """Complete test suite"""

    name: str
    description: str
    page_objects: List[GeneratedTest]
    test_files: List[GeneratedTest]
    fixtures: List[GeneratedTest]
    test_data: List[GeneratedTest]
    config_files: List[GeneratedTest]
    documentation: str
    setup_instructions: str


class LLMTestGenerator:
    """LLM-powered test generation engine"""

    def __init__(self, config: TestGenerationConfig):
        self.config = config
        self._setup_templates()

    def _setup_templates(self):
        """Setup LLM prompt templates for test generation"""

        # Gherkin scenario generation template
        gherkin_template = PromptTemplate(
            template="""
You are an expert QA engineer specializing in behavior-driven development (BDD). 
Generate comprehensive Gherkin test scenarios for a web application.

## Context
Page URL: {page_url}
Page Title: {page_title}
Page Type: {page_type}

## Page Elements
{elements_summary}

## Page Structure
{page_structure}

## Requirements
1. Generate realistic user scenarios using Given-When-Then format
2. Cover both positive and negative test cases
3. Include edge cases and error scenarios
4. Focus on user workflows and business logic
5. Use descriptive scenario names and clear step definitions
6. Include accessibility testing scenarios
7. Consider mobile and responsive behavior
8. Add data-driven test examples where appropriate
9. Include performance considerations where relevant
10. Follow BDD best practices

## Test Types to Include
{test_types}

## Output Format
Generate 8-15 comprehensive Gherkin scenarios with:
- Feature description
- Background steps (if applicable)
- Multiple scenarios covering different user paths
- Examples tables for data-driven tests
- Tags for test organization

Generate professional, realistic test scenarios that a QA team would actually use.
""",
            variables=[
                "page_url",
                "page_title",
                "page_type",
                "elements_summary",
                "page_structure",
                "test_types",
            ],
        )

        # Page Object Model generation template
        pom_template = PromptTemplate(
            template="""
You are a test automation expert. Generate a comprehensive Page Object Model (POM) class 
for the following web page using {framework} and {language}.

## Page Information
URL: {page_url}
Title: {page_title}
Page Type: {page_type}

## Elements with Locators
{elements_with_locators}

## Page Structure Analysis
{page_structure}

## Framework Requirements
Framework: {framework}
Language: {language}
Naming Convention: {naming_convention}

## POM Requirements
1. Create a clean, maintainable Page Object Model class
2. Use the most reliable locator strategies (prefer data-testid, then ID, then CSS)
3. Include comprehensive page validation methods
4. Add action methods for all interactive elements
5. Include proper error handling and explicit waits
6. Follow {framework} and {language} best practices
7. Add comprehensive docstrings and comments
8. Include method chaining where appropriate
9. Add logging for debugging
10. Handle dynamic elements and loading states
11. Include mobile-specific methods if applicable
12. Add screenshot capabilities for debugging

## Class Structure
- Constructor/initialization with page/driver
- Element locators as class properties
- Page validation methods
- Action methods for each interactive element
- Navigation methods
- Utility methods for common operations
- Error handling and logging

Generate a complete, production-ready Page Object Model class with comprehensive functionality.
""",
            variables=[
                "page_url",
                "page_title",
                "page_type",
                "elements_with_locators",
                "page_structure",
                "framework",
                "language",
                "naming_convention",
            ],
        )

        # Test code generation template
        test_code_template = PromptTemplate(
            template="""
You are a senior test automation engineer. Generate comprehensive test code based on the 
following Gherkin scenarios using {framework} and {language}.

## Test Configuration
Framework: {framework}
Language: {language}
Test Type: {test_type}
Naming Convention: {naming_convention}

## Gherkin Scenarios
{gherkin_scenarios}

## Page Object Model Classes
{page_object_classes}

## Test Data
{test_data}

## Requirements
1. Generate executable test code that implements the Gherkin scenarios
2. Use the provided Page Object Model classes
3. Include proper test setup and teardown
4. Add comprehensive assertions and validations
5. Implement proper error handling and reporting
6. Include parallel execution capabilities
7. Add logging and debugging information
8. Follow {framework} best practices and patterns
9. Include test data management
10. Add retry logic for flaky tests
11. Include accessibility testing where specified
12. Add performance assertions where relevant

## Code Structure
- Test class with proper inheritance/structure
- Setup and teardown methods
- Test methods for each scenario
- Helper methods for common operations
- Test data management
- Configuration and utilities

Generate production-ready test code with comprehensive coverage and error handling.
""",
            variables=[
                "framework",
                "language",
                "test_type",
                "naming_convention",
                "gherkin_scenarios",
                "page_object_classes",
                "test_data",
            ],
        )

        # Test fixtures generation template
        fixtures_template = PromptTemplate(
            template="""
You are a test automation expert. Generate comprehensive test fixtures and test data 
for the following test scenarios.

## Configuration
Framework: {framework}
Language: {language}
Test Data Format: {test_data_format}

## Test Scenarios
{test_scenarios}

## Page Objects
{page_objects_info}

## Requirements
1. Generate realistic test data for all scenarios
2. Include both valid and invalid data sets
3. Create reusable fixtures for common setup/teardown
4. Include different user roles and permissions
5. Generate configuration data and environment settings
6. Include database setup/cleanup if needed
7. Add API mock data if applicable
8. Include test data for edge cases
9. Generate data for performance testing
10. Include accessibility test data
11. Add internationalization test data
12. Include responsive design test data

## Fixtures to Generate
- User account fixtures (different roles)
- Test data files ({test_data_format} format)
- Database fixtures
- API response fixtures
- Configuration fixtures
- Environment setup fixtures
- Browser/device configuration fixtures

Generate comprehensive, realistic test fixtures that support all testing scenarios.
""",
            variables=[
                "framework",
                "language",
                "test_data_format",
                "test_scenarios",
                "page_objects_info",
            ],
        )

        # Test strategy template
        strategy_template = PromptTemplate(
            template="""
You are a QA architect. Generate a comprehensive test strategy and recommendations 
for the following web application.

## Application Analysis
Page URL: {page_url}
Page Type: {page_type}
Total Elements: {total_elements}
Interactive Elements: {interactive_elements}

## Page Structure
{page_structure}

## Current Test Coverage
{existing_tests}

## Requirements
1. Analyze the application structure and complexity
2. Recommend appropriate test types and coverage
3. Suggest test automation strategy
4. Identify risk areas and critical paths
5. Recommend testing tools and frameworks
6. Suggest test data management approach
7. Recommend CI/CD integration strategy
8. Identify accessibility testing requirements
9. Suggest performance testing approach
10. Recommend maintenance and scalability strategies

## Strategy Areas
- Test pyramid recommendations
- Risk-based testing approach
- Tool selection rationale
- Test environment requirements
- Test data management strategy
- CI/CD integration plan
- Maintenance and scaling considerations
- Training and skill requirements

Generate a comprehensive test strategy document with actionable recommendations.
""",
            variables=[
                "page_url",
                "page_type",
                "total_elements",
                "interactive_elements",
                "page_structure",
                "existing_tests",
            ],
        )

        # Register templates
        llm_manager.register_template("gherkin_generation", gherkin_template)
        llm_manager.register_template("pom_generation", pom_template)
        llm_manager.register_template("test_code_generation", test_code_template)
        llm_manager.register_template("fixtures_generation", fixtures_template)
        llm_manager.register_template("test_strategy", strategy_template)

    async def generate_test_suite(
        self, crawl_result, provider_name: str = "openai"
    ) -> TestSuite:
        """Generate complete test suite from crawl results"""

        # Prepare data for LLM
        elements_summary = self._create_elements_summary(crawl_result.elements)
        page_structure_summary = self._create_page_structure_summary(
            crawl_result.page_structure
        )

        # Generate Gherkin scenarios
        gherkin_content = await self._generate_gherkin_scenarios(
            crawl_result, elements_summary, page_structure_summary, provider_name
        )

        # Generate Page Object Models
        page_objects = await self._generate_page_objects(
            crawl_result, elements_summary, page_structure_summary, provider_name
        )

        # Generate test code
        test_files = await self._generate_test_code(
            gherkin_content, page_objects, provider_name
        )

        # Generate fixtures and test data
        fixtures = await self._generate_fixtures(
            gherkin_content, page_objects, provider_name
        )

        # Generate configuration files
        config_files = await self._generate_config_files()

        # Generate documentation
        documentation = await self._generate_documentation(
            crawl_result, gherkin_content, provider_name
        )

        return TestSuite(
            name=f"test_suite_{crawl_result.title.lower().replace(' ', '_')}",
            description=f"Comprehensive test suite for {crawl_result.title}",
            page_objects=page_objects,
            test_files=test_files,
            fixtures=fixtures,
            test_data=[],  # Will be populated by fixtures generation
            config_files=config_files,
            documentation=documentation,
            setup_instructions=self._generate_setup_instructions(),
        )

    async def _generate_gherkin_scenarios(
        self,
        crawl_result,
        elements_summary: str,
        page_structure_summary: str,
        provider_name: str,
    ) -> str:
        """Generate Gherkin scenarios using LLM"""

        test_types_str = ", ".join([t.value for t in self.config.test_types])

        response = await llm_manager.generate(
            provider_name=provider_name,
            template_name="gherkin_generation",
            template_vars={
                "page_url": crawl_result.url,
                "page_title": crawl_result.title,
                "page_type": crawl_result.page_structure.page_type,
                "elements_summary": elements_summary,
                "page_structure": page_structure_summary,
                "test_types": test_types_str,
            },
        )

        return response.content

    async def _generate_page_objects(
        self,
        crawl_result,
        elements_summary: str,
        page_structure_summary: str,
        provider_name: str,
    ) -> List[GeneratedTest]:
        """Generate Page Object Model classes"""

        # Format elements with their best locators
        elements_with_locators = self._format_elements_for_pom(crawl_result.elements)

        response = await llm_manager.generate(
            provider_name=provider_name,
            template_name="pom_generation",
            template_vars={
                "page_url": crawl_result.url,
                "page_title": crawl_result.title,
                "page_type": crawl_result.page_structure.page_type,
                "elements_with_locators": elements_with_locators,
                "page_structure": page_structure_summary,
                "framework": self.config.framework.value,
                "language": self.config.language.value,
                "naming_convention": self.config.naming_convention,
            },
        )

        # Generate file name based on page
        page_name = crawl_result.title.lower().replace(" ", "_").replace("-", "_")
        file_extension = self._get_file_extension(self.config.language)
        file_name = f"{page_name}_page{file_extension}"

        return [
            GeneratedTest(
                test_type=TestType.FUNCTIONAL,
                framework=self.config.framework,
                language=self.config.language,
                file_name=file_name,
                content=response.content,
                dependencies=self._get_framework_dependencies(),
                metadata={
                    "page_url": crawl_result.url,
                    "page_title": crawl_result.title,
                    "elements_count": len(crawl_result.elements),
                    "generation_timestamp": response.metadata.get("timestamp"),
                    "tokens_used": response.tokens_used,
                    "provider": response.provider.value,
                },
            )
        ]

    async def _generate_test_code(
        self,
        gherkin_content: str,
        page_objects: List[GeneratedTest],
        provider_name: str,
    ) -> List[GeneratedTest]:
        """Generate executable test code"""

        test_files = []

        for test_type in self.config.test_types:
            # Prepare page object classes info
            page_object_classes = "\n\n".join([po.content for po in page_objects])

            response = await llm_manager.generate(
                provider_name=provider_name,
                template_name="test_code_generation",
                template_vars={
                    "framework": self.config.framework.value,
                    "language": self.config.language.value,
                    "test_type": test_type.value,
                    "naming_convention": self.config.naming_convention,
                    "gherkin_scenarios": gherkin_content,
                    "page_object_classes": page_object_classes,
                    "test_data": "{}",  # Will be enhanced with actual test data
                },
            )

            file_extension = self._get_file_extension(self.config.language)
            file_name = f"test_{test_type.value}{file_extension}"

            test_files.append(
                GeneratedTest(
                    test_type=test_type,
                    framework=self.config.framework,
                    language=self.config.language,
                    file_name=file_name,
                    content=response.content,
                    dependencies=self._get_framework_dependencies(),
                    metadata={
                        "test_type": test_type.value,
                        "gherkin_scenarios_count": gherkin_content.count("Scenario:"),
                        "generation_timestamp": response.metadata.get("timestamp"),
                        "tokens_used": response.tokens_used,
                        "provider": response.provider.value,
                    },
                )
            )

        return test_files

    async def _generate_fixtures(
        self,
        gherkin_content: str,
        page_objects: List[GeneratedTest],
        provider_name: str,
    ) -> List[GeneratedTest]:
        """Generate test fixtures and data"""

        if not self.config.generate_fixtures:
            return []

        # Prepare page objects info
        page_objects_info = "\n".join(
            [
                f"- {po.file_name}: {po.metadata.get('page_title', 'Unknown')}"
                for po in page_objects
            ]
        )

        response = await llm_manager.generate(
            provider_name=provider_name,
            template_name="fixtures_generation",
            template_vars={
                "framework": self.config.framework.value,
                "language": self.config.language.value,
                "test_data_format": self.config.test_data_format,
                "test_scenarios": gherkin_content,
                "page_objects_info": page_objects_info,
            },
        )

        # Create multiple fixture files
        fixtures = []

        # Main fixtures file
        file_extension = self._get_file_extension(self.config.language)
        fixtures.append(
            GeneratedTest(
                test_type=TestType.FUNCTIONAL,
                framework=self.config.framework,
                language=self.config.language,
                file_name=f"fixtures{file_extension}",
                content=response.content,
                dependencies=self._get_framework_dependencies(),
                metadata={
                    "fixture_type": "main",
                    "generation_timestamp": response.metadata.get("timestamp"),
                    "tokens_used": response.tokens_used,
                    "provider": response.provider.value,
                },
            )
        )

        # Test data file
        test_data_extension = f".{self.config.test_data_format}"
        fixtures.append(
            GeneratedTest(
                test_type=TestType.FUNCTIONAL,
                framework=self.config.framework,
                language=self.config.language,
                file_name=f"test_data{test_data_extension}",
                content=self._generate_sample_test_data(),
                dependencies=[],
                metadata={
                    "fixture_type": "test_data",
                    "format": self.config.test_data_format,
                },
            )
        )

        return fixtures

    async def _generate_config_files(self) -> List[GeneratedTest]:
        """Generate framework configuration files"""
        config_files = []

        if self.config.framework == TestFramework.PLAYWRIGHT:
            if self.config.language == ProgrammingLanguage.PYTHON:
                config_files.append(
                    GeneratedTest(
                        test_type=TestType.FUNCTIONAL,
                        framework=self.config.framework,
                        language=self.config.language,
                        file_name="pytest.ini",
                        content=self._generate_pytest_config(),
                        dependencies=[],
                        metadata={"config_type": "pytest"},
                    )
                )

                config_files.append(
                    GeneratedTest(
                        test_type=TestType.FUNCTIONAL,
                        framework=self.config.framework,
                        language=self.config.language,
                        file_name="requirements.txt",
                        content=self._generate_requirements_txt(),
                        dependencies=[],
                        metadata={"config_type": "dependencies"},
                    )
                )

            # Playwright config
            config_files.append(
                GeneratedTest(
                    test_type=TestType.FUNCTIONAL,
                    framework=self.config.framework,
                    language=self.config.language,
                    file_name=(
                        "playwright.config.js"
                        if self.config.language
                        in [
                            ProgrammingLanguage.JAVASCRIPT,
                            ProgrammingLanguage.TYPESCRIPT,
                        ]
                        else "playwright.config.py"
                    ),
                    content=self._generate_playwright_config(),
                    dependencies=[],
                    metadata={"config_type": "playwright"},
                )
            )

        return config_files

    async def _generate_documentation(
        self, crawl_result, gherkin_content: str, provider_name: str
    ) -> str:
        """Generate comprehensive test documentation"""

        # This could also use LLM to generate documentation
        # For now, creating a template-based documentation

        docs = f"""# Test Suite Documentation

## Overview
This test suite was automatically generated for: **{crawl_result.title}**
- **URL**: {crawl_result.url}
- **Page Type**: {crawl_result.page_structure.page_type}
- **Framework**: {self.config.framework.value}
- **Language**: {self.config.language.value}

## Test Statistics
- **Total Elements**: {len(crawl_result.elements)}
- **Interactive Elements**: {len([e for e in crawl_result.elements if 'click' in e.interactions])}
- **Test Scenarios**: {gherkin_content.count('Scenario:')}
- **Test Types**: {', '.join([t.value for t in self.config.test_types])}

## Page Structure Analysis
- **Navigation**: {'✅' if crawl_result.page_structure.has_navigation else '❌'}
- **Forms**: {'✅' if crawl_result.page_structure.has_forms else '❌'}
- **Tables**: {'✅' if crawl_result.page_structure.has_tables else '❌'}
- **Modals**: {'✅' if crawl_result.page_structure.has_modals else '❌'}
- **Pagination**: {'✅' if crawl_result.page_structure.has_pagination else '❌'}

## Test Execution
1. Install dependencies: `pip install -r requirements.txt`
2. Install Playwright browsers: `playwright install`
3. Run tests: `pytest tests/`
4. Generate reports: `pytest --html=report.html`

## Maintenance
- Update page objects when UI changes
- Review and update test data regularly
- Monitor test execution times
- Keep dependencies updated

## Generated Files
- Page Object Models: `pages/`
- Test Files: `tests/`
- Fixtures: `fixtures/`
- Test Data: `data/`
- Configuration: `config/`
"""

        return docs

    def _create_elements_summary(self, elements) -> str:
        """Create a summary of page elements for LLM"""
        summary = []

        # Group elements by type
        element_groups = {}
        for element in elements:
            elem_type = element.element_type.value
            if elem_type not in element_groups:
                element_groups[elem_type] = []
            element_groups[elem_type].append(element)

        for elem_type, elem_list in element_groups.items():
            summary.append(f"\n**{elem_type.title()} Elements ({len(elem_list)}):**")

            for i, element in enumerate(elem_list[:5]):  # Limit to first 5 of each type
                best_locator = element.locators[0] if element.locators else None
                locator_str = (
                    f"{best_locator.strategy.value}: {best_locator.value}"
                    if best_locator
                    else "No locator"
                )

                text = (
                    element.text_content[:50] + "..."
                    if len(element.text_content) > 50
                    else element.text_content
                )
                summary.append(f"  {i+1}. {text or 'No text'} ({locator_str})")

                # Add interactions
                if element.interactions:
                    summary.append(
                        f"     Interactions: {', '.join(element.interactions[:3])}"
                    )

            if len(elem_list) > 5:
                summary.append(f"  ... and {len(elem_list) - 5} more")

        return "\n".join(summary)

    def _create_page_structure_summary(self, page_structure) -> str:
        """Create a summary of page structure for LLM"""
        return f"""
Page Type: {page_structure.page_type}
Has Navigation: {page_structure.has_navigation}
Has Forms: {page_structure.has_forms}
Has Tables: {page_structure.has_tables}
Has Modals: {page_structure.has_modals}
Has Pagination: {page_structure.has_pagination}
Accessibility Score: {page_structure.accessibility_score:.2f}
Responsive Breakpoints: {len(page_structure.responsive_breakpoints)}
Performance Score: {page_structure.performance_metrics.get('performance_score', 'N/A')}
"""

    def _format_elements_for_pom(self, elements) -> str:
        """Format elements with locators for POM generation"""
        formatted = []

        for element in elements[:20]:  # Limit for token management
            if not element.locators:
                continue

            best_locator = element.locators[
                0
            ]  # Best locator is first (sorted by reliability)
            text = (
                element.text_content[:30] + "..."
                if len(element.text_content) > 30
                else element.text_content
            )

            formatted.append(
                f"- {element.element_type.value}: '{text or 'No text'}'\n"
                f"  Locator: {best_locator.strategy.value} = '{best_locator.value}'\n"
                f"  Reliability: {best_locator.reliability_score:.2f}\n"
                f"  Interactions: {', '.join(element.interactions[:3])}\n"
            )

        return "\n".join(formatted)

    def _get_file_extension(self, language: ProgrammingLanguage) -> str:
        """Get file extension for programming language"""
        extensions = {
            ProgrammingLanguage.PYTHON: ".py",
            ProgrammingLanguage.JAVASCRIPT: ".js",
            ProgrammingLanguage.TYPESCRIPT: ".ts",
            ProgrammingLanguage.JAVA: ".java",
            ProgrammingLanguage.CSHARP: ".cs",
        }
        return extensions.get(language, ".py")

    def _get_framework_dependencies(self) -> List[str]:
        """Get framework dependencies"""
        if self.config.framework == TestFramework.PLAYWRIGHT:
            if self.config.language == ProgrammingLanguage.PYTHON:
                return ["playwright", "pytest", "pytest-html", "pytest-xdist"]
            else:
                return ["@playwright/test", "@types/node"]
        elif self.config.framework == TestFramework.SELENIUM:
            return ["selenium", "webdriver-manager", "pytest"]
        return []

    def _generate_sample_test_data(self) -> str:
        """Generate sample test data"""
        if self.config.test_data_format == "json":
            return json.dumps(
                {
                    "users": {
                        "valid_user": {
                            "username": "test_user",
                            "password": "Test123!",
                            "email": "test@example.com",
                        },
                        "invalid_user": {
                            "username": "",
                            "password": "weak",
                            "email": "invalid-email",
                        },
                    },
                    "test_strings": {
                        "special_characters": "!@#$%^&*()_+",
                        "unicode": "测试データ",
                        "long_string": "A" * 1000,
                        "sql_injection": "'; DROP TABLE users; --",
                    },
                },
                indent=2,
            )
        else:
            return "# Sample test data\nuser_name: test_user\npassword: Test123!"

    def _generate_pytest_config(self) -> str:
        """Generate pytest configuration"""
        return """[tool:pytest]
addopts = 
    --verbose
    --tb=short
    --strict-markers
    --disable-warnings
    --html=reports/report.html
    --self-contained-html
    
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

markers =
    smoke: Smoke tests
    regression: Regression tests
    functional: Functional tests
    accessibility: Accessibility tests
    performance: Performance tests
    slow: Slow running tests
"""

    def _generate_requirements_txt(self) -> str:
        """Generate requirements.txt"""
        deps = self._get_framework_dependencies()
        additional_deps = ["allure-pytest", "pytest-mock", "faker", "requests"]
        all_deps = deps + additional_deps
        return "\n".join(all_deps)

    def _generate_playwright_config(self) -> str:
        """Generate Playwright configuration"""
        if self.config.language == ProgrammingLanguage.PYTHON:
            return """import pytest
from playwright.sync_api import Playwright, BrowserType
from typing import Dict, Any

@pytest.fixture(scope="session")
def browser_config() -> Dict[str, Any]:
    return {
        "headless": True,
        "slow_mo": 0,
        "timeout": 30000,
        "viewport": {"width": 1920, "height": 1080}
    }

@pytest.fixture(scope="session")
def playwright_config(browser_config):
    return {
        "browser_name": "chromium",
        "browser_config": browser_config,
        "base_url": "http://localhost:3000"
    }
"""
        else:
            return """import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
  ],
});
"""

    def _generate_setup_instructions(self) -> str:
        """Generate setup instructions"""
        return f"""# Test Suite Setup Instructions

## Prerequisites
- {self.config.language.value.title()} runtime installed
- Package manager (pip for Python, npm for JavaScript/TypeScript)

## Installation
1. Clone the repository
2. Install dependencies:
   ```bash
   {'pip install -r requirements.txt' if self.config.language == ProgrammingLanguage.PYTHON else 'npm install'}
   ```

3. Install {self.config.framework.value} browsers:
   ```bash
   {'playwright install' if self.config.framework == TestFramework.PLAYWRIGHT else 'webdriver-manager chrome'}
   ```

## Running Tests
- All tests: `{'pytest' if self.config.language == ProgrammingLanguage.PYTHON else 'npm test'}`
- Specific test type: `{'pytest -m smoke' if self.config.language == ProgrammingLanguage.PYTHON else 'npm run test:smoke'}`
- With reports: `{'pytest --html=report.html' if self.config.language == ProgrammingLanguage.PYTHON else 'npm run test:report'}`

## Configuration
- Update base URLs in configuration files
- Modify browser settings as needed
- Adjust timeouts for your environment
"""
