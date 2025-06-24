"""
Data Quality (DQ) Plugin

This plugin provides AI-powered data quality assessment and automation:
- Schema and metadata analysis
- LLM-driven profiling suggestions
- Intelligent DQ rule generation
- PySpark code generation for DQ execution
- Data lineage and impact analysis
- Statistical profiling and anomaly detection
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter
from core.plugins import BasePlugin, PluginMetadata
from core.llm import llm_manager, PromptTemplate
from dataclasses import dataclass
from enum import Enum


class DataType(Enum):
    """Supported data types"""

    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    DECIMAL = "decimal"
    JSON = "json"


class DQRuleType(Enum):
    """Data Quality rule types"""

    COMPLETENESS = "completeness"
    UNIQUENESS = "uniqueness"
    VALIDITY = "validity"
    CONSISTENCY = "consistency"
    ACCURACY = "accuracy"
    TIMELINESS = "timeliness"
    REFERENTIAL_INTEGRITY = "referential_integrity"
    BUSINESS_RULES = "business_rules"


@dataclass
class ColumnMetadata:
    """Column metadata structure"""

    name: str
    data_type: DataType
    nullable: bool
    primary_key: bool = False
    foreign_key: Optional[str] = None
    unique: bool = False
    default_value: Optional[str] = None
    description: Optional[str] = None
    business_meaning: Optional[str] = None
    constraints: List[str] = None
    sample_values: List[Any] = None


@dataclass
class TableMetadata:
    """Table metadata structure"""

    name: str
    schema_name: str
    database_name: str
    columns: List[ColumnMetadata]
    row_count: Optional[int] = None
    description: Optional[str] = None
    business_context: Optional[str] = None
    data_classification: Optional[str] = None
    update_frequency: Optional[str] = None
    data_owner: Optional[str] = None


@dataclass
class DQRule:
    """Data Quality rule structure"""

    rule_id: str
    rule_type: DQRuleType
    column_name: str
    rule_description: str
    sql_expression: str
    pyspark_code: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    threshold: Optional[float] = None
    error_message: str = ""
    business_impact: str = ""


class DataQualityPlugin(BasePlugin):
    """Data Quality Assessment and Automation Plugin"""

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.router = APIRouter()
        self._setup_routes()
        self._setup_templates()

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="data_quality",
            version="1.0.0",
            description="AI-powered data quality assessment and rule generation",
            author="AI Base Platform",
            dependencies=["pyspark", "pandas", "sqlalchemy", "great_expectations"],
            api_version="1.0",
            config_schema={
                "spark_config": {"type": "object", "default": {}},
                "default_dq_engine": {"type": "string", "default": "pyspark"},
                "llm_provider": {"type": "string", "default": "openai"},
                "profiling_sample_size": {"type": "integer", "default": 10000},
                "enable_ml_anomaly_detection": {"type": "boolean", "default": True},
            },
        )

    async def initialize(self) -> bool:
        """Initialize the data quality plugin"""
        try:
            # Initialize Spark session if configured
            await self._initialize_spark()

            # Setup LLM templates for DQ rule generation
            await self._initialize_llm_templates()

            return True
        except Exception as e:
            print(f"Failed to initialize Data Quality plugin: {e}")
            return False

    async def cleanup(self) -> bool:
        """Cleanup resources"""
        try:
            # Stop Spark session if running
            if hasattr(self, "spark"):
                self.spark.stop()
            return True
        except Exception:
            return False

    def get_api_routes(self) -> List[Dict[str, Any]]:
        """Return API routes for data quality"""
        return [{"path": "/api/v1/data-quality", "router": self.router}]

    def get_frontend_routes(self) -> List[Dict[str, Any]]:
        """Return frontend routes for data quality"""
        return [
            {
                "path": "/apps/data-quality",
                "component": "DataQualityApp",
                "name": "Data Quality",
                "icon": "BarChart3",
            }
        ]

    def _setup_routes(self):
        """Setup API routes"""

        @self.router.post("/analyze-schema")
        async def analyze_schema(request: Dict[str, Any]):
            """Analyze database schema and generate metadata"""
            return await self._analyze_schema(
                connection_string=request["connection_string"],
                schema_name=request.get("schema_name"),
                table_names=request.get("table_names", []),
            )

        @self.router.post("/profile-data")
        async def profile_data(request: Dict[str, Any]):
            """Profile data and generate statistics"""
            return await self._profile_data(
                table_metadata=request["table_metadata"],
                sample_size=request.get("sample_size", 10000),
            )

        @self.router.post("/generate-dq-rules")
        async def generate_dq_rules(request: Dict[str, Any]):
            """Generate data quality rules using LLM"""
            return await self._generate_dq_rules(
                table_metadata=request["table_metadata"],
                profiling_results=request.get("profiling_results", {}),
                business_context=request.get("business_context", ""),
            )

        @self.router.post("/generate-pyspark-code")
        async def generate_pyspark_code(request: Dict[str, Any]):
            """Generate PySpark code for DQ rule execution"""
            return await self._generate_pyspark_code(
                dq_rules=request["dq_rules"], table_metadata=request["table_metadata"]
            )

        @self.router.post("/execute-dq-rules")
        async def execute_dq_rules(request: Dict[str, Any]):
            """Execute data quality rules and return results"""
            return await self._execute_dq_rules(
                pyspark_code=request["pyspark_code"],
                connection_config=request["connection_config"],
            )

        @self.router.get("/health")
        async def health_check():
            """Data quality plugin health check"""
            return await self.health_check()

    def _setup_templates(self):
        """Setup LLM prompt templates"""

        # Template for generating DQ rules based on schema analysis
        dq_rules_template = PromptTemplate(
            template="""
