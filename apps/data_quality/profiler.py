"""
Advanced Data Profiling and Quality Assessment

This module provides comprehensive data profiling capabilities:
- Statistical profiling and distribution analysis
- Data quality rule generation and validation
- Anomaly detection using ML techniques
- PySpark integration for big data processing
- LLM-powered quality insights and recommendations
"""

import json
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import hashlib
import statistics
from collections import Counter


class DataTypeEnum(Enum):
    """Enhanced data type classification"""

    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    TIMESTAMP = "timestamp"
    DECIMAL = "decimal"
    JSON = "json"
    ARRAY = "array"
    EMAIL = "email"
    PHONE = "phone"
    URL = "url"
    UUID = "uuid"
    IP_ADDRESS = "ip_address"
    CURRENCY = "currency"
    CATEGORICAL = "categorical"
    FREE_TEXT = "free_text"


class DQRuleTypeEnum(Enum):
    """Comprehensive data quality rule types"""

    COMPLETENESS = "completeness"
    UNIQUENESS = "uniqueness"
    VALIDITY = "validity"
    CONSISTENCY = "consistency"
    ACCURACY = "accuracy"
    TIMELINESS = "timeliness"
    REFERENTIAL_INTEGRITY = "referential_integrity"
    BUSINESS_RULES = "business_rules"
    CONFORMITY = "conformity"
    RANGE_CHECK = "range_check"
    FORMAT_CHECK = "format_check"
    PATTERN_MATCH = "pattern_match"
    STATISTICAL_OUTLIER = "statistical_outlier"
    FRESHNESS = "freshness"
    CUSTOM = "custom"


class QualityDimension(Enum):
    """Data quality dimensions"""

    ACCURACY = "accuracy"
    COMPLETENESS = "completeness"
    CONSISTENCY = "consistency"
    TIMELINESS = "timeliness"
    VALIDITY = "validity"
    UNIQUENESS = "uniqueness"


@dataclass
class StatisticalProfile:
    """Statistical profile for a column"""

    column_name: str
    data_type: DataTypeEnum
    total_count: int
    null_count: int
    unique_count: int
    duplicate_count: int

    # Numeric statistics
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    mean: Optional[float] = None
    median: Optional[float] = None
    mode: Optional[Union[int, float, str]] = None
    std_dev: Optional[float] = None
    variance: Optional[float] = None
    quartiles: Optional[Dict[str, float]] = None
    outliers: Optional[List[Any]] = None

    # String statistics
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    avg_length: Optional[float] = None
    common_patterns: Optional[List[Dict[str, Any]]] = None

    # Date/Time statistics
    earliest_date: Optional[str] = None
    latest_date: Optional[str] = None
    date_format: Optional[str] = None

    # Categorical statistics
    cardinality: Optional[int] = None
    top_values: Optional[List[Dict[str, Any]]] = None
    value_distribution: Optional[Dict[str, int]] = None

    # Quality metrics
    completeness_score: float = 0.0
    uniqueness_score: float = 0.0
    validity_score: float = 0.0
    consistency_score: float = 0.0

    # Recommendations
    quality_issues: List[str] = None
    recommended_rules: List[str] = None
    data_classification: Optional[str] = None


@dataclass
class DataQualityRule:
    """Enhanced data quality rule definition"""

    rule_id: str
    rule_name: str
    rule_type: DQRuleTypeEnum
    dimension: QualityDimension
    column_name: str
    description: str
    sql_expression: str
    pyspark_code: str
    python_code: str

    # Rule configuration
    threshold: Optional[float] = None
    severity: str = "MEDIUM"  # CRITICAL, HIGH, MEDIUM, LOW
    enabled: bool = True

    # Metadata
    business_context: str = ""
    error_message: str = ""
    suggested_action: str = ""
    business_impact: str = ""
    technical_details: str = ""

    # Execution
    expected_result: str = "PASS"  # PASS, FAIL, WARNING
    dependencies: List[str] = None
    execution_order: int = 0

    # Performance
    execution_time_ms: Optional[int] = None
    resource_usage: Optional[Dict[str, Any]] = None


