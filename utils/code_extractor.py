"""
Generic Code Extractor - Comprehensive and Input-Agnostic
Supports multiple input types and advanced extraction strategies
"""

import json
import re
import os
import csv
import xml.etree.ElementTree as ET
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Union, Tuple, Iterator
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
import argparse
import mimetypes
from urllib.parse import urlparse
import base64


# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class ExtractedCode:
    """Represents an extracted code block with comprehensive metadata"""

    content: str
    language: str
    source_type: str  # 'json', 'text', 'html', 'xml', 'markdown', etc.
    extraction_method: str  # 'triple_backtick', 'inline', 'indented', etc.
    confidence: float  # 0.0 to 1.0 confidence in extraction accuracy
    context: Dict[str, Any]  # Additional context (line numbers, message index, etc.)
    metadata: Dict[str, Any]  # File info, timestamps, etc.

    def __post_init__(self):
        """Validate and normalize data after initialization"""
        self.content = self.content.strip()
        self.language = self.language.lower()
        self.confidence = max(0.0, min(1.0, self.confidence))


class InputProcessor(ABC):
    """Abstract base class for input processors"""

    @abstractmethod
    def can_process(self, input_data: Any) -> bool:
        """Check if this processor can handle the input"""
        pass

    @abstractmethod
    def process(self, input_data: Any) -> List[Dict[str, Any]]:
        """Process input and return normalized text blocks"""
        pass


class JSONProcessor(InputProcessor):
    """Process JSON conversation data"""

    def can_process(self, input_data: Any) -> bool:
        if isinstance(input_data, str):
            try:
                json.loads(input_data)
                return True
            except:
                return False
        return isinstance(input_data, (list, dict))

    def process(self, input_data: Any) -> List[Dict[str, Any]]:
        if isinstance(input_data, str):
            data = json.loads(input_data)
        else:
            data = input_data

        texts = []
        if isinstance(data, list):
            for idx, item in enumerate(data):
                text_content = self._extract_text_from_message(item)
                if text_content:
                    texts.append(
                        {
                            "text": text_content,
                            "context": {
                                "message_index": idx,
                                "role": item.get("role", "unknown"),
                                "timestamp": item.get("timestamp"),
                            },
                        }
                    )
        elif isinstance(data, dict):
            text_content = self._extract_text_from_message(data)
            if text_content:
                texts.append(
                    {
                        "text": text_content,
                        "context": {"role": data.get("role", "unknown")},
                    }
                )

        return texts

    def _extract_text_from_message(self, message: Dict) -> str:
        """Extract text content from various message formats"""
        if "content" in message:
            content = message["content"]
            if isinstance(content, str):
                return content
            elif isinstance(content, list):
                text_parts = []
                for item in content:
                    if isinstance(item, dict):
                        if item.get("type") == "text":
                            text_parts.append(item.get("text", ""))
                        elif "text" in item:
                            text_parts.append(item["text"])
                    elif isinstance(item, str):
                        text_parts.append(item)
                return "\n".join(text_parts)

        # Try other common fields
        for field in ["text", "message", "body", "description"]:
            if field in message and isinstance(message[field], str):
                return message[field]

        return ""


class TextProcessor(InputProcessor):
    """Process plain text data"""

    def can_process(self, input_data: Any) -> bool:
        return isinstance(input_data, str)

    def process(self, input_data: Any) -> List[Dict[str, Any]]:
        return [{"text": input_data, "context": {"source": "plain_text"}}]


