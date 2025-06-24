"""
PySpark Code Generator for Data Quality

This module generates PySpark code for data quality validation and processing:
- DQ rule implementation in PySpark
- Data profiling jobs
- Anomaly detection algorithms
- Data cleaning and transformation pipelines
- Performance-optimized big data processing
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
from .profiler import (
    DataQualityRule,
    DQRuleTypeEnum,
    QualityDimension,
    StatisticalProfile,
)
import json


class SparkJobType(Enum):
    """Types of Spark jobs to generate"""

    PROFILING = "profiling"
    VALIDATION = "validation"
    CLEANING = "cleaning"
    ANOMALY_DETECTION = "anomaly_detection"
    QUALITY_MONITORING = "quality_monitoring"
    DATA_LINEAGE = "data_lineage"


@dataclass
class SparkJobConfig:
    """Configuration for Spark job generation"""

    job_type: SparkJobType
    input_format: str = "parquet"  # parquet, delta, csv, json
    output_format: str = "parquet"
    partitioning_columns: List[str] = None
    enable_caching: bool = True
    enable_checkpointing: bool = False
    parallelism_level: str = "medium"  # low, medium, high
    memory_optimization: bool = True
    broadcast_threshold: str = "10MB"

    # Quality-specific config
    quality_threshold: float = 0.8
    error_handling: str = "quarantine"  # fail, skip, quarantine
    enable_data_lineage: bool = False
    enable_metrics_collection: bool = True


class PySparkCodeGenerator:
    """Generates optimized PySpark code for data quality operations"""

    def __init__(self, config: SparkJobConfig):
        self.config = config

    def generate_profiling_job(
        self, table_metadata: Dict[str, Any], columns_to_profile: List[str] = None
    ) -> str:
        """Generate comprehensive data profiling job"""

        job_code = f'''
"""
Data Profiling Job
Generated for table: {table_metadata.get("table_name", "unknown")}
Purpose: Comprehensive statistical profiling and quality assessment
"""

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import *
from pyspark.sql.types import *
import pyspark.sql.functions as F
from datetime import datetime
import json

# Initialize Spark session with optimized configuration
spark = SparkSession.builder \\
    .appName("DataProfiling_{table_metadata.get("table_name", "table")}") \\
    .config("spark.sql.adaptive.enabled", "true") \\
    .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \\
    .config("spark.sql.adaptive.skewJoin.enabled", "true") \\
    .config("spark.sql.execution.arrow.pyspark.enabled", "true") \\
    .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \\
    .config("spark.sql.parquet.enableVectorizedReader", "true") \\
    .getOrCreate()

# Set logging level
spark.sparkContext.setLogLevel("WARN")

def load_data(input_path: str) -> DataFrame:
    """Load data with format detection and optimization"""
    try:
        if "{self.config.input_format}" == "parquet":
            df = spark.read.parquet(input_path)
        elif "{self.config.input_format}" == "delta":
            df = spark.read.format("delta").load(input_path)
        elif "{self.config.input_format}" == "csv":
            df = spark.read.option("header", "true").option("inferSchema", "true").csv(input_path)
        elif "{self.config.input_format}" == "json":
            df = spark.read.json(input_path)
        else:
            raise ValueError(f"Unsupported format: {self.config.input_format}")
        
        print(f"Loaded {{df.count()}} rows with {{len(df.columns)}} columns")
        return df
        
    except Exception as e:
        print(f"Error loading data: {{e}}")
        raise

def profile_table_statistics(df: DataFrame) -> Dict[str, Any]:
    """Generate table-level statistics"""
    stats = {{}}
    
    # Basic counts
    total_rows = df.count()
    total_columns = len(df.columns)
    
    # Estimate data size
    df_sample = df.sample(0.1, seed=42)  # 10% sample for estimation
    sample_size = df_sample.count()
    estimated_size_mb = (sample_size * len(df.columns) * 8) / (1024 * 1024) * 10  # Rough estimation
    
    stats.update({{
        "total_rows": total_rows,
        "total_columns": total_columns,
        "estimated_size_mb": estimated_size_mb,
        "partitions": df.rdd.getNumPartitions(),
        "profiling_timestamp": datetime.now().isoformat()
    }})
    
    return stats

def profile_column_statistics(df: DataFrame, column_name: str) -> Dict[str, Any]:
    """Generate comprehensive column statistics"""
    column_stats = {{}}
    
    try:
        # Get column data type
        column_type = dict(df.dtypes)[column_name]
        column_stats["data_type"] = column_type
        
        # Basic statistics
        total_count = df.count()
        null_count = df.filter(col(column_name).isNull()).count()
        unique_count = df.select(column_name).distinct().count()
        
        column_stats.update({{
            "total_count": total_count,
            "null_count": null_count,
            "null_percentage": (null_count / total_count * 100) if total_count > 0 else 0,
            "unique_count": unique_count,
            "uniqueness_percentage": (unique_count / total_count * 100) if total_count > 0 else 0
        }})
        
        # Type-specific statistics
        if column_type in ["int", "bigint", "double", "float", "decimal"]:
            # Numeric statistics
            numeric_stats = df.select(
                min(col(column_name)).alias("min_value"),
                max(col(column_name)).alias("max_value"),
                mean(col(column_name)).alias("mean_value"),
                stddev(col(column_name)).alias("std_dev"),
                expr(f"percentile_approx(`{{column_name}}`, 0.25)").alias("q1"),
                expr(f"percentile_approx(`{{column_name}}`, 0.5)").alias("median"),
                expr(f"percentile_approx(`{{column_name}}`, 0.75)").alias("q3")
            ).collect()[0]
            
            column_stats.update({{
                "min_value": numeric_stats["min_value"],
                "max_value": numeric_stats["max_value"],
                "mean_value": numeric_stats["mean_value"],
                "std_dev": numeric_stats["std_dev"],
                "median": numeric_stats["median"],
                "q1": numeric_stats["q1"],
                "q3": numeric_stats["q3"]
            }})
            
            # Outlier detection using IQR
            q1 = numeric_stats["q1"]
            q3 = numeric_stats["q3"]
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            
            outlier_count = df.filter(
                (col(column_name) < lower_bound) | (col(column_name) > upper_bound)
            ).count()
            
            column_stats["outlier_count"] = outlier_count
            column_stats["outlier_percentage"] = (outlier_count / total_count * 100) if total_count > 0 else 0
            
        elif column_type in ["string", "varchar"]:
            # String statistics
            string_stats = df.select(
                min(length(col(column_name))).alias("min_length"),
                max(length(col(column_name))).alias("max_length"),
                avg(length(col(column_name))).alias("avg_length")
            ).collect()[0]
            
            column_stats.update({{
                "min_length": string_stats["min_length"],
                "max_length": string_stats["max_length"],
                "avg_length": string_stats["avg_length"]
            }})
            
            # Top values
            top_values = df.groupBy(column_name) \\
                .count() \\
                .orderBy(desc("count")) \\
                .limit(10) \\
                .collect()
            
            column_stats["top_values"] = [
                {{"value": row[column_name], "count": row["count"]}}
                for row in top_values
            ]
            
        # Pattern analysis for strings
        if column_type in ["string", "varchar"]:
            # Check for common patterns
            patterns_analysis = {{
                "contains_email": df.filter(col(column_name).rlike(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{{2,}}$")).count(),
                "contains_phone": df.filter(col(column_name).rlike(r"^\\+?[0-9{{10,15}}]$")).count(),
                "contains_url": df.filter(col(column_name).rlike(r"^https?://")).count(),
                "contains_uuid": df.filter(col(column_name).rlike(r"^[0-9a-f]{{8}}-[0-9a-f]{{4}}-[0-9a-f]{{4}}-[0-9a-f]{{4}}-[0-9a-f]{{12}}$")).count(),
                "all_numeric": df.filter(col(column_name).rlike(r"^[0-9]+$")).count(),
                "all_alpha": df.filter(col(column_name).rlike(r"^[a-zA-Z]+$")).count()
            }}
            
            column_stats["pattern_analysis"] = patterns_analysis
        
    except Exception as e:
        column_stats["error"] = str(e)
        print(f"Error profiling column {{column_name}}: {{e}}")
    
    return column_stats

def detect_data_types(df: DataFrame) -> Dict[str, str]:
    """Enhanced data type detection"""
    type_suggestions = {{}}
    
    for column_name, current_type in df.dtypes:
        if current_type == "string":
            # Sample data for type inference
            sample_data = df.select(column_name).filter(col(column_name).isNotNull()).limit(1000).collect()
            
            if len(sample_data) > 0:
                # Check if all values can be converted to numeric
                try:
                    numeric_count = df.filter(col(column_name).cast("double").isNotNull()).count()
                    total_non_null = df.filter(col(column_name).isNotNull()).count()
                    
                    if numeric_count == total_non_null and total_non_null > 0:
                        # Check if integers
                        decimal_count = df.filter(col(column_name).contains(".")).count()
                        if decimal_count == 0:
                            type_suggestions[column_name] = "integer"
                        else:
                            type_suggestions[column_name] = "double"
                    else:
                        # Check for date patterns
                        date_patterns = [
                            r"^\\d{{4}}-\\d{{2}}-\\d{{2}}$",  # YYYY-MM-DD
                            r"^\\d{{2}}/\\d{{2}}/\\d{{4}}$",  # MM/DD/YYYY
                            r"^\\d{{4}}-\\d{{2}}-\\d{{2}} \\d{{2}}:\\d{{2}}:\\d{{2}}$"  # YYYY-MM-DD HH:MM:SS
                        ]
                        
                        for pattern in date_patterns:
                            date_count = df.filter(col(column_name).rlike(pattern)).count()
                            if date_count == total_non_null and total_non_null > 0:
                                type_suggestions[column_name] = "timestamp"
                                break
                        else:
                            type_suggestions[column_name] = "string"
                            
                except Exception:
                    type_suggestions[column_name] = "string"
            else:
                type_suggestions[column_name] = current_type
        else:
            type_suggestions[column_name] = current_type
    
    return type_suggestions

def main(input_path: str, output_path: str):
    """Main profiling function"""
    try:
        # Load data
        print("Loading data...")
        df = load_data(input_path)
        
        {"df.cache()" if self.config.enable_caching else "# Caching disabled"}
        
        # Table-level statistics
        print("Generating table statistics...")
        table_stats = profile_table_statistics(df)
        
        # Column-level statistics
        print("Generating column statistics...")
        columns_to_analyze = {columns_to_profile or "df.columns"}
        column_statistics = {{}}
        
        for column_name in columns_to_analyze:
            print(f"Profiling column: {{column_name}}")
            column_stats = profile_column_statistics(df, column_name)
            column_statistics[column_name] = column_stats
        
        # Data type suggestions
        print("Analyzing data types...")
        type_suggestions = detect_data_types(df)
        
        # Compile final report
        profiling_report = {{
            "table_statistics": table_stats,
            "column_statistics": column_statistics,
            "type_suggestions": type_suggestions,
            "profiling_metadata": {{
                "input_path": input_path,
                "output_path": output_path,
                "spark_version": spark.version,
                "profiling_timestamp": datetime.now().isoformat()
            }}
        }}
        
        # Save results
        print("Saving profiling results...")
        
        # Convert to DataFrame and save as JSON
        report_df = spark.createDataFrame([profiling_report])
        report_df.coalesce(1).write.mode("overwrite").json(f"{{output_path}}/profiling_report")
        
        # Also save column statistics as a structured table
        column_stats_data = []
        for col_name, stats in column_statistics.items():
            stats["column_name"] = col_name
            column_stats_data.append(stats)
        
        if column_stats_data:
            column_stats_df = spark.createDataFrame(column_stats_data)
            column_stats_df.write.mode("overwrite").{self.config.output_format}(f"{{output_path}}/column_statistics")
        
        print("Profiling completed successfully!")
        print(f"Results saved to: {{output_path}}")
        
        # Print summary
        print("\\n=== PROFILING SUMMARY ===")
        print(f"Total rows: {{table_stats['total_rows']:,}}")
        print(f"Total columns: {{table_stats['total_columns']}}")
        print(f"Estimated size: {{table_stats['estimated_size_mb']:.2f}} MB")
        
        quality_issues = []
        for col_name, stats in column_statistics.items():
            null_pct = stats.get("null_percentage", 0)
            if null_pct > 10:
                quality_issues.append(f"{{col_name}}: {{null_pct:.1f}}% null values")
        
        if quality_issues:
            print("\\nQuality Issues Found:")
            for issue in quality_issues[:5]:  # Show top 5 issues
                print(f"  - {{issue}}")
        
        return profiling_report
        
    except Exception as e:
        print(f"Profiling job failed: {{e}}")
        raise
    finally:
        if {"'spark' in locals()" if self.config.enable_caching else "False"}:
            df.unpersist()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 3:
        print("Usage: python profiling_job.py <input_path> <output_path>")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    
    main(input_path, output_path)
'''

        return job_code

    def generate_validation_job(
        self, rules: List[DataQualityRule], table_metadata: Dict[str, Any]
    ) -> str:
        """Generate data quality validation job"""

        # Convert rules to Spark code
        rule_implementations = []
        for rule in rules:
            rule_code = self._generate_rule_implementation(rule)
            rule_implementations.append(rule_code)

        job_code = f'''
"""
Data Quality Validation Job
Generated for table: {table_metadata.get("table_name", "unknown")}
Purpose: Execute data quality rules and generate quality report
"""

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import *
from pyspark.sql.types import *
import pyspark.sql.functions as F
from datetime import datetime
import json

# Initialize Spark session
spark = SparkSession.builder \\
    .appName("DataValidation_{table_metadata.get("table_name", "table")}") \\
    .config("spark.sql.adaptive.enabled", "true") \\
    .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \\
    .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \\
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

class DataQualityValidator:
    """Data quality validation engine"""
    
    def __init__(self, df: DataFrame):
        self.df = df
        self.validation_results = []
        self.error_records = []
        
    def run_all_validations(self) -> Dict[str, Any]:
        """Execute all data quality rules"""
        total_records = self.df.count()
        
        print(f"Starting validation on {{total_records:,}} records...")
        
        # Execute individual rule validations
        {chr(10).join(rule_implementations)}
        
        # Calculate overall quality score
        passed_rules = sum(1 for result in self.validation_results if result["status"] == "PASSED")
        total_rules = len(self.validation_results)
        overall_score = (passed_rules / total_rules) if total_rules > 0 else 0.0
        
        # Compile validation report
        validation_report = {{
            "table_name": "{table_metadata.get("table_name", "unknown")}",
            "validation_timestamp": datetime.now().isoformat(),
            "total_records": total_records,
            "total_rules": total_rules,
            "passed_rules": passed_rules,
            "failed_rules": total_rules - passed_rules,
            "overall_quality_score": overall_score,
            "rule_results": self.validation_results,
            "summary": self._generate_summary()
        }}
        
        return validation_report
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate validation summary"""
        summary = {{
            "critical_failures": [],
            "high_failures": [],
            "medium_failures": [],
            "warnings": []
        }}
        
        for result in self.validation_results:
            if result["status"] == "FAILED":
                severity = result.get("severity", "MEDIUM").lower()
                if severity == "critical":
                    summary["critical_failures"].append(result)
                elif severity == "high":
                    summary["high_failures"].append(result)
                elif severity == "medium":
                    summary["medium_failures"].append(result)
            elif result["status"] == "WARNING":
                summary["warnings"].append(result)
        
        return summary