@dataclass
class DataProfileReport:
    """Comprehensive data profiling report"""

    table_name: str
    schema_name: str
    database_name: str
    profiling_timestamp: str

    # Table-level statistics
    total_rows: int
    total_columns: int
    data_size_bytes: int

    # Column profiles
    column_profiles: List[StatisticalProfile]

    # Cross-column analysis
    correlations: Dict[str, Dict[str, float]]
    functional_dependencies: List[Dict[str, Any]]

    # Data quality assessment
    overall_quality_score: float
    quality_dimensions: Dict[QualityDimension, float]
    critical_issues: List[str]
    recommendations: List[str]

    # Generated rules
    suggested_rules: List[DataQualityRule]

    # Metadata
    profiling_config: Dict[str, Any]
    execution_time_seconds: float
    sample_size: int


class AdvancedDataProfiler:
    """Advanced data profiling engine with ML capabilities"""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.sample_size = self.config.get("sample_size", 10000)
        self.enable_ml_analysis = self.config.get("enable_ml", True)
        self.confidence_threshold = self.config.get("confidence_threshold", 0.8)

    async def profile_dataset(
        self, data: Union[pd.DataFrame, str], metadata: Dict[str, Any] = None
    ) -> DataProfileReport:
        """Profile a complete dataset with comprehensive analysis"""

        start_time = datetime.now()

        # Load data if string path provided
        if isinstance(data, str):
            data = self._load_data(data)

        # Sample data if too large
        if len(data) > self.sample_size:
            data = data.sample(n=self.sample_size, random_state=42)

        # Generate column profiles
        column_profiles = []
        for column in data.columns:
            profile = await self._profile_column(data[column], column)
            column_profiles.append(profile)

        # Cross-column analysis
        correlations = self._analyze_correlations(data)
        functional_deps = self._detect_functional_dependencies(data)

        # Overall quality assessment
        quality_scores = self._calculate_quality_scores(column_profiles)
        overall_score = self._calculate_overall_quality_score(quality_scores)

        # Generate recommendations
        critical_issues = self._identify_critical_issues(column_profiles)
        recommendations = self._generate_recommendations(
            column_profiles, quality_scores
        )

        # Generate DQ rules
        suggested_rules = await self._generate_quality_rules(column_profiles, data)

        execution_time = (datetime.now() - start_time).total_seconds()

        return DataProfileReport(
            table_name=metadata.get("table_name", "unknown_table"),
            schema_name=metadata.get("schema_name", "unknown_schema"),
            database_name=metadata.get("database_name", "unknown_database"),
            profiling_timestamp=datetime.now().isoformat(),
            total_rows=len(data),
            total_columns=len(data.columns),
            data_size_bytes=data.memory_usage(deep=True).sum(),
            column_profiles=column_profiles,
            correlations=correlations,
            functional_dependencies=functional_deps,
            overall_quality_score=overall_score,
            quality_dimensions=quality_scores,
            critical_issues=critical_issues,
            recommendations=recommendations,
            suggested_rules=suggested_rules,
            profiling_config=self.config,
            execution_time_seconds=execution_time,
            sample_size=len(data),
        )

    async def _profile_column(
        self, series: pd.Series, column_name: str
    ) -> StatisticalProfile:
        """Generate comprehensive profile for a single column"""

        # Detect data type
        data_type = self._detect_data_type(series)

        # Basic statistics
        total_count = len(series)
        null_count = series.isnull().sum()
        unique_count = series.nunique()
        duplicate_count = total_count - unique_count

        # Initialize profile
        profile = StatisticalProfile(
            column_name=column_name,
            data_type=data_type,
            total_count=total_count,
            null_count=null_count,
            unique_count=unique_count,
            duplicate_count=duplicate_count,
        )

        # Non-null data for detailed analysis
        non_null_series = series.dropna()

        if len(non_null_series) == 0:
            profile.completeness_score = 0.0
            profile.quality_issues = ["Column is completely empty"]
            return profile

        # Type-specific profiling
        if data_type in [
            DataTypeEnum.INTEGER,
            DataTypeEnum.FLOAT,
            DataTypeEnum.DECIMAL,
        ]:
            await self._profile_numeric_column(non_null_series, profile)
        elif data_type in [DataTypeEnum.STRING, DataTypeEnum.FREE_TEXT]:
            await self._profile_string_column(non_null_series, profile)
        elif data_type in [
            DataTypeEnum.DATE,
            DataTypeEnum.DATETIME,
            DataTypeEnum.TIMESTAMP,
        ]:
            await self._profile_datetime_column(non_null_series, profile)
        elif data_type == DataTypeEnum.CATEGORICAL:
            await self._profile_categorical_column(non_null_series, profile)

        # Calculate quality scores
        profile.completeness_score = (total_count - null_count) / total_count
        profile.uniqueness_score = (
            unique_count / total_count if total_count > 0 else 0.0
        )
        profile.validity_score = await self._calculate_validity_score(
            non_null_series, data_type
        )
        profile.consistency_score = await self._calculate_consistency_score(
            non_null_series, data_type
        )

        # Identify quality issues
        profile.quality_issues = await self._identify_column_issues(profile)
        profile.recommended_rules = await self._suggest_column_rules(profile)
        profile.data_classification = await self._classify_data_sensitivity(
            non_null_series, column_name
        )

        return profile

    async def _profile_numeric_column(
        self, series: pd.Series, profile: StatisticalProfile
    ):
        """Profile numeric column with statistical analysis"""
        try:
            # Convert to numeric, handling any string numbers
            numeric_series = pd.to_numeric(series, errors="coerce").dropna()

            if len(numeric_series) == 0:
                return

            # Basic statistics
            profile.min_value = float(numeric_series.min())
            profile.max_value = float(numeric_series.max())
            profile.mean = float(numeric_series.mean())
            profile.median = float(numeric_series.median())
            profile.std_dev = float(numeric_series.std())
            profile.variance = float(numeric_series.var())

            # Mode (most common value)
            mode_result = numeric_series.mode()
            if len(mode_result) > 0:
                profile.mode = float(mode_result.iloc[0])

            # Quartiles
            profile.quartiles = {
                "q1": float(numeric_series.quantile(0.25)),
                "q2": float(numeric_series.quantile(0.5)),
                "q3": float(numeric_series.quantile(0.75)),
            }

            # Outlier detection using IQR method
            q1 = profile.quartiles["q1"]
            q3 = profile.quartiles["q3"]
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr

            outliers = numeric_series[
                (numeric_series < lower_bound) | (numeric_series > upper_bound)
            ]
            profile.outliers = outliers.tolist()[:50]  # Limit outliers list

        except Exception as e:
            print(f"Error profiling numeric column {profile.column_name}: {e}")

    async def _profile_string_column(
        self, series: pd.Series, profile: StatisticalProfile
    ):
        """Profile string column with pattern analysis"""
        try:
            # Length statistics
            lengths = series.astype(str).str.len()
            profile.min_length = int(lengths.min())
            profile.max_length = int(lengths.max())
            profile.avg_length = float(lengths.mean())

            # Common patterns
            patterns = self._extract_string_patterns(series)
            profile.common_patterns = patterns[:10]  # Top 10 patterns

            # Value frequency
            value_counts = series.value_counts()
            profile.top_values = [
                {
                    "value": str(val),
                    "count": int(count),
                    "percentage": float(count / len(series) * 100),
                }
                for val, count in value_counts.head(10).items()
            ]

        except Exception as e:
            print(f"Error profiling string column {profile.column_name}: {e}")

    async def _profile_datetime_column(
        self, series: pd.Series, profile: StatisticalProfile
    ):
        """Profile datetime column"""
        try:
            # Convert to datetime
            dt_series = pd.to_datetime(series, errors="coerce").dropna()

            if len(dt_series) == 0:
                return

            profile.earliest_date = dt_series.min().isoformat()
            profile.latest_date = dt_series.max().isoformat()

            # Detect common date format
            sample_values = series.head(100).astype(str)
            profile.date_format = self._detect_date_format(sample_values)

        except Exception as e:
            print(f"Error profiling datetime column {profile.column_name}: {e}")

    async def _profile_categorical_column(
        self, series: pd.Series, profile: StatisticalProfile
    ):
        """Profile categorical column"""
        try:
            profile.cardinality = series.nunique()

            # Value distribution
            value_counts = series.value_counts()
            profile.value_distribution = value_counts.to_dict()

            # Top values
            profile.top_values = [
                {
                    "value": str(val),
                    "count": int(count),
                    "percentage": float(count / len(series) * 100),
                }
                for val, count in value_counts.head(20).items()
            ]

        except Exception as e:
            print(f"Error profiling categorical column {profile.column_name}: {e}")

    def _detect_data_type(self, series: pd.Series) -> DataTypeEnum:
        """Intelligent data type detection"""
        # Remove nulls for analysis
        non_null_series = series.dropna()

        if len(non_null_series) == 0:
            return DataTypeEnum.STRING

        # Sample for performance
        sample = non_null_series.sample(
            min(1000, len(non_null_series)), random_state=42
        )
        sample_str = sample.astype(str)

        # Check for specific patterns
        if self._is_email_pattern(sample_str):
            return DataTypeEnum.EMAIL
        elif self._is_phone_pattern(sample_str):
            return DataTypeEnum.PHONE
        elif self._is_url_pattern(sample_str):
            return DataTypeEnum.URL
        elif self._is_uuid_pattern(sample_str):
            return DataTypeEnum.UUID
        elif self._is_ip_pattern(sample_str):
            return DataTypeEnum.IP_ADDRESS
        elif self._is_currency_pattern(sample_str):
            return DataTypeEnum.CURRENCY

        # Check for datetime
        try:
            pd.to_datetime(sample, errors="raise")
            return DataTypeEnum.DATETIME
        except:
            pass

        # Check for numeric types
        try:
            numeric_sample = pd.to_numeric(sample, errors="raise")
            if all(numeric_sample == numeric_sample.astype(int)):
                return DataTypeEnum.INTEGER
            else:
                return DataTypeEnum.FLOAT
        except:
            pass

        # Check for boolean
        bool_values = {"true", "false", "1", "0", "yes", "no", "y", "n"}
        if set(sample_str.str.lower().unique()).issubset(bool_values):
            return DataTypeEnum.BOOLEAN

        # Check if categorical (low cardinality)
        cardinality_ratio = sample.nunique() / len(sample)
        if cardinality_ratio < 0.1 and sample.nunique() < 50:
            return DataTypeEnum.CATEGORICAL

        # Check for JSON
        if self._is_json_pattern(sample_str):
            return DataTypeEnum.JSON

        # Default to string or free text
        avg_length = sample_str.str.len().mean()
        if avg_length > 100:  # Arbitrary threshold for free text
            return DataTypeEnum.FREE_TEXT

        return DataTypeEnum.STRING

    def _is_email_pattern(self, series: pd.Series) -> bool:
        """Check if series contains email addresses"""
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return series.str.match(email_pattern).sum() / len(series) > 0.8

    def _is_phone_pattern(self, series: pd.Series) -> bool:
        """Check if series contains phone numbers"""
        phone_patterns = [
            r"^\+?1?[0-9]{10,15}$",
            r"^\([0-9]{3}\)[0-9]{3}-[0-9]{4}$",
            r"^[0-9]{3}-[0-9]{3}-[0-9]{4}$",
        ]
        for pattern in phone_patterns:
            if series.str.match(pattern).sum() / len(series) > 0.8:
                return True
        return False

    def _is_url_pattern(self, series: pd.Series) -> bool:
        """Check if series contains URLs"""
        url_pattern = r"^https?://[^\s/$.?#].[^\s]*$"
        return series.str.match(url_pattern).sum() / len(series) > 0.8

    def _is_uuid_pattern(self, series: pd.Series) -> bool:
        """Check if series contains UUIDs"""
        uuid_pattern = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
        return series.str.match(uuid_pattern, case=False).sum() / len(series) > 0.8

    def _is_ip_pattern(self, series: pd.Series) -> bool:
        """Check if series contains IP addresses"""
        ip_pattern = r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$"
        return series.str.match(ip_pattern).sum() / len(series) > 0.8

    def _is_currency_pattern(self, series: pd.Series) -> bool:
        """Check if series contains currency values"""
        currency_pattern = r"^[\$£€¥]?[0-9,]+\.?[0-9]*$"
        return series.str.match(currency_pattern).sum() / len(series) > 0.8

    def _is_json_pattern(self, series: pd.Series) -> bool:
        """Check if series contains JSON strings"""
        json_count = 0
        for value in series.head(100):  # Sample for performance
            try:
                json.loads(str(value))
                json_count += 1
            except:
                pass
        return json_count / min(100, len(series)) > 0.8

    def _extract_string_patterns(self, series: pd.Series) -> List[Dict[str, Any]]:
        """Extract common string patterns"""
        patterns = []
        sample = series.head(1000).astype(str)  # Sample for performance

        # Simple pattern extraction (could be enhanced with regex learning)
        pattern_counter = Counter()

        for value in sample:
            # Create a simple pattern by replacing digits and letters
            pattern = ""
            for char in value:
                if char.isdigit():
                    pattern += "9"
                elif char.isalpha():
                    pattern += "A"
                else:
                    pattern += char
            pattern_counter[pattern] += 1

        # Convert to list of dicts
        for pattern, count in pattern_counter.most_common(10):
            patterns.append(
                {
                    "pattern": pattern,
                    "count": count,
                    "percentage": count / len(sample) * 100,
                    "example": next(
                        (val for val in sample if self._matches_pattern(val, pattern)),
                        "",
                    ),
                }
            )

        return patterns

    def _matches_pattern(self, value: str, pattern: str) -> bool:
        """Check if value matches the simple pattern"""
        if len(value) != len(pattern):
            return False

        for v_char, p_char in zip(value, pattern):
            if p_char == "9" and not v_char.isdigit():
                return False
            elif p_char == "A" and not v_char.isalpha():
                return False
            elif p_char not in ["9", "A"] and v_char != p_char:
                return False

        return True

    def _detect_date_format(self, sample_values: pd.Series) -> Optional[str]:
        """Detect common date format"""
        common_formats = [
            "%Y-%m-%d",
            "%m/%d/%Y",
            "%d/%m/%Y",
            "%Y-%m-%d %H:%M:%S",
            "%m/%d/%Y %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S",
        ]

        for fmt in common_formats:
            try:
                parsed_count = 0
                for value in sample_values.head(50):
                    try:
                        datetime.strptime(str(value), fmt)
                        parsed_count += 1
                    except:
                        pass

                if parsed_count / min(50, len(sample_values)) > 0.8:
                    return fmt
            except:
                continue

        return None

    async def _calculate_validity_score(
        self, series: pd.Series, data_type: DataTypeEnum
    ) -> float:
        """Calculate validity score based on data type expectations"""
        valid_count = 0
        total_count = len(series)

        if total_count == 0:
            return 0.0

        for value in series:
            if self._is_valid_for_type(value, data_type):
                valid_count += 1

        return valid_count / total_count

    def _is_valid_for_type(self, value: Any, data_type: DataTypeEnum) -> bool:
        """Check if value is valid for the specified data type"""
        try:
            str_value = str(value)

            if data_type == DataTypeEnum.EMAIL:
                import re

                return bool(
                    re.match(
                        r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", str_value
                    )
                )
            elif data_type == DataTypeEnum.PHONE:
                # Simple phone validation
                digits_only = "".join(filter(str.isdigit, str_value))
                return 10 <= len(digits_only) <= 15
            elif data_type == DataTypeEnum.URL:
                return str_value.startswith(("http://", "https://"))
            elif data_type in [DataTypeEnum.INTEGER, DataTypeEnum.FLOAT]:
                float(str_value)
                return True
            elif data_type == DataTypeEnum.DATE:
                pd.to_datetime(str_value)
                return True
            else:
                return True  # Default to valid for other types

        except:
            return False

    async def _calculate_consistency_score(
        self, series: pd.Series, data_type: DataTypeEnum
    ) -> float:
        """Calculate consistency score (format consistency)"""
        if len(series) <= 1:
            return 1.0

        # For string types, check format consistency
        if data_type in [DataTypeEnum.STRING, DataTypeEnum.EMAIL, DataTypeEnum.PHONE]:
            patterns = self._extract_string_patterns(series)
            if patterns:
                # Calculate how consistent the most common pattern is
                top_pattern_percentage = patterns[0]["percentage"]
                return top_pattern_percentage / 100.0

        # For numeric types, check for consistent decimal places
        elif data_type in [DataTypeEnum.FLOAT, DataTypeEnum.DECIMAL]:
            decimal_places = []
            for value in series.head(100):  # Sample for performance
                try:
                    str_val = str(float(value))
                    if "." in str_val:
                        decimal_places.append(len(str_val.split(".")[1]))
                    else:
                        decimal_places.append(0)
                except:
                    pass

            if decimal_places:
                most_common_places = Counter(decimal_places).most_common(1)[0][1]
                return most_common_places / len(decimal_places)

        return 0.8  # Default consistency score

    def _analyze_correlations(self, data: pd.DataFrame) -> Dict[str, Dict[str, float]]:
        """Analyze correlations between numeric columns"""
        numeric_columns = data.select_dtypes(include=[np.number]).columns

        if len(numeric_columns) < 2:
            return {}

        corr_matrix = data[numeric_columns].corr()

        # Convert to nested dict format
        correlations = {}
        for col1 in numeric_columns:
            correlations[col1] = {}
            for col2 in numeric_columns:
                if col1 != col2:
                    correlations[col1][col2] = float(corr_matrix.loc[col1, col2])

        return correlations

    def _detect_functional_dependencies(
        self, data: pd.DataFrame
    ) -> List[Dict[str, Any]]:
        """Detect potential functional dependencies"""
        dependencies = []

        # Simple heuristic: if column A determines column B,
        # then for each value of A, there should be only one value of B

        for col_a in data.columns:
            for col_b in data.columns:
                if col_a != col_b:
                    # Group by col_a and check unique values in col_b
                    grouped = data.groupby(col_a)[col_b].nunique()

                    # If all groups have only 1 unique value, it's a functional dependency
                    if (grouped == 1).all() and len(grouped) > 1:
                        confidence = 1.0
                        dependencies.append(
                            {
                                "determinant": col_a,
                                "dependent": col_b,
                                "confidence": confidence,
                                "type": "functional_dependency",
                            }
                        )

        return dependencies

    def _calculate_quality_scores(
        self, column_profiles: List[StatisticalProfile]
    ) -> Dict[QualityDimension, float]:
        """Calculate overall quality scores by dimension"""
        if not column_profiles:
            return {dim: 0.0 for dim in QualityDimension}

        scores = {
            QualityDimension.COMPLETENESS: np.mean(
                [p.completeness_score for p in column_profiles]
            ),
            QualityDimension.UNIQUENESS: np.mean(
                [p.uniqueness_score for p in column_profiles]
            ),
            QualityDimension.VALIDITY: np.mean(
                [p.validity_score for p in column_profiles]
            ),
            QualityDimension.CONSISTENCY: np.mean(
                [p.consistency_score for p in column_profiles]
            ),
            QualityDimension.ACCURACY: 0.8,  # Placeholder - would need reference data
            QualityDimension.TIMELINESS: 0.8,  # Placeholder - would need time analysis
        }

        return scores

    def _calculate_overall_quality_score(
        self, quality_scores: Dict[QualityDimension, float]
    ) -> float:
        """Calculate weighted overall quality score"""
        weights = {
            QualityDimension.COMPLETENESS: 0.25,
            QualityDimension.VALIDITY: 0.25,
            QualityDimension.CONSISTENCY: 0.20,
            QualityDimension.UNIQUENESS: 0.15,
            QualityDimension.ACCURACY: 0.10,
            QualityDimension.TIMELINESS: 0.05,
        }

        weighted_score = sum(
            quality_scores[dim] * weights[dim] for dim in QualityDimension
        )

        return weighted_score

    def _identify_critical_issues(
        self, column_profiles: List[StatisticalProfile]
    ) -> List[str]:
        """Identify critical data quality issues"""
        critical_issues = []

        for profile in column_profiles:
            # High null percentage
            if profile.completeness_score < 0.5:
                critical_issues.append(
                    f"Column '{profile.column_name}' has {profile.null_count}/{profile.total_count} "
                    f"null values ({(1-profile.completeness_score)*100:.1f}%)"
                )

            # Low validity
            if profile.validity_score < 0.8:
                critical_issues.append(
                    f"Column '{profile.column_name}' has validity issues "
                    f"(score: {profile.validity_score:.2f})"
                )

            # Potential PII without encryption
            if profile.data_classification in ["PII", "SENSITIVE"]:
                critical_issues.append(
                    f"Column '{profile.column_name}' may contain {profile.data_classification} "
                    f"data and should be reviewed for privacy compliance"
                )

        return critical_issues

    def _generate_recommendations(
        self,
        column_profiles: List[StatisticalProfile],
        quality_scores: Dict[QualityDimension, float],
    ) -> List[str]:
        """Generate data quality improvement recommendations"""
        recommendations = []

        # Overall recommendations
        if quality_scores[QualityDimension.COMPLETENESS] < 0.8:
            recommendations.append(
                "Implement data validation rules to reduce null values"
            )

        if quality_scores[QualityDimension.CONSISTENCY] < 0.8:
            recommendations.append(
                "Standardize data formats and implement format validation"
            )

        # Column-specific recommendations
        for profile in column_profiles:
            if profile.quality_issues:
                recommendations.extend(
                    [
                        f"Address {profile.column_name}: {issue}"
                        for issue in profile.quality_issues[:3]  # Limit recommendations
                    ]
                )

        return recommendations[:10]  # Limit total recommendations

    async def _generate_quality_rules(
        self, column_profiles: List[StatisticalProfile], data: pd.DataFrame
    ) -> List[DataQualityRule]:
        """Generate data quality rules based on profiling results"""
        rules = []

        for profile in column_profiles:
            column_name = profile.column_name

            # Completeness rule
            if profile.null_count > 0:
                rules.append(
                    DataQualityRule(
                        rule_id=f"completeness_{column_name}",
                        rule_name=f"Completeness check for {column_name}",
                        rule_type=DQRuleTypeEnum.COMPLETENESS,
                        dimension=QualityDimension.COMPLETENESS,
                        column_name=column_name,
                        description=f"Check that {column_name} is not null",
                        sql_expression=f"SELECT COUNT(*) FROM table WHERE {column_name} IS NULL",
                        pyspark_code=f"df.filter(col('{column_name}').isNull()).count()",
                        python_code=f"data['{column_name}'].isnull().sum()",
                        threshold=0.0,
                        severity=(
                            "HIGH" if profile.completeness_score < 0.5 else "MEDIUM"
                        ),
                        business_context=f"Null values in {column_name} may indicate data collection issues",
                        error_message=f"Found null values in {column_name}",
                        suggested_action="Investigate data source and implement validation",
                    )
                )

            # Uniqueness rule for potential keys
            if profile.uniqueness_score > 0.95:
                rules.append(
                    DataQualityRule(
                        rule_id=f"uniqueness_{column_name}",
                        rule_name=f"Uniqueness check for {column_name}",
                        rule_type=DQRuleTypeEnum.UNIQUENESS,
                        dimension=QualityDimension.UNIQUENESS,
                        column_name=column_name,
                        description=f"Check that {column_name} values are unique",
                        sql_expression=f"SELECT {column_name}, COUNT(*) FROM table GROUP BY {column_name} HAVING COUNT(*) > 1",
                        pyspark_code=f"df.groupBy('{column_name}').count().filter(col('count') > 1)",
                        python_code=f"data['{column_name}'].duplicated().sum()",
                        threshold=0.0,
                        severity="HIGH",
                        business_context=f"{column_name} appears to be a unique identifier",
                        error_message=f"Found duplicate values in {column_name}",
                        suggested_action="Ensure uniqueness constraints are enforced",
                    )
                )

            # Range checks for numeric columns
            if profile.data_type in [DataTypeEnum.INTEGER, DataTypeEnum.FLOAT]:
                if profile.min_value is not None and profile.max_value is not None:
                    rules.append(
                        DataQualityRule(
                            rule_id=f"range_{column_name}",
                            rule_name=f"Range check for {column_name}",
                            rule_type=DQRuleTypeEnum.RANGE_CHECK,
                            dimension=QualityDimension.VALIDITY,
                            column_name=column_name,
                            description=f"Check that {column_name} is within expected range",
                            sql_expression=f"SELECT COUNT(*) FROM table WHERE {column_name} < {profile.min_value} OR {column_name} > {profile.max_value}",
                            pyspark_code=f"df.filter((col('{column_name}') < {profile.min_value}) | (col('{column_name}') > {profile.max_value})).count()",
                            python_code=f"((data['{column_name}'] < {profile.min_value}) | (data['{column_name}'] > {profile.max_value})).sum()",
                            threshold=0.05,  # Allow 5% outliers
                            severity="MEDIUM",
                            business_context=f"Values outside normal range may indicate data quality issues",
                            error_message=f"Found values outside expected range in {column_name}",
                            suggested_action="Review outliers and validate data collection process",
                        )
                    )

            # Format validation for specific data types
            if profile.data_type == DataTypeEnum.EMAIL:
                rules.append(
                    DataQualityRule(
                        rule_id=f"email_format_{column_name}",
                        rule_name=f"Email format validation for {column_name}",
                        rule_type=DQRuleTypeEnum.FORMAT_CHECK,
                        dimension=QualityDimension.VALIDITY,
                        column_name=column_name,
                        description=f"Check that {column_name} contains valid email addresses",
                        sql_expression=f"SELECT COUNT(*) FROM table WHERE {column_name} NOT REGEXP '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{{2,}}$'",
                        pyspark_code=f"df.filter(~col('{column_name}').rlike('^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\\\.[a-zA-Z]{{2,}}$')).count()",
                        python_code=f"~data['{column_name}'].str.match('^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{{2,}}$').sum()",
                        threshold=0.0,
                        severity="HIGH",
                        business_context="Invalid email addresses can cause communication failures",
                        error_message=f"Found invalid email addresses in {column_name}",
                        suggested_action="Implement email validation at data entry point",
                    )
                )

        return rules

    async def _identify_column_issues(self, profile: StatisticalProfile) -> List[str]:
        """Identify specific issues for a column"""
        issues = []

        # Completeness issues
        if profile.completeness_score < 0.9:
            issues.append(f"High null rate: {(1-profile.completeness_score)*100:.1f}%")

        # Validity issues
        if profile.validity_score < 0.95:
            issues.append(
                f"Invalid values detected: {(1-profile.validity_score)*100:.1f}%"
            )

        # Consistency issues
        if profile.consistency_score < 0.8:
            issues.append("Inconsistent format patterns detected")

        # Outliers for numeric columns
        if profile.outliers and len(profile.outliers) > 0:
            outlier_percentage = len(profile.outliers) / profile.total_count * 100
            if outlier_percentage > 5:
                issues.append(f"High outlier rate: {outlier_percentage:.1f}%")

        # Low cardinality issues
        if profile.data_type in [DataTypeEnum.STRING, DataTypeEnum.CATEGORICAL]:
            if profile.unique_count == 1:
                issues.append("All values are identical")
            elif profile.unique_count / profile.total_count < 0.01:
                issues.append(
                    "Very low cardinality - consider if this should be categorical"
                )

        return issues

    async def _suggest_column_rules(self, profile: StatisticalProfile) -> List[str]:
        """Suggest DQ rules for a column"""
        suggestions = []

        # Always suggest completeness check
        if profile.null_count > 0:
            suggestions.append("Implement NOT NULL constraint")

        # Uniqueness suggestions
        if profile.uniqueness_score > 0.95:
            suggestions.append("Consider adding UNIQUE constraint")

        # Type-specific suggestions
        if profile.data_type == DataTypeEnum.EMAIL:
            suggestions.append("Add email format validation")
        elif profile.data_type == DataTypeEnum.PHONE:
            suggestions.append("Add phone number format validation")
        elif profile.data_type in [DataTypeEnum.INTEGER, DataTypeEnum.FLOAT]:
            suggestions.append("Add range validation based on business rules")
            if profile.outliers:
                suggestions.append("Review and handle outliers")

        return suggestions

    async def _classify_data_sensitivity(
        self, series: pd.Series, column_name: str
    ) -> Optional[str]:
        """Classify data sensitivity level"""
        # Simple heuristic-based classification
        column_lower = column_name.lower()

        # Check for PII indicators
        pii_indicators = [
            "ssn",
            "social",
            "phone",
            "email",
            "address",
            "name",
            "birth",
            "age",
        ]
        sensitive_indicators = [
            "salary",
            "income",
            "password",
            "secret",
            "key",
            "token",
        ]

        if any(indicator in column_lower for indicator in pii_indicators):
            return "PII"
        elif any(indicator in column_lower for indicator in sensitive_indicators):
            return "SENSITIVE"
        elif profile.data_type == DataTypeEnum.EMAIL:
            return "PII"
        elif profile.data_type == DataTypeEnum.PHONE:
            return "PII"

        return "PUBLIC"

    def _load_data(self, data_path: str) -> pd.DataFrame:
        """Load data from various file formats"""
        if data_path.endswith(".csv"):
            return pd.read_csv(data_path)
        elif data_path.endswith(".json"):
            return pd.read_json(data_path)
        elif data_path.endswith(".parquet"):
            return pd.read_parquet(data_path)
        else:
            raise ValueError(f"Unsupported file format: {data_path}")