class HTMLProcessor(InputProcessor):
    """Process HTML content"""

    def can_process(self, input_data: Any) -> bool:
        if isinstance(input_data, str):
            return bool(re.search(r"<[^>]+>", input_data))
        return False

    def process(self, input_data: Any) -> List[Dict[str, Any]]:
        texts = []

        # Extract text from code tags
        code_patterns = [
            (r"<code[^>]*>(.*?)</code>", "html_code"),
            (r"<pre[^>]*>(.*?)</pre>", "html_pre"),
            (r"<script[^>]*>(.*?)</script>", "javascript"),
            (r"<style[^>]*>(.*?)</style>", "css"),
        ]

        for pattern, tag_type in code_patterns:
            matches = re.finditer(pattern, input_data, re.DOTALL | re.IGNORECASE)
            for idx, match in enumerate(matches):
                texts.append(
                    {
                        "text": match.group(1),
                        "context": {
                            "tag_type": tag_type,
                            "match_index": idx,
                            "start_pos": match.start(),
                            "end_pos": match.end(),
                        },
                    }
                )

        # Also extract plain text content
        text_content = re.sub(r"<[^>]+>", "", input_data)
        if text_content.strip():
            texts.append({"text": text_content, "context": {"source": "html_text"}})

        return texts


class MarkdownProcessor(InputProcessor):
    """Process Markdown content"""

    def can_process(self, input_data: Any) -> bool:
        if isinstance(input_data, str):
            # Check for markdown patterns
            md_patterns = [r"```", r"`[^`]+`", r"^\s*#", r"^\s*\*", r"^\s*\d+\."]
            return any(
                re.search(pattern, input_data, re.MULTILINE) for pattern in md_patterns
            )
        return False

    def process(self, input_data: Any) -> List[Dict[str, Any]]:
        return [{"text": input_data, "context": {"source": "markdown"}}]


class XMLProcessor(InputProcessor):
    """Process XML content"""

    def can_process(self, input_data: Any) -> bool:
        if isinstance(input_data, str):
            try:
                ET.fromstring(input_data)
                return True
            except:
                return False
        return False

    def process(self, input_data: Any) -> List[Dict[str, Any]]:
        texts = []
        try:
            root = ET.fromstring(input_data)

            # Extract text from specific tags that might contain code
            code_tags = ["code", "script", "query", "command", "example"]
            for tag in code_tags:
                elements = root.findall(f".//{tag}")
                for idx, elem in enumerate(elements):
                    if elem.text:
                        texts.append(
                            {
                                "text": elem.text,
                                "context": {
                                    "xml_tag": tag,
                                    "element_index": idx,
                                    "attributes": elem.attrib,
                                },
                            }
                        )

            # Extract all text content as fallback
            all_text = "".join(root.itertext())
            if all_text.strip():
                texts.append({"text": all_text, "context": {"source": "xml_all_text"}})

        except Exception as e:
            # Fallback to plain text processing
            texts.append(
                {
                    "text": input_data,
                    "context": {"source": "xml_fallback", "error": str(e)},
                }
            )

        return texts