def load_data(input_path: str) -> DataFrame:
    """Load data for validation"""
    if "{self.config.input_format}" == "parquet":
        return spark.read.parquet(input_path)
    elif "{self.config.input_format}" == "delta":
        return spark.read.format("delta").load(input_path)
    elif "{self.config.input_format}" == "csv":
        return spark.read.option("header", "true").option("inferSchema", "true").csv(input_path)
    elif "{self.config.input_format}" == "json":
        return spark.read.json(input_path)
    else:
        raise ValueError(f"Unsupported format: {self.config.input_format}")

def quarantine_bad_records(df: DataFrame, validation_results: List[Dict], 
                          output_path: str) -> None:
    """Quarantine records that failed validation"""
    if "{self.config.error_handling}" != "quarantine":
        return
    
    # Create quarantine conditions
    quarantine_conditions = []
    for result in validation_results:
        if result["status"] == "FAILED" and "quarantine_condition" in result:
            quarantine_conditions.append(result["quarantine_condition"])
    
    if quarantine_conditions:
        # Combine all quarantine conditions
        combined_condition = quarantine_conditions[0]
        for condition in quarantine_conditions[1:]:
            combined_condition = combined_condition | condition
        
        # Split data into clean and quarantine
        quarantine_df = df.filter(combined_condition)
        clean_df = df.filter(~combined_condition)
        
        # Save quarantine records
        if quarantine_df.count() > 0:
            quarantine_df.write.mode("overwrite").{self.config.output_format}(f"{{output_path}}/quarantine")
            print(f"Quarantined {{quarantine_df.count()}} records")
        
        # Save clean records
        clean_df.write.mode("overwrite").{self.config.output_format}(f"{{output_path}}/clean")
        print(f"Clean records: {{clean_df.count()}}")