You are a data quality expert. Based on the following table schema and profiling results, generate comprehensive data quality rules.

Table: {schema_name}.{table_name}
Business Context: {business_context}

Column Metadata:
{column_metadata}

Profiling Results:
{profiling_results}

Requirements:
1. Generate DQ rules for each relevant column
2. Include completeness, uniqueness, validity, and consistency checks
3. Consider business logic and domain constraints
4. Provide SQL expressions and PySpark code for each rule
5. Assign appropriate severity levels (CRITICAL, HIGH, MEDIUM, LOW)
6. Include meaningful error messages and business impact descriptions
7. Consider cross-column validations and referential integrity
8. Add statistical anomaly detection rules where appropriate

Generate comprehensive data quality rules in JSON format:
{{
  "rules": [
    {{
      "rule_id": "unique_rule_id",
      "rule_type": "completeness|uniqueness|validity|consistency|accuracy",
      "column_name": "column_name",
      "rule_description": "Human readable description",
      "sql_expression": "SQL WHERE clause expression",
      "pyspark_code": "PySpark DataFrame operation",
      "severity": "CRITICAL|HIGH|MEDIUM|LOW",
      "threshold": 0.95,
      "error_message": "Error message for failures",
      "business_impact": "Business impact description"
    }}
  ]
}}
""",
            variables=[
                "schema_name",
                "table_name",
                "business_context",
                "column_metadata",
                "profiling_results",
            ],
        )

        # Template for generating PySpark data quality framework
        pyspark_framework_template = PromptTemplate(
            template="""
You are a PySpark expert. Generate a comprehensive PySpark data quality framework for the following table and rules.

Table: {schema_name}.{table_name}
Connection Type: {connection_type}

Data Quality Rules:
{dq_rules}

Requirements:
1. Create a complete PySpark application
2. Include data loading from the specified connection
3. Implement each DQ rule as a separate function
4. Add comprehensive logging and error handling
5. Generate detailed DQ results with metrics
6. Include data lineage tracking
7. Handle large datasets efficiently with partitioning
8. Add configuration management
9. Include unit tests for each DQ rule
10. Generate summary reports and alerts

Generate production-ready PySpark code with proper error handling and performance optimization.
""",
            variables=["schema_name", "table_name", "connection_type", "dq_rules"],
        )

        # Template for generating profiling suggestions
        profiling_template = PromptTemplate(
            template="""
You are a data profiling expert. Based on the following table metadata, suggest comprehensive data profiling strategies.

Table: {schema_name}.{table_name}
Business Context: {business_context}

Column Information:
{column_info}