class GenericCodeExtractor:
    """Comprehensive code extractor with advanced strategies"""

    def __init__(self):
        self.processors = [
            JSONProcessor(),
            HTMLProcessor(),
            MarkdownProcessor(),
            XMLProcessor(),
            TextProcessor(),  # Always last as fallback
        ]

        self.extraction_patterns = {
            "triple_backtick": {
                "pattern": r"```(\w+)?\s*\n?(.*?)\n?```",
                "confidence": 0.95,
                "flags": re.DOTALL,
                "groups": {"language": 1, "content": 2},
            },
            "single_backtick": {
                "pattern": r"`([^`\n]+)`",
                "confidence": 0.8,
                "flags": 0,
                "groups": {"content": 1},
            },
            "indented_code": {
                "pattern": r"(?:^|\n)((?:    .+(?:\n|$))+)",
                "confidence": 0.7,
                "flags": re.MULTILINE,
                "groups": {"content": 1},
            },
            "fenced_tilde": {
                "pattern": r"~~~(\w+)?\s*\n?(.*?)\n?~~~",
                "confidence": 0.9,
                "flags": re.DOTALL,
                "groups": {"language": 1, "content": 2},
            },
            "html_code": {
                "pattern": r"<code[^>]*>(.*?)</code>",
                "confidence": 0.85,
                "flags": re.DOTALL | re.IGNORECASE,
                "groups": {"content": 1},
            },
            "html_pre": {
                "pattern": r"<pre[^>]*>(.*?)</pre>",
                "confidence": 0.85,
                "flags": re.DOTALL | re.IGNORECASE,
                "groups": {"content": 1},
            },
            "script_tag": {
                "pattern": r'<script[^>]*type=["\']([^"\']+)["\'][^>]*>(.*?)</script>',
                "confidence": 0.9,
                "flags": re.DOTALL | re.IGNORECASE,
                "groups": {"language": 1, "content": 2},
            },
            "style_tag": {
                "pattern": r"<style[^>]*>(.*?)</style>",
                "confidence": 0.9,
                "flags": re.DOTALL | re.IGNORECASE,
                "groups": {"content": 1},
            },
            "heredoc": {
                "pattern": r"<<(\w+)\s*\n(.*?)\n\1",
                "confidence": 0.8,
                "flags": re.DOTALL,
                "groups": {"language": 1, "content": 2},
            },
            "language_comment": {
                "pattern": r"(?:^|\n)\s*(?://|#|--)\s*(?:lang|language):\s*(\w+)\s*\n((?:(?!(?:^|\n)\s*(?://|#|--)).)*)",
                "confidence": 0.85,
                "flags": re.MULTILINE | re.DOTALL,
                "groups": {"language": 1, "content": 2},
            },
        }

        # Language detection patterns
        self.language_patterns = {
            "python": [
                r"\bdef\s+\w+\s*\(",
                r"\bimport\s+\w+",
                r"\bfrom\s+\w+\s+import",
                r"\.py\b",
            ],
            "javascript": [
                r"\bfunction\s+\w+\s*\(",
                r"\bvar\s+\w+",
                r"\blet\s+\w+",
                r"\bconst\s+\w+",
                r"\.js\b",
            ],
            "typescript": [
                r"\binterface\s+\w+",
                r"\btype\s+\w+\s*=",
                r":\s*\w+\[\]",
                r"\.ts\b",
            ],
            "java": [
                r"\bpublic\s+class\s+\w+",
                r"\bpublic\s+static\s+void\s+main",
                r"\.java\b",
            ],
            "csharp": [
                r"\busing\s+System",
                r"\bpublic\s+class\s+\w+",
                r"\bnamespace\s+\w+",
                r"\.cs\b",
            ],
            "cpp": [r"#include\s*<", r"\bstd::", r"\.cpp\b", r"\.hpp\b"],
            "c": [r"#include\s*<stdio\.h>", r"\bint\s+main\s*\(", r"\.c\b", r"\.h\b"],
            "html": [r"<html", r"<!DOCTYPE", r"<div", r"<span", r"\.html\b"],
            "css": [r"\{[^}]*\}", r"@media", r"\.css\b"],
            "sql": [
                r"\bSELECT\s+",
                r"\bFROM\s+\w+",
                r"\bINSERT\s+INTO",
                r"\bUPDATE\s+\w+",
            ],
            "json": [r"^\s*\{.*\}\s*$", r"^\s*\[.*\]\s*$"],
            "xml": [r"<\?xml", r"<\w+[^>]*>", r"\.xml\b"],
            "yaml": [r"^\s*\w+:\s*", r"^\s*-\s+"],
            "bash": [r"#!/bin/bash", r"\$\{?\w+\}?", r"\.sh\b"],
            "powershell": [r"Get-\w+", r"Set-\w+", r"\$\w+", r"\.ps1\b"],
            "go": [
                r"\bfunc\s+\w+\s*\(",
                r"\bpackage\s+\w+",
                r"\bimport\s*\(",
                r"\.go\b",
            ],
            "rust": [r"\bfn\s+\w+\s*\(", r"\buse\s+\w+", r"\blet\s+mut\s+", r"\.rs\b"],
            "php": [r"<\?php", r"\$\w+", r"\.php\b"],
            "ruby": [r"\bdef\s+\w+", r"\bclass\s+\w+", r"\bend\b", r"\.rb\b"],
            "swift": [
                r"\bfunc\s+\w+\s*\(",
                r"\bvar\s+\w+",
                r"\blet\s+\w+",
                r"\.swift\b",
            ],
            "kotlin": [r"\bfun\s+\w+\s*\(", r"\bval\s+\w+", r"\bvar\s+\w+", r"\.kt\b"],
            "scala": [
                r"\bdef\s+\w+\s*\(",
                r"\bobject\s+\w+",
                r"\bclass\s+\w+",
                r"\.scala\b",
            ],
            "r": [r"<-", r"\blibrary\s*\(", r"\bdata\.frame", r"\.r\b"],
            "matlab": [r"\bfunction\s+\w+", r"\.m\b"],
            "svg": [r"<svg", r"<path", r"<circle", r"<rect"],
            "dockerfile": [r"\bFROM\s+", r"\bRUN\s+", r"\bCOPY\s+", r"Dockerfile"],
            "makefile": [r"^\w+:", r"\$\(.*\)", r"Makefile"],
        }

    def extract(
        self,
        input_data: Any,
        source_type: Optional[str] = None,
        patterns: Optional[List[str]] = None,
        min_confidence: float = 0.0,
    ) -> List[ExtractedCode]:
        """
        Extract code from any input type

        Args:
            input_data: Input to extract from (str, dict, list, etc.)
            source_type: Override source type detection
            patterns: List of extraction patterns to use (None for all)
            min_confidence: Minimum confidence threshold for results

        Returns:
            List of ExtractedCode objects
        """
        logger.debug(
            f"Starting extraction with source_type={source_type}, patterns={patterns}, min_confidence={min_confidence}"
        )

        # Determine source type
        if source_type is None:
            source_type = self._detect_source_type(input_data)

        logger.debug(f"Detected source type: {source_type}")

        # Process input to get text blocks
        text_blocks = self._process_input(input_data, source_type)
        logger.debug(f"Found {len(text_blocks)} text blocks to process")

        # Extract code from each text block
        extracted_codes = []
        for i, text_block in enumerate(text_blocks):
            logger.debug(f"Processing text block {i+1}/{len(text_blocks)}")
            codes = self._extract_from_text_block(
                text_block, source_type, patterns, min_confidence
            )
            extracted_codes.extend(codes)

        logger.debug(f"Extraction complete. Found {len(extracted_codes)} code blocks")
        return extracted_codes

    def _detect_source_type(self, input_data: Any) -> str:
        """Detect the source type of input data"""
        for processor in self.processors:
            if processor.can_process(input_data):
                return processor.__class__.__name__.replace("Processor", "").lower()
        return "unknown"

    def _process_input(self, input_data: Any, source_type: str) -> List[Dict[str, Any]]:
        """Process input using appropriate processor"""
        for processor in self.processors:
            if processor.can_process(input_data):
                return processor.process(input_data)

        # Fallback
        return [{"text": str(input_data), "context": {"source": "fallback"}}]

    def _extract_from_text_block(
        self,
        text_block: Dict[str, Any],
        source_type: str,
        patterns: Optional[List[str]] = None,
        min_confidence: float = 0.0,
    ) -> List[ExtractedCode]:
        """Extract code from a single text block"""
        text = text_block["text"]
        context = text_block["context"]

        logger.debug(f"Extracting from text block with {len(text)} characters")

        if patterns is None:
            patterns = list(self.extraction_patterns.keys())

        extracted_codes = []

        for pattern_name in patterns:
            if pattern_name not in self.extraction_patterns:
                logger.warning(f"Unknown pattern: {pattern_name}")
                continue

            pattern_info = self.extraction_patterns[pattern_name]
            pattern = pattern_info["pattern"]
            base_confidence = pattern_info["confidence"]
            flags = pattern_info.get("flags", 0)
            groups = pattern_info["groups"]

            matches = re.finditer(pattern, text, flags)

            for match_idx, match in enumerate(matches):
                try:
                    # Extract content and language
                    content = ""
                    language = "text"

                    if "content" in groups:
                        content = match.group(groups["content"])

                    if "language" in groups and match.group(groups["language"]):
                        language = match.group(groups["language"])
                    else:
                        # Try to detect language from content
                        detected_lang = self._detect_language(content)
                        if detected_lang:
                            language = detected_lang

                    # Skip empty content
                    if not content or not content.strip():
                        continue

                    # Calculate confidence
                    confidence = self._calculate_confidence(
                        content, language, pattern_name, base_confidence
                    )

                    if confidence < min_confidence:
                        logger.debug(
                            f"Skipping match with confidence {confidence:.3f} < {min_confidence}"
                        )
                        continue

                    # Create metadata
                    metadata = {
                        "match_index": match_idx,
                        "start_pos": match.start(),
                        "end_pos": match.end(),
                        "original_length": len(text),
                        "extracted_length": len(content),
                    }

                    # Merge context
                    full_context = {**context, **metadata}

                    logger.debug(
                        f"Extracted {language} code block with confidence {confidence:.3f} using {pattern_name}"
                    )

                    extracted_codes.append(
                        ExtractedCode(
                            content=content,
                            language=language,
                            source_type=source_type,
                            extraction_method=pattern_name,
                            confidence=confidence,
                            context=full_context,
                            metadata=metadata,
                        )
                    )

                except Exception as e:
                    # Log error but continue processing
                    logger.error(
                        f"Error processing match with pattern {pattern_name}: {e}"
                    )
                    continue

        return extracted_codes

    def _detect_language(self, content: str) -> Optional[str]:
        """Detect programming language from content"""
        content_lower = content.lower()

        # Score each language
        language_scores = {}
        for lang, patterns in self.language_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(
                    re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
                )
                score += matches

            if score > 0:
                language_scores[lang] = score

        if not language_scores:
            return None

        # Return language with highest score
        return max(language_scores, key=language_scores.get)

    def _calculate_confidence(
        self,
        content: str,
        language: str,
        extraction_method: str,
        base_confidence: float,
    ) -> float:
        """Calculate confidence score for extracted code"""
        confidence = base_confidence

        # Adjust based on content characteristics
        if len(content) < 10:
            confidence *= 0.8  # Very short content is less reliable
        elif len(content) > 1000:
            confidence *= 1.1  # Longer content is more likely to be actual code

        # Adjust based on language detection confidence
        if language != "text":
            detected_lang = self._detect_language(content)
            if detected_lang == language:
                confidence *= 1.1  # Language matches detection
            elif detected_lang:
                confidence *= 0.9  # Different language detected

        # Adjust based on extraction method reliability
        method_adjustments = {
            "triple_backtick": 1.0,
            "fenced_tilde": 1.0,
            "script_tag": 1.0,
            "html_code": 0.95,
            "single_backtick": 0.8,
            "indented_code": 0.7,
            "language_comment": 0.9,
        }

        confidence *= method_adjustments.get(extraction_method, 1.0)

        return min(1.0, max(0.0, confidence))

    def filter(
        self, extracted_codes: List[ExtractedCode], **criteria
    ) -> List[ExtractedCode]:
        """Filter extracted codes by various criteria"""
        logger.debug(
            f"Filtering {len(extracted_codes)} codes with criteria: {criteria}"
        )
        filtered = extracted_codes.copy()

        # Filter by language
        if "language" in criteria:
            lang = criteria["language"].lower()
            before_count = len(filtered)
            filtered = [code for code in filtered if code.language == lang]
            logger.debug(f"Language filter ({lang}): {before_count} -> {len(filtered)}")

        # Filter by source type
        if "source_type" in criteria:
            source = criteria["source_type"].lower()
            before_count = len(filtered)
            filtered = [code for code in filtered if code.source_type == source]
            logger.debug(
                f"Source type filter ({source}): {before_count} -> {len(filtered)}"
            )

        # Filter by extraction method
        if "extraction_method" in criteria:
            method = criteria["extraction_method"]
            before_count = len(filtered)
            filtered = [code for code in filtered if code.extraction_method == method]
            logger.debug(
                f"Extraction method filter ({method}): {before_count} -> {len(filtered)}"
            )

        # Filter by confidence threshold
        if "min_confidence" in criteria:
            min_conf = criteria["min_confidence"]
            before_count = len(filtered)
            filtered = [code for code in filtered if code.confidence >= min_conf]
            logger.debug(
                f"Min confidence filter ({min_conf}): {before_count} -> {len(filtered)}"
            )

        # Filter by content length
        if "min_length" in criteria:
            min_len = criteria["min_length"]
            before_count = len(filtered)
            filtered = [code for code in filtered if len(code.content) >= min_len]
            logger.debug(
                f"Min length filter ({min_len}): {before_count} -> {len(filtered)}"
            )

        if "max_length" in criteria:
            max_len = criteria["max_length"]
            before_count = len(filtered)
            filtered = [code for code in filtered if len(code.content) <= max_len]
            logger.debug(
                f"Max length filter ({max_len}): {before_count} -> {len(filtered)}"
            )

        # Filter by content contains
        if "contains" in criteria:
            search_term = criteria["contains"].lower()
            before_count = len(filtered)
            filtered = [
                code for code in filtered if search_term in code.content.lower()
            ]
            logger.debug(
                f"Contains filter ({search_term}): {before_count} -> {len(filtered)}"
            )

        # Filter by role (if available in context)
        if "role" in criteria:
            role = criteria["role"].lower()
            before_count = len(filtered)
            filtered = [
                code
                for code in filtered
                if code.context.get("role", "").lower() == role
            ]
            logger.debug(f"Role filter ({role}): {before_count} -> {len(filtered)}")

        logger.info(
            f"Filtering complete: {len(extracted_codes)} -> {len(filtered)} codes"
        )
        return filtered

    def get_statistics(self, extracted_codes: List[ExtractedCode]) -> Dict[str, Any]:
        """Get comprehensive statistics about extracted codes"""
        if not extracted_codes:
            return {"total": 0}

        stats = {
            "total": len(extracted_codes),
            "by_language": {},
            "by_source_type": {},
            "by_extraction_method": {},
            "confidence_stats": {
                "min": min(code.confidence for code in extracted_codes),
                "max": max(code.confidence for code in extracted_codes),
                "avg": sum(code.confidence for code in extracted_codes)
                / len(extracted_codes),
            },
            "content_length": {
                "min": min(len(code.content) for code in extracted_codes),
                "max": max(len(code.content) for code in extracted_codes),
                "avg": sum(len(code.content) for code in extracted_codes)
                / len(extracted_codes),
                "total": sum(len(code.content) for code in extracted_codes),
            },
            "high_confidence": len([c for c in extracted_codes if c.confidence >= 0.9]),
            "medium_confidence": len(
                [c for c in extracted_codes if 0.7 <= c.confidence < 0.9]
            ),
            "low_confidence": len([c for c in extracted_codes if c.confidence < 0.7]),
        }

        # Count by categories
        for code in extracted_codes:
            # By language
            lang = code.language
            stats["by_language"][lang] = stats["by_language"].get(lang, 0) + 1

            # By source type
            source = code.source_type
            stats["by_source_type"][source] = stats["by_source_type"].get(source, 0) + 1

            # By extraction method
            method = code.extraction_method
            stats["by_extraction_method"][method] = (
                stats["by_extraction_method"].get(method, 0) + 1
            )

        return stats

    def export(
        self,
        extracted_codes: List[ExtractedCode],
        output_format: str,
        output_path: str,
        include_metadata: bool = True,
    ):
        """Export extracted codes to various formats"""
        logger.info(
            f"Exporting {len(extracted_codes)} codes to {output_format} format at {output_path}"
        )
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        if output_format.lower() == "json":
            logger.debug("Exporting as JSON")
            data = [asdict(code) for code in extracted_codes]
            if not include_metadata:
                for item in data:
                    item.pop("metadata", None)

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

        elif output_format.lower() == "csv":
            logger.debug("Exporting as CSV")
            with open(output_path, "w", newline="", encoding="utf-8") as f:
                fieldnames = [
                    "language",
                    "source_type",
                    "extraction_method",
                    "confidence",
                    "content_length",
                    "content_preview",
                ]
                if include_metadata:
                    fieldnames.extend(["context", "metadata"])

                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()

                for code in extracted_codes:
                    row = {
                        "language": code.language,
                        "source_type": code.source_type,
                        "extraction_method": code.extraction_method,
                        "confidence": f"{code.confidence:.3f}",
                        "content_length": len(code.content),
                        "content_preview": code.content[:100].replace("\n", " "),
                    }

                    if include_metadata:
                        row["context"] = json.dumps(code.context)
                        row["metadata"] = json.dumps(code.metadata)

                    writer.writerow(row)

        elif output_format.lower() == "files":
            logger.debug("Exporting as individual files")
            # Save as individual files
            output_dir = Path(output_path)
            output_dir.mkdir(parents=True, exist_ok=True)

            language_counts = {}

            for code in extracted_codes:
                # Count for unique naming
                lang = code.language
                language_counts[lang] = language_counts.get(lang, 0) + 1

                # Get file extension
                ext = self._get_file_extension(lang)

                # Create filename
                confidence_str = f"{code.confidence:.2f}".replace(".", "_")
                filename = f"{lang}_{language_counts[lang]:03d}_{code.extraction_method}_{confidence_str}{ext}"

                # Save file
                file_path = output_dir / filename
                with open(file_path, "w", encoding="utf-8") as f:
                    if include_metadata:
                        f.write(f"# Extracted from: {code.source_type}\n")
                        f.write(f"# Method: {code.extraction_method}\n")
                        f.write(f"# Confidence: {code.confidence:.3f}\n")
                        f.write(f"# Language: {code.language}\n\n")
                    f.write(code.content)

                logger.info(f"Saved: {filename}")

        else:
            raise ValueError(f"Unsupported output format: {output_format}")

        logger.info(f"Export completed successfully")

    def _get_file_extension(self, language: str) -> str:
        """Get file extension for a programming language"""
        extensions = {
            "python": ".py",
            "py": ".py",
            "javascript": ".js",
            "js": ".js",
            "typescript": ".ts",
            "ts": ".ts",
            "html": ".html",
            "css": ".css",
            "svg": ".svg",
            "xml": ".xml",
            "json": ".json",
            "yaml": ".yaml",
            "sql": ".sql",
            "bash": ".sh",
            "powershell": ".ps1",
            "c": ".c",
            "cpp": ".cpp",
            "java": ".java",
            "csharp": ".cs",
            "cs": ".cs",
            "php": ".php",
            "ruby": ".rb",
            "go": ".go",
            "rust": ".rs",
            "swift": ".swift",
            "kotlin": ".kt",
            "scala": ".scala",
            "r": ".r",
            "matlab": ".m",
            "dockerfile": ".dockerfile",
            "makefile": ".makefile",
        }
        return extensions.get(language.lower(), ".txt")