def main(input_path: str, output_path: str):
    """Main validation function"""
    try:
        # Load data
        print("Loading data for validation...")
        df = load_data(input_path)
        
        {"df.cache()" if self.config.enable_caching else "# Caching disabled"}
        
        # Initialize validator
        validator = DataQualityValidator(df)
        
        # Run validations
        validation_report = validator.run_all_validations()
        
        # Handle error records based on configuration
        if "{self.config.error_handling}" == "quarantine":
            quarantine_bad_records(df, validator.validation_results, output_path)
        
        # Save validation report
        report_df = spark.createDataFrame([validation_report])
        report_df.coalesce(1).write.mode("overwrite").json(f"{{output_path}}/validation_report")
        
        # Save detailed results
        if validator.validation_results:
            results_df = spark.createDataFrame(validator.validation_results)
            results_df.write.mode("overwrite").{self.config.output_format}(f"{{output_path}}/rule_results")
        
        print("\\n=== VALIDATION SUMMARY ===")
        print(f"Overall Quality Score: {{validation_report['overall_quality_score']:.2f}}")
        print(f"Rules Passed: {{validation_report['passed_rules']}}/{{validation_report['total_rules']}}")
        
        if validation_report['failed_rules'] > 0:
            print(f"Rules Failed: {{validation_report['failed_rules']}}")
            summary = validation_report['summary']
            if summary['critical_failures']:
                print(f"  Critical: {{len(summary['critical_failures'])}}")
            if summary['high_failures']:
                print(f"  High: {{len(summary['high_failures'])}}")
            if summary['medium_failures']:
                print(f"  Medium: {{len(summary['medium_failures'])}}")
        
        print(f"Results saved to: {{output_path}}")
        
        return validation_report
        
    except Exception as e:
        print(f"Validation job failed: {{e}}")
        raise
    finally:
        if {"'df' in locals() and self.config.enable_caching" if self.config.enable_caching else "False"}:
            df.unpersist()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 3:
        print("Usage: python validation_job.py <input_path> <output_path>")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    
    main(input_path, output_path)