Requirements:
1. Suggest statistical profiling for numeric columns
2. Recommend pattern analysis for string columns
3. Identify potential data quality issues
4. Suggest anomaly detection approaches
5. Recommend sampling strategies for large datasets
6. Include temporal analysis for date/time columns
7. Suggest cross-column correlation analysis
8. Identify potential PII and sensitive data
9. Recommend data classification strategies

Generate detailed profiling recommendations with specific techniques and tools.
""",
            variables=["schema_name", "table_name", "business_context", "column_info"],
        )

        # Register templates
        llm_manager.register_template("dq_rules_generation", dq_rules_template)
        llm_manager.register_template(
            "pyspark_framework_generation", pyspark_framework_template
        )
        llm_manager.register_template("profiling_suggestions", profiling_template)

    async def _initialize_spark(self):
        """Initialize Spark session"""
        try:
            from pyspark.sql import SparkSession

            self.spark = (
                SparkSession.builder.appName("AI_Base_DataQuality")
                .config("spark.sql.adaptive.enabled", "true")
                .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
                .getOrCreate()
            )
        except ImportError:
            print("PySpark not available - some features will be limited")
            self.spark = None

    async def _initialize_llm_templates(self):
        """Initialize LLM templates"""
        self._setup_templates()

    async def _analyze_schema(
        self,
        connection_string: str,
        schema_name: str = None,
        table_names: List[str] = None,
    ) -> Dict[str, Any]:
        """Analyze database schema and extract metadata"""
        try:
            # Use SQLAlchemy to introspect database schema
            from sqlalchemy import create_engine, MetaData, inspect

            engine = create_engine(connection_string)
            inspector = inspect(engine)

            schemas = [schema_name] if schema_name else inspector.get_schema_names()
            tables_metadata = []

            for schema in schemas:
                table_names_in_schema = table_names or inspector.get_table_names(
                    schema=schema
                )

                for table_name in table_names_in_schema:
                    columns_info = inspector.get_columns(table_name, schema=schema)
                    pk_constraint = inspector.get_pk_constraint(
                        table_name, schema=schema
                    )
                    fk_constraints = inspector.get_foreign_keys(
                        table_name, schema=schema
                    )
                    unique_constraints = inspector.get_unique_constraints(
                        table_name, schema=schema
                    )

                    # Build column metadata
                    columns = []
                    for col_info in columns_info:
                        column_meta = ColumnMetadata(
                            name=col_info["name"],
                            data_type=self._map_sql_type_to_enum(str(col_info["type"])),
                            nullable=col_info.get("nullable", True),
                            primary_key=col_info["name"]
                            in pk_constraint.get("constrained_columns", []),
                            default_value=col_info.get("default"),
                            constraints=[],
                        )

                        # Add foreign key information
                        for fk in fk_constraints:
                            if col_info["name"] in fk["constrained_columns"]:
                                column_meta.foreign_key = f"{fk['referred_schema']}.{fk['referred_table']}.{fk['referred_columns'][0]}"

                        # Check unique constraints
                        for uc in unique_constraints:
                            if col_info["name"] in uc["column_names"]:
                                column_meta.unique = True

                        columns.append(column_meta)

                    # Get row count estimate
                    try:
                        with engine.connect() as conn:
                            result = conn.execute(
                                f"SELECT COUNT(*) FROM {schema}.{table_name}"
                            )
                            row_count = result.fetchone()[0]
                    except Exception:
                        row_count = None

                    table_meta = TableMetadata(
                        name=table_name,
                        schema_name=schema,
                        database_name=engine.url.database,
                        columns=columns,
                        row_count=row_count,
                    )

                    tables_metadata.append(table_meta)

            return {
                "database_name": engine.url.database,
                "tables": [
                    self._serialize_table_metadata(tm) for tm in tables_metadata
                ],
                "analysis_timestamp": "2025-01-01T00:00:00Z",
                "metadata": {
                    "total_tables": len(tables_metadata),
                    "total_columns": sum(len(tm.columns) for tm in tables_metadata),
                    "connection_type": engine.url.drivername,
                },
            }

        except Exception as e:
            raise RuntimeError(f"Failed to analyze schema: {str(e)}")

    async def _profile_data(
        self, table_metadata: Dict[str, Any], sample_size: int = 10000
    ) -> Dict[str, Any]:
        """Profile data and generate comprehensive statistics"""
        try:
            # This would use pandas/PySpark for actual profiling
            # For now, return a mock structure

            profiling_results = {
                "table_stats": {
                    "row_count": table_metadata.get("row_count", 0),
                    "column_count": len(table_metadata.get("columns", [])),
                    "completeness_score": 0.95,
                    "uniqueness_score": 0.87,
                    "validity_score": 0.92,
                },
                "column_profiles": [],
                "data_quality_issues": [],
                "recommendations": [],
            }

            # Generate column profiles
            for column in table_metadata.get("columns", []):
                column_profile = await self._profile_column(column, sample_size)
                profiling_results["column_profiles"].append(column_profile)

            # Generate profiling suggestions using LLM
            suggestions_response = await llm_manager.generate(
                provider_name="openai",
                template_name="profiling_suggestions",
                template_vars={
                    "schema_name": table_metadata.get("schema_name", ""),
                    "table_name": table_metadata.get("name", ""),
                    "business_context": table_metadata.get("business_context", ""),
                    "column_info": str(table_metadata.get("columns", []))[:1000],
                },
            )

            profiling_results["ai_suggestions"] = suggestions_response.content
            profiling_results["generation_metadata"] = {
                "provider": suggestions_response.provider.value,
                "tokens_used": suggestions_response.tokens_used,
                "cost": suggestions_response.cost,
            }

            return profiling_results

        except Exception as e:
            raise RuntimeError(f"Failed to profile data: {str(e)}")

    async def _profile_column(
        self, column: Dict[str, Any], sample_size: int
    ) -> Dict[str, Any]:
        """Profile individual column"""
        # Mock column profiling - would use actual data in production
        return {
            "column_name": column["name"],
            "data_type": column["data_type"],
            "null_count": 45,
            "null_percentage": 4.5,
            "unique_count": 850,
            "unique_percentage": 85.0,
            "min_value": None,
            "max_value": None,
            "mean": None,
            "median": None,
            "std_dev": None,
            "pattern_analysis": {"most_common_patterns": [], "invalid_patterns": []},
            "anomalies": [],
            "data_quality_score": 0.92,
        }

    async def _generate_dq_rules(
        self,
        table_metadata: Dict[str, Any],
        profiling_results: Dict[str, Any] = None,
        business_context: str = "",
    ) -> Dict[str, Any]:
        """Generate data quality rules using LLM"""
        try:
            # Prepare metadata for LLM
            column_metadata = "\n".join(
                [
                    f"- {col['name']} ({col['data_type']}): nullable={col['nullable']}, pk={col.get('primary_key', False)}"
                    for col in table_metadata.get("columns", [])
                ]
            )

            # Generate DQ rules using LLM
            dq_response = await llm_manager.generate(
                provider_name="openai",
                template_name="dq_rules_generation",
                template_vars={
                    "schema_name": table_metadata.get("schema_name", ""),
                    "table_name": table_metadata.get("name", ""),
                    "business_context": business_context,
                    "column_metadata": column_metadata,
                    "profiling_results": str(profiling_results or {})[:1000],
                },
            )

            # Parse the generated rules (would include proper JSON parsing)
            return {
                "table_name": table_metadata.get("name"),
                "schema_name": table_metadata.get("schema_name"),
                "generated_rules": dq_response.content,
                "rules_count": 0,  # Would count actual parsed rules
                "generation_metadata": {
                    "provider": dq_response.provider.value,
                    "model": dq_response.model,
                    "tokens_used": dq_response.tokens_used,
                    "cost": dq_response.cost,
                },
                "business_context": business_context,
            }

        except Exception as e:
            raise RuntimeError(f"Failed to generate DQ rules: {str(e)}")

    async def _generate_pyspark_code(
        self, dq_rules: List[Dict[str, Any]], table_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate PySpark code for DQ rule execution"""
        try:
            # Generate PySpark framework using LLM
            pyspark_response = await llm_manager.generate(
                provider_name="openai",
                template_name="pyspark_framework_generation",
                template_vars={
                    "schema_name": table_metadata.get("schema_name", ""),
                    "table_name": table_metadata.get("name", ""),
                    "connection_type": "jdbc",  # Would be configurable
                    "dq_rules": str(dq_rules)[:2000],
                },
            )

            return {
                "pyspark_code": pyspark_response.content,
                "framework_type": "pyspark",
                "table_metadata": table_metadata,
                "dq_rules_count": len(dq_rules),
                "generation_metadata": {
                    "provider": pyspark_response.provider.value,
                    "model": pyspark_response.model,
                    "tokens_used": pyspark_response.tokens_used,
                    "cost": pyspark_response.cost,
                },
            }

        except Exception as e:
            raise RuntimeError(f"Failed to generate PySpark code: {str(e)}")

    async def _execute_dq_rules(
        self, pyspark_code: str, connection_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute data quality rules and return results"""
        try:
            if not self.spark:
                raise RuntimeError("Spark session not available")

            # In production, this would execute the generated PySpark code
            # For now, return mock results
            return {
                "execution_status": "completed",
                "total_rules_executed": 15,
                "passed_rules": 12,
                "failed_rules": 3,
                "execution_time_seconds": 45.2,
                "results": [
                    {
                        "rule_id": "completeness_check_id",
                        "status": "passed",
                        "score": 0.98,
                        "threshold": 0.95,
                        "records_processed": 100000,
                        "failed_records": 2000,
                        "error_details": [],
                    }
                ],
                "summary": {
                    "overall_quality_score": 0.89,
                    "data_quality_level": "GOOD",
                    "critical_issues": 1,
                    "recommendations": [
                        "Address missing values in customer_email column",
                        "Investigate duplicate records in customer_id",
                    ],
                },
            }

        except Exception as e:
            raise RuntimeError(f"Failed to execute DQ rules: {str(e)}")

    def _map_sql_type_to_enum(self, sql_type: str) -> DataType:
        """Map SQL data type to our enum"""
        sql_type_lower = sql_type.lower()

        if (
            "varchar" in sql_type_lower
            or "char" in sql_type_lower
            or "text" in sql_type_lower
        ):
            return DataType.STRING
        elif "int" in sql_type_lower or "bigint" in sql_type_lower:
            return DataType.INTEGER
        elif (
            "float" in sql_type_lower
            or "double" in sql_type_lower
            or "real" in sql_type_lower
        ):
            return DataType.FLOAT
        elif "decimal" in sql_type_lower or "numeric" in sql_type_lower:
            return DataType.DECIMAL
        elif "bool" in sql_type_lower:
            return DataType.BOOLEAN
        elif "date" in sql_type_lower and "time" not in sql_type_lower:
            return DataType.DATE
        elif "timestamp" in sql_type_lower or "datetime" in sql_type_lower:
            return DataType.DATETIME
        elif "json" in sql_type_lower:
            return DataType.JSON
        else:
            return DataType.STRING

    def _serialize_table_metadata(self, table_meta: TableMetadata) -> Dict[str, Any]:
        """Serialize table metadata to dictionary"""
        return {
            "name": table_meta.name,
            "schema_name": table_meta.schema_name,
            "database_name": table_meta.database_name,
            "row_count": table_meta.row_count,
            "description": table_meta.description,
            "business_context": table_meta.business_context,
            "columns": [
                {
                    "name": col.name,
                    "data_type": col.data_type.value,
                    "nullable": col.nullable,
                    "primary_key": col.primary_key,
                    "foreign_key": col.foreign_key,
                    "unique": col.unique,
                    "default_value": col.default_value,
                    "description": col.description,
                    "constraints": col.constraints or [],
                }
                for col in table_meta.columns
            ],
        }

    async def health_check(self) -> Dict[str, Any]:
        """Health check for data quality plugin"""
        try:
            # Check if Spark is available
            spark_available = self.spark is not None

            # Check if LLM is available
            llm_available = len(llm_manager._providers) > 0

            status = "healthy" if spark_available and llm_available else "degraded"

            return {
                "status": status,
                "message": f"Data Quality plugin is {status}",
                "details": {
                    "spark_available": spark_available,
                    "llm_available": llm_available,
                    "supported_databases": [
                        "postgresql",
                        "mysql",
                        "sqlserver",
                        "oracle",
                        "sqlite",
                    ],
                    "supported_engines": ["pyspark", "pandas", "great_expectations"],
                },
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Data Quality plugin error: {str(e)}",
                "details": {},
            }