def setup_logging(level: str = "INFO", format_string: Optional[str] = None) -> None:
    """Configure logging for the code extractor"""
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=format_string,
        handlers=[
            logging.StreamHandler(),  # Console output
        ],
    )


def main():
    """Command line interface"""
    parser = argparse.ArgumentParser(
        description="Generic Code Extractor - Extract code from any input format"
    )

    # Input options
    parser.add_argument("input", help="Input file or data")
    parser.add_argument(
        "--input-type",
        choices=["auto", "json", "text", "html", "xml", "markdown"],
        default="auto",
        help="Input type (auto-detect if not specified)",
    )

    # Extraction options
    parser.add_argument(
        "--patterns",
        nargs="+",
        choices=list(GenericCodeExtractor().extraction_patterns.keys()),
        help="Extraction patterns to use",
    )
    parser.add_argument(
        "--min-confidence", type=float, default=0.0, help="Minimum confidence threshold"
    )

    # Filtering options
    parser.add_argument("--language", help="Filter by programming language")
    parser.add_argument("--source-type", help="Filter by source type")
    parser.add_argument("--min-length", type=int, help="Minimum content length")
    parser.add_argument("--max-length", type=int, help="Maximum content length")
    parser.add_argument("--contains", help="Filter by content containing text")

    # Output options
    parser.add_argument("--output", default="extracted_code", help="Output path")
    parser.add_argument(
        "--format",
        choices=["files", "json", "csv"],
        default="files",
        help="Output format",
    )
    parser.add_argument(
        "--include-metadata",
        action="store_true",
        default=True,
        help="Include metadata in output",
    )
    parser.add_argument("--stats", action="store_true", help="Show statistics")

    # Logging options
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set the logging level",
    )
    parser.add_argument(
        "--quiet", "-q", action="store_true", help="Suppress all output except errors"
    )

    args = parser.parse_args()

    # Setup logging
    log_level = "ERROR" if args.quiet else args.log_level
    setup_logging(level=log_level)

    # Create extractor
    extractor = GenericCodeExtractor()

    # Read input
    try:
        if os.path.isfile(args.input):
            logger.debug(f"Reading input from file: {args.input}")
            with open(args.input, "r", encoding="utf-8") as f:
                input_data = f.read()
                # Try to parse as JSON first
                try:
                    input_data = json.loads(input_data)
                    logger.debug("Successfully parsed input as JSON")
                except:
                    logger.debug("Input is not valid JSON, treating as text")
                    pass  # Keep as string
        else:
            # Treat as direct input
            logger.debug("Using direct input data")
            input_data = args.input
            try:
                input_data = json.loads(input_data)
                logger.debug("Successfully parsed input as JSON")
            except:
                logger.debug("Input is not valid JSON, treating as text")
                pass
    except Exception as e:
        logger.error(f"Error reading input: {e}")
        return

    # Extract codes
    source_type = None if args.input_type == "auto" else args.input_type
    extracted_codes = extractor.extract(
        input_data,
        source_type=source_type,
        patterns=args.patterns,
        min_confidence=args.min_confidence,
    )

    # Apply filters
    filters = {}
    if args.language:
        filters["language"] = args.language
    if args.source_type:
        filters["source_type"] = args.source_type
    if args.min_length:
        filters["min_length"] = args.min_length
    if args.max_length:
        filters["max_length"] = args.max_length
    if args.contains:
        filters["contains"] = args.contains

    if filters:
        extracted_codes = extractor.filter(extracted_codes, **filters)

    logger.info(f"Found {len(extracted_codes)} code blocks")

    # Show statistics
    if args.stats:
        stats = extractor.get_statistics(extracted_codes)
        logger.info(f"\n📊 Statistics:")
        logger.info(f"Total: {stats['total']}")
        logger.info(f"Languages: {dict(sorted(stats['by_language'].items()))}")
        logger.info(f"Source types: {dict(sorted(stats['by_source_type'].items()))}")
        logger.info(
            f"Extraction methods: {dict(sorted(stats['by_extraction_method'].items()))}"
        )
        logger.info(
            f"Confidence - Min: {stats['confidence_stats']['min']:.3f}, "
            f"Max: {stats['confidence_stats']['max']:.3f}, "
            f"Avg: {stats['confidence_stats']['avg']:.3f}"
        )
        logger.info(f"High confidence (≥0.9): {stats['high_confidence']}")
        logger.info(f"Medium confidence (0.7-0.9): {stats['medium_confidence']}")
        logger.info(f"Low confidence (<0.7): {stats['low_confidence']}")

    # Export results
    if extracted_codes:
        extractor.export(
            extracted_codes,
            args.format,
            args.output,
            include_metadata=args.include_metadata,
        )
        logger.info(f"Results exported to: {args.output}")
    else:
        logger.warning("No code blocks found with the specified criteria.")


if __name__ == "__main__":
    main()