'''

        return job_code

    def _generate_rule_implementation(self, rule: DataQualityRule) -> str:
        """Generate Spark code for a specific rule"""

        rule_id = rule.rule_id
        rule_name = rule.rule_name
        column_name = rule.column_name
        pyspark_code = rule.pyspark_code
        threshold = rule.threshold or 0.0
        severity = rule.severity

        if rule.rule_type == DQRuleTypeEnum.COMPLETENESS:
            implementation = f"""
        # Rule: {rule_name}
        print("Executing rule: {rule_name}")
        null_count = {pyspark_code}
        null_percentage = (null_count / total_records * 100) if total_records > 0 else 0
        
        status = "PASSED" if null_count <= {threshold} else "FAILED"
        
        self.validation_results.append({{
            "rule_id": "{rule_id}",
            "rule_name": "{rule_name}",
            "rule_type": "completeness",
            "column_name": "{column_name}",
            "status": status,
            "severity": "{severity}",
            "failed_records": null_count,
            "failure_percentage": null_percentage,
            "threshold": {threshold},
            "message": f"Found {{null_count}} null values ({{null_percentage:.2f}}%)",
            "quarantine_condition": col("{column_name}").isNull() if status == "FAILED" else lit(False)
        }})
"""

        elif rule.rule_type == DQRuleTypeEnum.UNIQUENESS:
            implementation = f"""
        # Rule: {rule_name}
        print("Executing rule: {rule_name}")
        duplicate_count = total_records - {pyspark_code.replace(".count()", ".distinct().count()")}
        duplicate_percentage = (duplicate_count / total_records * 100) if total_records > 0 else 0
        
        status = "PASSED" if duplicate_count <= {threshold} else "FAILED"
        
        self.validation_results.append({{
            "rule_id": "{rule_id}",
            "rule_name": "{rule_name}",
            "rule_type": "uniqueness",
            "column_name": "{column_name}",
            "status": status,
            "severity": "{severity}",
            "failed_records": duplicate_count,
            "failure_percentage": duplicate_percentage,
            "threshold": {threshold},
            "message": f"Found {{duplicate_count}} duplicate values ({{duplicate_percentage:.2f}}%)",
            "quarantine_condition": lit(False)  # Duplicates handling would need more complex logic
        }})
"""

        elif rule.rule_type == DQRuleTypeEnum.RANGE_CHECK:
            # Extract range values from the rule
            implementation = f"""
        # Rule: {rule_name}
        print("Executing rule: {rule_name}")
        out_of_range_count = {pyspark_code}
        out_of_range_percentage = (out_of_range_count / total_records * 100) if total_records > 0 else 0
        
        status = "PASSED" if out_of_range_percentage <= {threshold * 100} else "FAILED"
        
        self.validation_results.append({{
            "rule_id": "{rule_id}",
            "rule_name": "{rule_name}",
            "rule_type": "range_check",
            "column_name": "{column_name}",
            "status": status,
            "severity": "{severity}",
            "failed_records": out_of_range_count,
            "failure_percentage": out_of_range_percentage,
            "threshold": {threshold * 100},
            "message": f"Found {{out_of_range_count}} out-of-range values ({{out_of_range_percentage:.2f}}%)",
            "quarantine_condition": lit(False)  # Would need to reconstruct range condition
        }})
"""

        elif rule.rule_type == DQRuleTypeEnum.FORMAT_CHECK:
            implementation = f"""
        # Rule: {rule_name}
        print("Executing rule: {rule_name}")
        invalid_format_count = {pyspark_code}
        invalid_format_percentage = (invalid_format_count / total_records * 100) if total_records > 0 else 0
        
        status = "PASSED" if invalid_format_count <= {threshold} else "FAILED"
        
        self.validation_results.append({{
            "rule_id": "{rule_id}",
            "rule_name": "{rule_name}",
            "rule_type": "format_check",
            "column_name": "{column_name}",
            "status": status,
            "severity": "{severity}",
            "failed_records": invalid_format_count,
            "failure_percentage": invalid_format_percentage,
            "threshold": {threshold},
            "message": f"Found {{invalid_format_count}} invalid format values ({{invalid_format_percentage:.2f}}%)",
            "quarantine_condition": lit(False)  # Would need format condition
        }})
"""

        else:
            # Generic rule implementation
            implementation = f"""
        # Rule: {rule_name}
        print("Executing rule: {rule_name}")
        try:
            violation_count = {pyspark_code}
            violation_percentage = (violation_count / total_records * 100) if total_records > 0 else 0
            
            status = "PASSED" if violation_count <= {threshold} else "FAILED"
            
            self.validation_results.append({{
                "rule_id": "{rule_id}",
                "rule_name": "{rule_name}",
                "rule_type": "{rule.rule_type.value}",
                "column_name": "{column_name}",
                "status": status,
                "severity": "{severity}",
                "failed_records": violation_count,
                "failure_percentage": violation_percentage,
                "threshold": {threshold},
                "message": f"Rule validation result: {{violation_count}} violations ({{violation_percentage:.2f}}%)",
                "quarantine_condition": lit(False)
            }})
            
        except Exception as e:
            self.validation_results.append({{
                "rule_id": "{rule_id}",
                "rule_name": "{rule_name}",
                "rule_type": "{rule.rule_type.value}",
                "column_name": "{column_name}",
                "status": "ERROR",
                "severity": "{severity}",
                "failed_records": 0,
                "failure_percentage": 0,
                "threshold": {threshold},
                "message": f"Rule execution failed: {{str(e)}}",
                "quarantine_condition": lit(False)
            }})
"""

        return implementation

    def generate_anomaly_detection_job(
        self, columns_config: List[Dict[str, Any]]
    ) -> str:
        """Generate anomaly detection job using statistical methods"""

        job_code = f'''
"""
Anomaly Detection Job
Purpose: Detect statistical anomalies and outliers in data
"""

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.stat import Correlation
from pyspark.ml.clustering import KMeans
from pyspark.ml.evaluation import ClusteringEvaluator
import pyspark.sql.functions as F
from datetime import datetime
import json

# Initialize Spark session
spark = SparkSession.builder \\
    .appName("AnomalyDetection") \\
    .config("spark.sql.adaptive.enabled", "true") \\
    .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \\
    .getOrCreate()

class AnomalyDetector:
    """Advanced anomaly detection using multiple methods"""
    
    def __init__(self, df: DataFrame):
        self.df = df
        self.anomalies = []
        
    def detect_statistical_outliers(self, column_name: str, method: str = "iqr") -> DataFrame:
        """Detect outliers using statistical methods"""
        
        if method == "iqr":
            # Interquartile Range method
            quantiles = self.df.select(
                expr(f"percentile_approx(`{{column_name}}`, 0.25)").alias("q1"),
                expr(f"percentile_approx(`{{column_name}}`, 0.75)").alias("q3")
            ).collect()[0]
            
            q1, q3 = quantiles["q1"], quantiles["q3"]
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            
            outliers = self.df.filter(
                (col(column_name) < lower_bound) | (col(column_name) > upper_bound)
            ).withColumn("anomaly_type", lit("statistical_outlier")) \\
             .withColumn("anomaly_method", lit("iqr")) \\
             .withColumn("anomaly_score", 
                        when(col(column_name) < lower_bound, (lower_bound - col(column_name)) / iqr)
                        .otherwise((col(column_name) - upper_bound) / iqr))
            
        elif method == "zscore":
            # Z-Score method
            stats = self.df.select(
                mean(col(column_name)).alias("mean"),
                stddev(col(column_name)).alias("stddev")
            ).collect()[0]
            
            mean_val, stddev_val = stats["mean"], stats["stddev"]
            threshold = 3.0  # 3 standard deviations
            
            outliers = self.df.withColumn("zscore", 
                                        abs((col(column_name) - mean_val) / stddev_val)) \\
                             .filter(col("zscore") > threshold) \\
                             .withColumn("anomaly_type", lit("statistical_outlier")) \\
                             .withColumn("anomaly_method", lit("zscore")) \\
                             .withColumn("anomaly_score", col("zscore"))
        
        return outliers
    
    def detect_time_series_anomalies(self, date_column: str, value_column: str) -> DataFrame:
        """Detect time series anomalies"""
        from pyspark.sql.window import Window
        
        # Calculate rolling statistics
        window_spec = Window.partitionBy().orderBy(col(date_column)).rowsBetween(-6, 0)  # 7-day window
        
        df_with_stats = self.df.withColumn("rolling_mean", 
                                         avg(col(value_column)).over(window_spec)) \\
                              .withColumn("rolling_stddev", 
                                        stddev(col(value_column)).over(window_spec))
        
        # Detect anomalies using rolling statistics
        anomalies = df_with_stats.withColumn("zscore", 
                                           abs((col(value_column) - col("rolling_mean")) / col("rolling_stddev"))) \\
                                  .filter(col("zscore") > 2.5) \\
                                  .withColumn("anomaly_type", lit("time_series_anomaly")) \\
                                  .withColumn("anomaly_method", lit("rolling_zscore")) \\
                                  .withColumn("anomaly_score", col("zscore"))
        
        return anomalies
    
    def detect_clustering_anomalies(self, feature_columns: List[str]) -> DataFrame:
        """Detect anomalies using clustering"""
        
        # Prepare features
        assembler = VectorAssembler(inputCols=feature_columns, outputCol="features")
        feature_df = assembler.transform(self.df)
        
        # Fit K-means clustering
        kmeans = KMeans(k=5, seed=42, featuresCol="features", predictionCol="cluster")
        model = kmeans.fit(feature_df)
        
        # Transform data
        clustered_df = model.transform(feature_df)
        
        # Calculate distances to cluster centers
        centers = model.clusterCenters()
        
        # Add distance calculation (simplified)
        anomalies = clustered_df.filter(col("cluster") == 0)  # Placeholder - would calculate actual distances
        
        return anomalies.withColumn("anomaly_type", lit("clustering_anomaly")) \\
                       .withColumn("anomaly_method", lit("kmeans")) \\
                       .withColumn("anomaly_score", lit(1.0))  # Placeholder
    
    def detect_pattern_anomalies(self, column_name: str) -> DataFrame:
        """Detect pattern-based anomalies in string columns"""
        
        # Get common patterns
        pattern_counts = self.df.groupBy(column_name).count() \\
                                .orderBy(desc("count")) \\
                                .limit(100)  # Top 100 patterns
        
        common_patterns = [row[column_name] for row in pattern_counts.collect()]
        
        # Find records that don't match common patterns
        anomalies = self.df.filter(~col(column_name).isin(common_patterns)) \\
                          .withColumn("anomaly_type", lit("pattern_anomaly")) \\
                          .withColumn("anomaly_method", lit("pattern_matching")) \\
                          .withColumn("anomaly_score", lit(1.0))
        
        return anomalies
    
    def generate_anomaly_report(self) -> Dict[str, Any]:
        """Generate comprehensive anomaly report"""
        
        all_anomalies = None
        anomaly_summary = {{}}
        
        # Statistical outliers for numeric columns
        numeric_columns = [field.name for field in self.df.schema.fields 
                          if field.dataType in [IntegerType(), DoubleType(), FloatType(), LongType()]]
        
        for column in numeric_columns[:5]:  # Limit to first 5 numeric columns
            print(f"Detecting outliers in {{column}}...")
            
            # IQR method
            iqr_outliers = self.detect_statistical_outliers(column, "iqr")
            
            # Z-score method
            zscore_outliers = self.detect_statistical_outliers(column, "zscore")
            
            # Combine anomalies
            column_anomalies = iqr_outliers.union(zscore_outliers)
            
            if all_anomalies is None:
                all_anomalies = column_anomalies
            else:
                all_anomalies = all_anomalies.union(column_anomalies)
            
            # Summary for this column
            anomaly_summary[column] = {{
                "iqr_outliers": iqr_outliers.count(),
                "zscore_outliers": zscore_outliers.count(),
                "total_outliers": column_anomalies.count()
            }}
        
        # String pattern anomalies
        string_columns = [field.name for field in self.df.schema.fields 
                         if field.dataType == StringType()]
        
        for column in string_columns[:3]:  # Limit to first 3 string columns
            print(f"Detecting pattern anomalies in {{column}}...")
            pattern_anomalies = self.detect_pattern_anomalies(column)
            
            if all_anomalies is None:
                all_anomalies = pattern_anomalies
            else:
                all_anomalies = all_anomalies.union(pattern_anomalies)
            
            anomaly_summary[f"{{column}}_patterns"] = {{
                "pattern_anomalies": pattern_anomalies.count()
            }}
        
        # Clustering anomalies (if enough numeric columns)
        if len(numeric_columns) >= 2:
            print("Detecting clustering anomalies...")
            clustering_anomalies = self.detect_clustering_anomalies(numeric_columns[:5])
            
            if all_anomalies is None:
                all_anomalies = clustering_anomalies
            else:
                all_anomalies = all_anomalies.union(clustering_anomalies)
            
            anomaly_summary["clustering"] = {{
                "clustering_anomalies": clustering_anomalies.count()
            }}
        
        # Overall statistics
        total_records = self.df.count()
        total_anomalies = all_anomalies.count() if all_anomalies else 0
        anomaly_percentage = (total_anomalies / total_records * 100) if total_records > 0 else 0
        
        report = {{
            "detection_timestamp": datetime.now().isoformat(),
            "total_records": total_records,
            "total_anomalies": total_anomalies,
            "anomaly_percentage": anomaly_percentage,
            "column_summary": anomaly_summary,
            "detection_methods": ["iqr", "zscore", "pattern_matching", "clustering"],
            "anomaly_data": all_anomalies
        }}
        
        return report

def main(input_path: str, output_path: str):
    """Main anomaly detection function"""
    try:
        # Load data
        print("Loading data for anomaly detection...")
        if "{self.config.input_format}" == "parquet":
            df = spark.read.parquet(input_path)
        elif "{self.config.input_format}" == "delta":
            df = spark.read.format("delta").load(input_path)
        else:
            df = spark.read.option("header", "true").option("inferSchema", "true").csv(input_path)
        
        {"df.cache()" if self.config.enable_caching else "# Caching disabled"}
        
        # Initialize detector
        detector = AnomalyDetector(df)
        
        # Generate anomaly report
        print("Generating anomaly report...")
        anomaly_report = detector.generate_anomaly_report()
        
        # Save results
        print("Saving anomaly detection results...")
        
        # Save anomaly records
        if anomaly_report["anomaly_data"] and anomaly_report["total_anomalies"] > 0:
            anomaly_report["anomaly_data"].write.mode("overwrite").{self.config.output_format}(f"{{output_path}}/anomalies")
        
        # Save summary report
        report_without_data = {{k: v for k, v in anomaly_report.items() if k != "anomaly_data"}}
        report_df = spark.createDataFrame([report_without_data])
        report_df.coalesce(1).write.mode("overwrite").json(f"{{output_path}}/anomaly_report")
        
        print("\\n=== ANOMALY DETECTION SUMMARY ===")
        print(f"Total records analyzed: {{anomaly_report['total_records']:,}}")
        print(f"Anomalies detected: {{anomaly_report['total_anomalies']:,}}")
        print(f"Anomaly rate: {{anomaly_report['anomaly_percentage']:.2f}}%")
        
        for column, stats in anomaly_report['column_summary'].items():
            for method, count in stats.items():
                if count > 0:
                    print(f"  {{column}} ({{method}}): {{count:,}}")
        
        print(f"Results saved to: {{output_path}}")
        
        return anomaly_report
        
    except Exception as e:
        print(f"Anomaly detection job failed: {{e}}")
        raise
    finally:
        if {"'df' in locals() and self.config.enable_caching" if self.config.enable_caching else "False"}:
            df.unpersist()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 3:
        print("Usage: python anomaly_detection_job.py <input_path> <output_path>")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    
    main(input_path, output_path)
'''

        return job_code

    def generate_cleaning_job(self, cleaning_rules: List[Dict[str, Any]]) -> str:
        """Generate data cleaning and transformation job"""

        job_code = f'''
"""
Data Cleaning and Transformation Job
Purpose: Clean and standardize data based on quality rules
"""

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import *
from pyspark.sql.types import *
import pyspark.sql.functions as F
from datetime import datetime
import re

# Initialize Spark session
spark = SparkSession.builder \\
    .appName("DataCleaning") \\
    .config("spark.sql.adaptive.enabled", "true") \\
    .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \\
    .getOrCreate()

class DataCleaner:
    """Data cleaning and transformation engine"""
    
    def __init__(self, df: DataFrame):
        self.df = df
        self.cleaning_stats = {{}}
        
    def standardize_column_names(self) -> DataFrame:
        """Standardize column names"""
        print("Standardizing column names...")
        
        cleaned_df = self.df
        renamed_columns = {{}}
        
        for column in self.df.columns:
            # Convert to snake_case and remove special characters
            cleaned_name = re.sub(r'[^a-zA-Z0-9_]', '_', column.lower())
            cleaned_name = re.sub(r'_+', '_', cleaned_name)  # Remove multiple underscores
            cleaned_name = cleaned_name.strip('_')  # Remove leading/trailing underscores
            
            if cleaned_name != column:
                cleaned_df = cleaned_df.withColumnRenamed(column, cleaned_name)
                renamed_columns[column] = cleaned_name
        
        self.cleaning_stats["renamed_columns"] = renamed_columns
        return cleaned_df
    
    def handle_missing_values(self, strategies: Dict[str, str]) -> DataFrame:
        """Handle missing values with different strategies"""
        print("Handling missing values...")
        
        cleaned_df = self.df
        null_stats = {{}}
        
        for column, strategy in strategies.items():
            if column not in self.df.columns:
                continue
                
            original_nulls = cleaned_df.filter(col(column).isNull()).count()
            
            if strategy == "drop":
                cleaned_df = cleaned_df.filter(col(column).isNotNull())
            elif strategy == "fill_mean":
                mean_value = cleaned_df.select(mean(col(column))).collect()[0][0]
                if mean_value is not None:
                    cleaned_df = cleaned_df.fillna({{column: mean_value}})
            elif strategy == "fill_median":
                median_value = cleaned_df.select(expr(f"percentile_approx(`{{column}}`, 0.5)")).collect()[0][0]
                if median_value is not None:
                    cleaned_df = cleaned_df.fillna({{column: median_value}})
            elif strategy == "fill_mode":
                mode_value = cleaned_df.groupBy(column).count().orderBy(desc("count")).first()[column]
                if mode_value is not None:
                    cleaned_df = cleaned_df.fillna({{column: mode_value}})
            elif strategy.startswith("fill_"):
                # Custom fill value
                fill_value = strategy.replace("fill_", "")
                cleaned_df = cleaned_df.fillna({{column: fill_value}})
            
            final_nulls = cleaned_df.filter(col(column).isNull()).count()
            null_stats[column] = {{
                "original_nulls": original_nulls,
                "final_nulls": final_nulls,
                "strategy": strategy
            }}
        
        self.cleaning_stats["null_handling"] = null_stats
        return cleaned_df
    
    def standardize_formats(self) -> DataFrame:
        """Standardize data formats"""
        print("Standardizing formats...")
        
        cleaned_df = self.df
        format_stats = {{}}
        
        for column in self.df.columns:
            column_type = dict(self.df.dtypes)[column]
            
            if column_type == "string":
                # Email standardization
                if "email" in column.lower():
                    original_count = cleaned_df.count()
                    cleaned_df = cleaned_df.withColumn(column, lower(trim(col(column))))
                    # Remove invalid emails
                    cleaned_df = cleaned_df.filter(
                        col(column).rlike(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{{2,}}$") | 
                        col(column).isNull()
                    )
                    final_count = cleaned_df.count()
                    format_stats[f"{{column}}_email"] = {{
                        "removed_invalid": original_count - final_count
                    }}
                
                # Phone number standardization
                elif "phone" in column.lower():
                    # Remove formatting and keep only digits
                    cleaned_df = cleaned_df.withColumn(
                        column,
                        regexp_replace(col(column), r"[^0-9]", "")
                    )
                    # Ensure proper length
                    cleaned_df = cleaned_df.withColumn(
                        column,
                        when(length(col(column)).between(10, 15), col(column))
                        .otherwise(lit(None))
                    )
                
                # Text standardization
                else:
                    # Trim whitespace and normalize case for categorical data
                    unique_ratio = cleaned_df.select(column).distinct().count() / cleaned_df.count()
                    if unique_ratio < 0.1:  # Likely categorical
                        cleaned_df = cleaned_df.withColumn(column, trim(col(column)))
            
            elif column_type in ["timestamp", "date"]:
                # Date standardization
                if column_type == "string":
                    # Try to parse common date formats
                    cleaned_df = cleaned_df.withColumn(
                        column,
                        coalesce(
                            to_timestamp(col(column), "yyyy-MM-dd"),
                            to_timestamp(col(column), "MM/dd/yyyy"),
                            to_timestamp(col(column), "dd/MM/yyyy"),
                            to_timestamp(col(column), "yyyy-MM-dd HH:mm:ss")
                        )
                    )
        
        self.cleaning_stats["format_standardization"] = format_stats
        return cleaned_df
    
    def remove_duplicates(self, subset_columns: List[str] = None) -> DataFrame:
        """Remove duplicate records"""
        print("Removing duplicates...")
        
        original_count = self.df.count()
        
        if subset_columns:
            cleaned_df = self.df.dropDuplicates(subset_columns)
        else:
            cleaned_df = self.df.dropDuplicates()
        
        final_count = cleaned_df.count()
        duplicates_removed = original_count - final_count
        
        self.cleaning_stats["duplicates"] = {{
            "original_count": original_count,
            "final_count": final_count,
            "duplicates_removed": duplicates_removed,
            "subset_columns": subset_columns
        }}
        
        return cleaned_df
    
    def validate_and_fix_ranges(self, range_rules: Dict[str, Dict]) -> DataFrame:
        """Validate and fix range violations"""
        print("Validating and fixing ranges...")
        
        cleaned_df = self.df
        range_stats = {{}}
        
        for column, rules in range_rules.items():
            if column not in self.df.columns:
                continue
                
            min_val = rules.get("min")
            max_val = rules.get("max")
            action = rules.get("action", "cap")  # cap, null, remove
            
            original_violations = 0
            if min_val is not None:
                original_violations += cleaned_df.filter(col(column) < min_val).count()
            if max_val is not None:
                original_violations += cleaned_df.filter(col(column) > max_val).count()
            
            if action == "cap":
                # Cap values to min/max
                if min_val is not None and max_val is not None:
                    cleaned_df = cleaned_df.withColumn(
                        column,
                        when(col(column) < min_val, lit(min_val))
                        .when(col(column) > max_val, lit(max_val))
                        .otherwise(col(column))
                    )
                elif min_val is not None:
                    cleaned_df = cleaned_df.withColumn(
                        column,
                        when(col(column) < min_val, lit(min_val))
                        .otherwise(col(column))
                    )
                elif max_val is not None:
                    cleaned_df = cleaned_df.withColumn(
                        column,
                        when(col(column) > max_val, lit(max_val))
                        .otherwise(col(column))
                    )
            elif action == "null":
                # Set to null
                if min_val is not None and max_val is not None:
                    cleaned_df = cleaned_df.withColumn(
                        column,
                        when((col(column) < min_val) | (col(column) > max_val), lit(None))
                        .otherwise(col(column))
                    )
            elif action == "remove":
                # Remove records
                if min_val is not None:
                    cleaned_df = cleaned_df.filter(col(column) >= min_val)
                if max_val is not None:
                    cleaned_df = cleaned_df.filter(col(column) <= max_val)
            
            range_stats[column] = {{
                "original_violations": original_violations,
                "action": action,
                "min_value": min_val,
                "max_value": max_val
            }}
        
        self.cleaning_stats["range_validation"] = range_stats
        return cleaned_df
    
    def generate_cleaning_report(self) -> Dict[str, Any]:
        """Generate cleaning report"""
        return {{
            "cleaning_timestamp": datetime.now().isoformat(),
            "cleaning_statistics": self.cleaning_stats,
            "original_columns": len(self.df.columns),
            "final_columns": len(self.df.columns),  # Would update after cleaning
            "cleaning_steps": list(self.cleaning_stats.keys())
        }}

def main(input_path: str, output_path: str):
    """Main cleaning function"""
    try:
        # Load data
        print("Loading data for cleaning...")
        if "{self.config.input_format}" == "parquet":
            df = spark.read.parquet(input_path)
        elif "{self.config.input_format}" == "delta":
            df = spark.read.format("delta").load(input_path)
        else:
            df = spark.read.option("header", "true").option("inferSchema", "true").csv(input_path)
        
        original_count = df.count()
        print(f"Original data: {{original_count:,}} records, {{len(df.columns)}} columns")
        
        # Initialize cleaner
        cleaner = DataCleaner(df)
        
        # Step 1: Standardize column names
        cleaned_df = cleaner.standardize_column_names()
        
        # Step 2: Handle missing values
        missing_strategies = {{
            # Define strategies based on column types and business rules
            # This would be configurable in real implementation
        }}
        if missing_strategies:
            cleaned_df = cleaner.handle_missing_values(missing_strategies)
        
        # Step 3: Standardize formats
        cleaned_df = cleaner.standardize_formats()
        
        # Step 4: Remove duplicates
        cleaned_df = cleaner.remove_duplicates()
        
        # Step 5: Validate ranges (if rules provided)
        range_rules = {{
            # Define range rules based on business requirements
            # This would be configurable in real implementation
        }}
        if range_rules:
            cleaned_df = cleaner.validate_and_fix_ranges(range_rules)
        
        final_count = cleaned_df.count()
        
        # Generate cleaning report
        cleaning_report = cleaner.generate_cleaning_report()
        cleaning_report["original_records"] = original_count
        cleaning_report["final_records"] = final_count
        cleaning_report["records_removed"] = original_count - final_count
        
        # Save cleaned data
        print("Saving cleaned data...")
        cleaned_df.write.mode("overwrite").{self.config.output_format}(f"{{output_path}}/cleaned_data")
        
        # Save cleaning report
        report_df = spark.createDataFrame([cleaning_report])
        report_df.coalesce(1).write.mode("overwrite").json(f"{{output_path}}/cleaning_report")
        
        print("\\n=== CLEANING SUMMARY ===")
        print(f"Original records: {{original_count:,}}")
        print(f"Final records: {{final_count:,}}")
        print(f"Records removed: {{original_count - final_count:,}}")
        print(f"Data retention: {{(final_count / original_count * 100):.1f}}%")
        
        for step, stats in cleaner.cleaning_stats.items():
            print(f"\\n{{step.replace('_', ' ').title()}}:")
            if isinstance(stats, dict):
                for key, value in list(stats.items())[:3]:  # Show first 3 items
                    print(f"  {{key}}: {{value}}")
        
        print(f"Results saved to: {{output_path}}")
        
        return cleaning_report
        
    except Exception as e:
        print(f"Data cleaning job failed: {{e}}")
        raise

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 3:
        print("Usage: python data_cleaning_job.py <input_path> <output_path>")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    
    main(input_path, output_path)
'''

        return job_code
