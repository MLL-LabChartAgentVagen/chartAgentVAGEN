"""
ChartAgentVAGEN - Gemini-Driven Synthetic Data Construction Pipeline
=====================================================================

A modular, multi-node pipeline for generating high-quality training samples
with RL-Ready outputs (Chain-of-Thought traces + Hard Negatives).

Architecture: LangGraph-style sequential workflow
LLM Backend: Google Gemini (gemini-1.5-pro / gemini-2.0-flash)

Author: ChartAgentVAGEN Team
Version: 1.0.0
"""

import json
import random
import hashlib
from typing import TypedDict, Literal, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

# =============================================================================
# SECTION 1: CORE SCHEMA DEFINITIONS (The "Knowledge Base")
# =============================================================================

META_CATEGORIES = [
    "1 - Media & Entertainment",
    "2 - Geography & Demography",
    "3 - Education & Academia",
    "4 - Business & Industry",
    "5 - Major & Course",
    "6 - Animal & Zoology",
    "7 - Plant & Botany",
    "8 - Biology & Chemistry",
    "9 - Food & Nutrition",
    "10 - Space & Astronomy",
    "11 - Sale & Merchandise",
    "12 - Market & Economy",
    "13 - Sports & Athletics",
    "14 - Computing & Technology",
    "15 - Health & Medicine",
    "16 - Energy & Environment",
    "17 - Travel & Expedition",
    "18 - Arts & Culture",
    "19 - Communication & Collaboration",
    "20 - Language & Linguistics",
    "21 - History & Archaeology",
    "22 - Weather & Climate",
    "23 - Transportation & Infrastructure",
    "24 - Psychology & Personality",
    "25 - Materials & Engineering",
    "26 - Philanthropy & Charity",
    "27 - Fashion & Apparel",
    "28 - Parenting & Child Development",
    "29 - Architecture & Urban Planning",
    "30 - Gaming & Recreation",
]

class ChartType(Enum):
    BAR = "bar"
    SCATTER = "scatter"
    PIE = "pie"


# Schema definitions for each chart type
CHART_SCHEMAS = {
    ChartType.BAR: {
        "required_keys": ["bar_data", "bar_labels", "bar_colors", "x_label", "y_label", "img_title"],
        "data_constraints": {
            "bar_data": "list[float] - Numeric values, typically 5-15 items",
            "bar_labels": "list[str] - Category labels, same length as bar_data",
            "bar_colors": "list[str] - Hex color codes (#RRGGBB), same length as bar_data",
            "x_label": "str - X-axis label describing the categories",
            "y_label": "str - Y-axis label with units in parentheses",
            "img_title": "str - Descriptive chart title"
        }
    },
    ChartType.SCATTER: {
        "required_keys": ["scatter_x_data", "scatter_y_data", "scatter_labels", "scatter_colors", 
                         "scatter_sizes", "x_label", "y_label", "img_title"],
        "data_constraints": {
            "scatter_x_data": "list[float] - X-coordinates",
            "scatter_y_data": "list[float] - Y-coordinates",
            "scatter_labels": "list[str] - Point labels",
            "scatter_colors": "list[str] - Hex color codes",
            "scatter_sizes": "list[float] - Point sizes (typically value * scaling_factor)",
            "x_label": "str - X-axis label with units",
            "y_label": "str - Y-axis label with units",
            "img_title": "str - Descriptive chart title"
        }
    },
    ChartType.PIE: {
        "required_keys": ["pie_data", "pie_labels", "pie_colors", "pie_data_category", 
                         "pie_label_category", "img_title"],
        "data_constraints": {
            "pie_data": "list[float] - Numeric values (will be converted to percentages)",
            "pie_labels": "list[str] - Slice labels",
            "pie_colors": "list[str] - Hex color codes",
            "pie_data_category": 'dict with keys "singular" and "plural" describing what data represents',
            "pie_label_category": 'dict with keys "singular" and "plural" describing the label entities',
            "img_title": "str - Descriptive chart title"
        }
    }
}


# =============================================================================
# SECTION 2: STATE DEFINITIONS FOR LANGGRAPH
# =============================================================================

@dataclass
class MasterDataRecord:
    """Raw data output from Node B (Data Fabricator)"""
    entities: list[str]           # Entity names (e.g., ["Netflix", "Disney+", ...])
    primary_values: list[float]   # Main metric values
    secondary_values: list[float] # Secondary metric (for scatter plots)
    tertiary_values: list[float]  # Tertiary metric (for scatter sizes)
    unit_primary: str             # Unit for primary values
    unit_secondary: str           # Unit for secondary values
    entity_type_singular: str     # e.g., "streaming service"
    entity_type_plural: str       # e.g., "streaming services"
    metric_name_primary: str      # e.g., "Monthly Subscribers"
    metric_name_secondary: str    # e.g., "Annual Revenue"
    statistical_properties: dict  # Trends, outliers, clusters info


class PipelineState(TypedDict):
    """Complete state object passed through the LangGraph pipeline"""
    # Node A outputs
    category_id: int
    category_name: str
    semantic_concept: str
    topic_description: str
    
    # Node B outputs
    master_data: dict  # Serialized MasterDataRecord
    
    # Node C outputs
    chart_entries: dict[str, dict]  # {chart_type: metadata_dict}
    
    # Node D outputs
    captions: dict[str, dict]  # {chart_type: {ground_truth_caption}}
    
    # Metadata
    generation_id: str
    timestamp: str
    

# =============================================================================
# SECTION 3: LLM SYSTEM PROMPTS
# =============================================================================

PROMPT_NODE_A_TOPIC_AGENT = """You are a Topic Generation Agent for a chart data synthesis pipeline.

## Your Role
Generate diverse, realistic topics for data visualization WITHIN the assigned category.

## Assigned Category (User-Specified)
**{category_name}** (ID: {category_id})

You MUST generate a topic that belongs to this category.

## Output Format
Return a JSON object with these exact keys:
{{
    "semantic_concept": "<specific topic, 3-8 words>",
    "topic_description": "<one sentence explaining what data would be visualized>",
    "suggested_entities": ["<entity1>", "<entity2>", ...],  // 8-12 entities
    "suggested_metrics": ["<metric1>", "<metric2>", "<metric3>"],  // 2-3 quantifiable metrics
    "domain_context": "<brief domain background for realistic data generation>"
}}

## Diversity Requirements (Critical: Avoid Repetitive Topics)
- Vary between micro (individual items) and macro (countries, industries) scales
- Include both well-known and obscure topics within this category
- Balance between contemporary (2020s) and timeless topics
- Consider international perspectives, not just US-centric
- Generate UNIQUE topics - avoid repeating similar concepts

## Examples of Good Semantic Concepts for Different Categories

### Media & Entertainment
- "Streaming platform subscriber growth 2020-2024"
- "Box office revenue by film genre in Asia"
- "Podcast listening hours by age demographic"

### Geography & Demography  
- "Urban population density in European capitals"
- "Migration patterns of coastal cities"
- "Median household income by region"

### Business & Industry
- "Market capitalization of semiconductor companies"
- "Supply chain disruptions by industry sector"
- "Corporate carbon emissions by Fortune 500 companies"

### Health & Medicine
- "Hospital bed capacity by metropolitan area"
- "Vaccination rates across different age groups"
- "Mental health service availability by country"

### Education & Academia
- "University research funding by discipline"
- "Student-teacher ratios in international schools"
- "Graduate employment rates by major"

### Technology & Computing
- "Cloud service market share by provider"
- "Programming language popularity trends"
- "Semiconductor chip production capacity"

## Anti-patterns to Avoid
- Generic concepts: "Sales data", "Population statistics"
- Overly broad: "Technology trends", "Economic indicators"
- Fictional: Made-up companies, imaginary species
- Repetitive: Topics too similar to recently generated ones
"""

PROMPT_NODE_B_DATA_FABRICATOR = """You are a Statistical Data Fabrication Agent specializing in generating realistic synthetic datasets.

## Your Role
Generate "Master Data" - raw numbers and entities that will be transformed into multiple chart formats.

## Input Context
Category: {category_name}
Semantic Concept: {semantic_concept}
Topic Description: {topic_description}
Suggested Entities: {suggested_entities}
Suggested Metrics: {suggested_metrics}
Domain Context: {domain_context}

## Statistical Realism Requirements

### 1. Distribution Patterns (vary these across generations)
- **Normal-ish**: Most values cluster around mean with natural variation
- **Power Law**: Few large values, many small (common in popularity metrics)
- **Bimodal**: Two distinct clusters (e.g., premium vs budget products)
- **Uniform with outliers**: Even spread with 1-2 exceptional values
- **Exponential decay**: Ranked data that drops off quickly

### 2. Value Ranges (CRITICAL for realism)
- Research typical ranges for the domain
- Example: "Streaming subscribers" → millions to hundreds of millions
- Example: "Protein per serving" → 0-50 grams
- Example: "City population" → thousands to tens of millions
- Include appropriate decimal precision (financial: 2 decimals, scientific: varies)

### 3. Correlation Patterns (for scatter-suitable data)
- **Positive correlation**: Larger X tends to have larger Y (r ≈ 0.6-0.9)
- **Negative correlation**: Inverse relationship (r ≈ -0.5 to -0.8)
- **Weak/No correlation**: Scattered with no clear pattern (r ≈ -0.2 to 0.2)
- **Non-linear**: Curved relationships (logarithmic, exponential)

### 4. Outlier Injection
- Include 1-2 natural outliers in ~30% of datasets
- Outliers should be plausible (market leaders, exceptional cases)
- Mark outliers in the statistical_properties field

## Output Format
Return a JSON object:
{{
    "entities": ["<entity1>", "<entity2>", ...],  // 8-12 entities
    "primary_values": [<val1>, <val2>, ...],      // Main metric, same length as entities
    "secondary_values": [<val1>, <val2>, ...],    // Secondary metric for scatter X or additional context
    "tertiary_values": [<val1>, <val2>, ...],     // For scatter sizes or weights
    "unit_primary": "<unit with format, e.g., '$ Million', 'kg', '%'>",
    "unit_secondary": "<unit>",
    "entity_type_singular": "<e.g., 'streaming service'>",
    "entity_type_plural": "<e.g., 'streaming services'>",
    "metric_name_primary": "<e.g., 'Monthly Active Users'>",
    "metric_name_secondary": "<e.g., 'Annual Revenue'>",
    "statistical_properties": {{
        "distribution_type": "<normal|power_law|bimodal|uniform|exponential>",
        "correlation_xy": <float -1 to 1>,  // correlation between primary and secondary
        "outlier_indices": [<indices of outlier entities>],
        "trend_description": "<brief description of data pattern>",
        "data_year": "<year or range, e.g., '2024' or '2020-2024'>"
    }}
}}

## Quality Checklist
✓ Values are within realistic domain ranges
✓ Entity names are real and recognizable (or plausibly real for obscure domains)
✓ Statistical properties match the distribution_type
✓ All arrays have the same length
✓ No duplicate entities
"""

PROMPT_NODE_C_SCHEMA_MAPPER = """You are a Schema Mapping Agent that transforms raw data into strict chart metadata formats.

## Your Role
Take Master Data and produce valid metadata dictionaries for BAR, SCATTER, and PIE chart types.

## Input Master Data
{master_data_json}

## CRITICAL: Exact Schema Specifications

### BAR Chart Schema
```json
{{
    "bar_data": [<float>, ...],           // Primary values, 8-12 items
    "bar_labels": ["<str>", ...],         // Entity names, same length
    "bar_colors": ["#RRGGBB", ...],       // Hex colors, same length, visually distinct
    "x_label": "<str>",                   // Describes the entities (e.g., "Streaming Services")
    "y_label": "<str>",                   // Metric + unit (e.g., "Subscribers (Millions)")
    "img_title": "<str>"                  // Descriptive title (e.g., "Top Streaming Platforms by Subscriber Count")
}}
```

### SCATTER Chart Schema
```json
{{
    "scatter_x_data": [<float>, ...],     // Secondary values as X coordinates
    "scatter_y_data": [<float>, ...],     // Primary values as Y coordinates
    "scatter_labels": ["<str>", ...],     // Entity names
    "scatter_colors": ["#RRGGBB", ...],   // Hex colors
    "scatter_sizes": [<float>, ...],      // Tertiary values * scaling_factor (aim for 50-500 range)
    "x_label": "<str>",                   // X-axis: secondary metric + unit
    "y_label": "<str>",                   // Y-axis: primary metric + unit  
    "img_title": "<str>"                  // Title showing relationship (e.g., "Revenue vs User Base")
}}
```

### PIE Chart Schema
```json
{{
    "pie_data": [<float>, ...],           // Primary values (will auto-convert to %)
    "pie_labels": ["<str>", ...],         // Entity names
    "pie_colors": ["#RRGGBB", ...],       // Hex colors
    "pie_data_category": {{
        "singular": "<what one slice represents>",
        "plural": "<what all slices represent>"
    }},
    "pie_label_category": {{
        "singular": "<entity type singular>",
        "plural": "<entity type plural>"
    }},
    "img_title": "<str>"                  // Title (e.g., "Market Share of Streaming Services")
}}
```

## Color Palette Guidelines
Use visually distinct, accessible colors. Suggested palettes:
- Categorical: ["#0088FE", "#00C49F", "#FFBB28", "#FF8042", "#8884D8", "#82CA9D", "#FFC658", "#FF6B9D", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7"]
- Sequential warm: ["#FFF5F0", "#FEE0D2", "#FCBBA1", "#FC9272", "#FB6A4A", "#EF3B2C", "#CB181D", "#A50F15", "#67000D"]
- Branded (if applicable): Match known brand colors for recognizable entities

## Scatter Size Calculation
scatter_sizes = [tertiary_value * scaling_factor for each entity]
Choose scaling_factor so sizes range roughly 50-500:
- If tertiary max < 10: scaling_factor ≈ 50-100
- If tertiary max 10-100: scaling_factor ≈ 10-50
- If tertiary max > 100: scaling_factor ≈ 1-10

## Output Format
Return a JSON object with three keys:
{{
    "bar": {{ <bar schema fields> }},
    "scatter": {{ <scatter schema fields> }},
    "pie": {{ <pie schema fields> }}
}}

## Validation Checklist (MUST pass all)
✓ All arrays within each chart have identical length
✓ All color codes are valid 6-digit hex with # prefix
✓ pie_data_category and pie_label_category both have "singular" and "plural" keys
✓ Labels are human-readable (no underscores, proper capitalization)
✓ Titles are descriptive and grammatically correct
✓ Units are consistently formatted (e.g., always "$ Million" not "$M" or "Million $")
"""

PROMPT_NODE_D_RL_CAPTIONER = """You are an RL Caption Generation Agent that produces training data for chart understanding models.

## Your Role
Generate a ground truth caption for the chart - an accurate, comprehensive description.

## Input Chart Metadata
Chart Type: {chart_type}
Metadata: {chart_metadata_json}

## Output Specifications

### Ground Truth Caption
A factual description covering:
- What the chart shows (topic, entities, metrics)
- Key insights (highest/lowest values, notable patterns)
- Quantitative details (specific numbers for top 2-3 items)
- Overall trend or distribution pattern

Length: 2-4 sentences, 50-100 words

## Output Format
Return a JSON object with only the ground truth caption:
{{
    "ground_truth_caption": "<accurate description>"
}}

## Quality Requirements
- Caption must be 100% accurate to the input data
- Include specific numerical values for top performers
- Describe the overall pattern or distribution
- Be concise but comprehensive
"""


# =============================================================================
# SECTION 4: NODE IMPLEMENTATIONS
# =============================================================================

class NodeA_TopicAgent:
    """
    Node A: Topic Concept Generation (User-Specified Category Version)
    
    Improvements over old implementation:
    - User MUST manually specify category_id and category_name
    - LLM no longer selects category, but generates diverse topics within specified category
    - Maintains diversity tracker to ensure topic variety in batch generation
    
    Responsibilities:
    - Generate semantic concept within user-specified category
    - Provide entity and metric suggestions
    - Provide domain context for Node B
    """
    
    def __init__(self, llm_client, diversity_tracker: Optional[dict] = None):
        self.llm = llm_client
        self.diversity_tracker = diversity_tracker or {
            "used_concepts": [],      # Previously used concepts
            "used_entities": []        # Previously used entity types
        }
    
    def get_system_prompt(self, category_id: int, category_name: str) -> str:
        """Generate system prompt for specified category"""
        return PROMPT_NODE_A_TOPIC_AGENT.format(
            category_id=category_id,
            category_name=category_name
        )
    
    def get_user_prompt(self, constraints: Optional[dict] = None) -> str:
        """Generate user prompt with constraints and diversity hints"""
        prompt = "Generate a new, unique topic for chart data synthesis within the assigned category."
        
        # Add constraints
        if constraints:
            if constraints.get("avoid_concepts"):
                recent_concepts = constraints["avoid_concepts"][-10:]  # Last 10
                if recent_concepts:
                    prompt += f"\n\n**AVOID these recently used concepts:**\n"
                    for concept in recent_concepts:
                        prompt += f"- {concept}\n"
            
            if constraints.get("theme_hint"):
                prompt += f"\n\n**Theme suggestion:** {constraints['theme_hint']}"
            
            if constraints.get("scale_preference"):
                prompt += f"\n\n**Scale preference:** {constraints['scale_preference']}"
        
        # Add diversity hints based on tracker
        recent_concepts = self.diversity_tracker.get("used_concepts", [])[-15:]
        if recent_concepts:
            prompt += f"\n\n**Recently generated concepts (for diversity):**"
            prompt += f"\n{', '.join(recent_concepts[-5:])}"
            prompt += f"\n\nGenerate something DIFFERENT from these."
        
        return prompt
    
    def validate_output(self, response: dict, category_name: str) -> tuple[bool, list[str]]:
        """Validate Node A output"""
        errors = []
        
        # Check required fields
        required_fields = [
            "semantic_concept", "topic_description", 
            "suggested_entities", "suggested_metrics", "domain_context"
        ]
        
        for field in required_fields:
            if field not in response:
                errors.append(f"Missing required field: {field}")
        
        # Check data types
        if "suggested_entities" in response:
            if not isinstance(response["suggested_entities"], list):
                errors.append("suggested_entities must be a list")
            elif len(response["suggested_entities"]) < 8:
                errors.append(f"Need at least 8 entities, got {len(response['suggested_entities'])}")
        
        if "suggested_metrics" in response:
            if not isinstance(response["suggested_metrics"], list):
                errors.append("suggested_metrics must be a list")
            elif len(response["suggested_metrics"]) < 2:
                errors.append("Need at least 2 metrics")
        
        # Check for topic repetition
        semantic_concept = response.get("semantic_concept", "")
        recent_concepts = self.diversity_tracker.get("used_concepts", [])[-10:]
        
        for recent in recent_concepts:
            # Simple similarity check (can be improved with more sophisticated algorithms)
            if semantic_concept.lower() in recent.lower() or recent.lower() in semantic_concept.lower():
                errors.append(f"Concept too similar to recent: '{recent}'")
                break
        
        return len(errors) == 0, errors
    
    def __call__(
        self, 
        state: PipelineState, 
        category_id: int,
        category_name: str,
        constraints: Optional[dict] = None
    ) -> PipelineState:
        """
        Execute Node A and update state
        
        Args:
            state: Pipeline state object
            category_id: User-specified category ID (1-30)
            category_name: User-specified category name
            constraints: Optional constraints
                - avoid_concepts: list[str] - Concepts to avoid
                - theme_hint: str - Theme suggestion
                - scale_preference: str - Scale preference ("micro", "macro")
        
        Returns:
            Updated PipelineState
        """
        # Validate category
        if not 1 <= category_id <= 30:
            raise ValueError(
                f"Invalid category_id: {category_id}. Must be between 1 and 30."
            )
        
        if category_name not in META_CATEGORIES:
            raise ValueError(
                f"Invalid category_name: {category_name}. "
                f"Must be one of the 30 predefined categories."
            )
        
        # Prepare constraints (including info from diversity tracker)
        full_constraints = constraints or {}
        if "avoid_concepts" not in full_constraints:
            full_constraints["avoid_concepts"] = self.diversity_tracker.get("used_concepts", [])
        
        # Call LLM to generate topic
        response = self.llm.generate_json(
            system=self.get_system_prompt(category_id, category_name),
            user=self.get_user_prompt(full_constraints)
        )
        
        # Validate output
        is_valid, errors = self.validate_output(response, category_name)
        if not is_valid:
            # Warning but don't interrupt (allow to continue)
            print(f"Warning: Node A validation issues: {errors}")
        
        # Update diversity tracker
        self.diversity_tracker["used_concepts"].append(
            response.get("semantic_concept", "")
        )
        self.diversity_tracker["used_entities"].extend(
            response.get("suggested_entities", [])[:3]  # Only track first 3
        )
        
        # Update state (user-provided category + LLM-generated topic)
        state["category_id"] = category_id
        state["category_name"] = category_name
        state["semantic_concept"] = response.get("semantic_concept", "")
        state["topic_description"] = response.get("topic_description", "")
        
        # Store additional info for Node B (underscore prefix indicates internal variable)
        state["_suggested_entities"] = response.get("suggested_entities", [])
        state["_suggested_metrics"] = response.get("suggested_metrics", [])
        state["_domain_context"] = response.get("domain_context", "")
        
        return state


class NodeB_DataFabricator:
    """
    Node B: Statistical Data Generation
    
    Responsibilities:
    - Generate realistic entity names
    - Produce statistically valid numeric data
    - Ensure domain-appropriate value ranges
    - Inject controlled statistical properties
    """
    
    def __init__(self, llm_client):
        self.llm = llm_client
    
    def get_system_prompt(self) -> str:
        return PROMPT_NODE_B_DATA_FABRICATOR
    
    def get_user_prompt(self, state: PipelineState) -> str:
        return PROMPT_NODE_B_DATA_FABRICATOR.format(
            category_name=state["category_name"],
            semantic_concept=state["semantic_concept"],
            topic_description=state["topic_description"],
            suggested_entities=state.get("suggested_entities", []),
            suggested_metrics=state.get("suggested_metrics", []),
            domain_context=state.get("domain_context", "")
        )
    
    def validate_output(self, data: dict) -> tuple[bool, list[str]]:
        """Validate fabricated data meets requirements"""
        errors = []
        
        # Check array lengths match
        n_entities = len(data.get("entities", []))
        for key in ["primary_values", "secondary_values", "tertiary_values"]:
            if len(data.get(key, [])) != n_entities:
                errors.append(f"{key} length mismatch: expected {n_entities}, got {len(data.get(key, []))}")
        
        # Check value types
        for key in ["primary_values", "secondary_values", "tertiary_values"]:
            if not all(isinstance(v, (int, float)) for v in data.get(key, [])):
                errors.append(f"{key} contains non-numeric values")
        
        # Check required string fields
        for key in ["unit_primary", "unit_secondary", "entity_type_singular", 
                    "entity_type_plural", "metric_name_primary", "metric_name_secondary"]:
            if not isinstance(data.get(key), str) or not data.get(key):
                errors.append(f"Missing or invalid {key}")
        
        # Check statistical_properties
        props = data.get("statistical_properties", {})
        required_props = ["distribution_type", "trend_description"]
        for prop in required_props:
            if prop not in props:
                errors.append(f"Missing statistical_properties.{prop}")
        
        return len(errors) == 0, errors
    
    def __call__(self, state: PipelineState) -> PipelineState:
        """Execute Node B and update state"""
        system_prompt = PROMPT_NODE_B_DATA_FABRICATOR.format(
            category_name=state.get("category_name", ""),
            semantic_concept=state.get("semantic_concept", ""),
            topic_description=state.get("topic_description", ""),
            suggested_entities=state.get("_suggested_entities", []),
            suggested_metrics=state.get("_suggested_metrics", []),
            domain_context=state.get("_domain_context", "")
        )
        
        response = self.llm.generate_json(
            system=system_prompt,
            user="Generate the master data now."
        )
        
        # Validate output
        is_valid, errors = self.validate_output(response)
        if not is_valid:
            raise ValueError(f"Node B validation failed: {errors}")
        
        state["master_data"] = response
        return state


class NodeC_SchemaMapper:
    """
    Node C: One-to-Many Schema Transformation
    
    The CORE logic that transforms a single Master Data record
    into three valid chart metadata dictionaries.
    
    Responsibilities:
    - Transform data to BAR schema
    - Transform data to SCATTER schema  
    - Transform data to PIE schema
    - Ensure strict schema compliance
    - Generate appropriate color palettes
    """
    
    # Default color palette for generation
    DEFAULT_COLORS = [
        "#0088FE", "#00C49F", "#FFBB28", "#FF8042", "#8884D8",
        "#82CA9D", "#FFC658", "#FF6B9D", "#4ECDC4", "#45B7D1",
        "#96CEB4", "#FFEAA7", "#DDA0DD", "#98D8C8", "#F7DC6F"
    ]
    
    def __init__(self, llm_client):
        self.llm = llm_client
    
    def get_system_prompt(self) -> str:
        return PROMPT_NODE_C_SCHEMA_MAPPER
    
    def get_user_prompt(self, state: PipelineState) -> str:
        return f"Transform this Master Data into BAR, SCATTER, and PIE chart schemas:\n\n{json.dumps(state['master_data'], indent=2)}"
    
    def transform_to_bar(self, master_data: dict) -> dict:
        """Direct transformation to BAR schema (fallback/validation)"""
        n = len(master_data["entities"])
        colors = self.DEFAULT_COLORS[:n]
        
        return {
            "bar_data": master_data["primary_values"],
            "bar_labels": master_data["entities"],
            "bar_colors": colors,
            "x_label": master_data["entity_type_plural"].title(),
            "y_label": f"{master_data['metric_name_primary']} ({master_data['unit_primary']})",
            "img_title": f"{master_data['metric_name_primary']} by {master_data['entity_type_singular'].title()}"
        }
    
    def transform_to_scatter(self, master_data: dict) -> dict:
        """Direct transformation to SCATTER schema (fallback/validation)"""
        n = len(master_data["entities"])
        colors = self.DEFAULT_COLORS[:n]
        
        # Calculate appropriate size scaling
        tertiary = master_data["tertiary_values"]
        max_tertiary = max(tertiary) if tertiary else 1
        if max_tertiary < 10:
            scale = 60
        elif max_tertiary < 100:
            scale = 20
        else:
            scale = 5
        
        return {
            "scatter_x_data": master_data["secondary_values"],
            "scatter_y_data": master_data["primary_values"],
            "scatter_labels": master_data["entities"],
            "scatter_colors": colors,
            "scatter_sizes": [v * scale for v in tertiary],
            "x_label": f"{master_data['metric_name_secondary']} ({master_data['unit_secondary']})",
            "y_label": f"{master_data['metric_name_primary']} ({master_data['unit_primary']})",
            "img_title": f"{master_data['metric_name_primary']} vs {master_data['metric_name_secondary']}"
        }
    
    def transform_to_pie(self, master_data: dict) -> dict:
        """Direct transformation to PIE schema (fallback/validation)"""
        n = len(master_data["entities"])
        colors = self.DEFAULT_COLORS[:n]
        
        return {
            "pie_data": master_data["primary_values"],
            "pie_labels": master_data["entities"],
            "pie_colors": colors,
            "pie_data_category": {
                "singular": master_data["entity_type_singular"],
                "plural": master_data["entity_type_plural"]
            },
            "pie_label_category": {
                "singular": master_data["entity_type_singular"],
                "plural": master_data["entity_type_plural"]
            },
            "img_title": f"Distribution of {master_data['metric_name_primary']} by {master_data['entity_type_singular'].title()}"
        }
    
    def validate_bar_schema(self, data: dict) -> tuple[bool, list[str]]:
        """Validate BAR chart schema"""
        errors = []
        required = ["bar_data", "bar_labels", "bar_colors", "x_label", "y_label", "img_title"]
        
        for key in required:
            if key not in data:
                errors.append(f"Missing required key: {key}")
        
        if errors:
            return False, errors
        
        n = len(data["bar_data"])
        if len(data["bar_labels"]) != n:
            errors.append(f"bar_labels length mismatch")
        if len(data["bar_colors"]) != n:
            errors.append(f"bar_colors length mismatch")
        
        # Validate hex colors
        import re
        hex_pattern = re.compile(r'^#[0-9A-Fa-f]{6}$')
        for i, color in enumerate(data["bar_colors"]):
            if not hex_pattern.match(color):
                errors.append(f"Invalid hex color at index {i}: {color}")
        
        return len(errors) == 0, errors
    
    def validate_scatter_schema(self, data: dict) -> tuple[bool, list[str]]:
        """Validate SCATTER chart schema"""
        errors = []
        required = ["scatter_x_data", "scatter_y_data", "scatter_labels", 
                    "scatter_colors", "scatter_sizes", "x_label", "y_label", "img_title"]
        
        for key in required:
            if key not in data:
                errors.append(f"Missing required key: {key}")
        
        if errors:
            return False, errors
        
        n = len(data["scatter_x_data"])
        for key in ["scatter_y_data", "scatter_labels", "scatter_colors", "scatter_sizes"]:
            if len(data[key]) != n:
                errors.append(f"{key} length mismatch")
        
        return len(errors) == 0, errors
    
    def validate_pie_schema(self, data: dict) -> tuple[bool, list[str]]:
        """Validate PIE chart schema"""
        errors = []
        required = ["pie_data", "pie_labels", "pie_colors", 
                    "pie_data_category", "pie_label_category", "img_title"]
        
        for key in required:
            if key not in data:
                errors.append(f"Missing required key: {key}")
        
        if errors:
            return False, errors
        
        n = len(data["pie_data"])
        if len(data["pie_labels"]) != n:
            errors.append("pie_labels length mismatch")
        if len(data["pie_colors"]) != n:
            errors.append("pie_colors length mismatch")
        
        # Validate category dicts
        for cat_key in ["pie_data_category", "pie_label_category"]:
            cat = data[cat_key]
            if not isinstance(cat, dict):
                errors.append(f"{cat_key} must be a dict")
            elif "singular" not in cat or "plural" not in cat:
                errors.append(f"{cat_key} must have 'singular' and 'plural' keys")
        
        return len(errors) == 0, errors
    
    def __call__(self, state: PipelineState) -> PipelineState:
        """Execute Node C and update state"""
        master_data = state.get("master_data", {})
        
        system_prompt = PROMPT_NODE_C_SCHEMA_MAPPER.format(
            master_data_json=json.dumps(master_data, indent=2)
        )
        
        response = self.llm.generate_json(
            system=system_prompt,
            user=f"Transform this Master Data into BAR, SCATTER, and PIE chart schemas:\n\n{json.dumps(master_data, indent=2)}"
        )
        
        # Validate each schema
        for chart_type, validator in [
            ("bar", self.validate_bar_schema),
            ("scatter", self.validate_scatter_schema),
            ("pie", self.validate_pie_schema)
        ]:
            if chart_type in response:
                is_valid, errors = validator(response[chart_type])
                if not is_valid:
                    # Try to use fallback transformation
                    if chart_type == "bar":
                        response[chart_type] = self.transform_to_bar(master_data)
                    elif chart_type == "scatter":
                        response[chart_type] = self.transform_to_scatter(master_data)
                    elif chart_type == "pie":
                        response[chart_type] = self.transform_to_pie(master_data)
        
        state["chart_entries"] = response
        return state


class NodeD_RLCaptioner:
    """
    Node D: RL-Ready Caption Generation
    
    Responsibilities:
    - Generate ground truth captions
    - Produce Chain-of-Thought reasoning traces
    - Create hard negative captions for contrastive learning
    """
    
    def __init__(self, llm_client):
        self.llm = llm_client
    
    def get_system_prompt(self) -> str:
        return PROMPT_NODE_D_RL_CAPTIONER
    
    def get_user_prompt(self, chart_type: str, chart_metadata: dict) -> str:
        return PROMPT_NODE_D_RL_CAPTIONER.format(
            chart_type=chart_type.upper(),
            chart_metadata_json=json.dumps(chart_metadata, indent=2)
        )
    
    def validate_output(self, data: dict) -> tuple[bool, list[str]]:
        """Validate caption output structure"""
        errors = []
        
        if "ground_truth_caption" not in data:
            errors.append("Missing ground_truth_caption")
        elif not isinstance(data["ground_truth_caption"], str):
            errors.append("ground_truth_caption must be a string")
        elif len(data["ground_truth_caption"].strip()) == 0:
            errors.append("ground_truth_caption cannot be empty")
        
        return len(errors) == 0, errors
    
    def __call__(self, state: PipelineState) -> PipelineState:
        """Execute Node D for all chart types and update state"""
        chart_entries = state.get("chart_entries", {})
        captions = {}
        
        for chart_type, metadata in chart_entries.items():
            system_prompt = PROMPT_NODE_D_RL_CAPTIONER.format(
                chart_type=chart_type.upper(),
                chart_metadata_json=json.dumps(metadata, indent=2)
            )
            
            response = self.llm.generate_json(
                system=system_prompt,
                user=f"Generate caption for this {chart_type} chart:\n\nMetadata: {json.dumps(metadata, indent=2)}"
            )
            
            # 只保留 ground_truth_caption
            cleaned_response = {
                "ground_truth_caption": response.get("ground_truth_caption", f"Chart showing {metadata.get('img_title', 'data')}")
            }
            
            # 验证输出
            is_valid, errors = self.validate_output(cleaned_response)
            if not is_valid:
                print(f"Warning: Caption validation failed for {chart_type}: {errors}")
                # 使用默认值
                cleaned_response["ground_truth_caption"] = f"Chart showing {metadata.get('img_title', 'data')}"
            
            captions[chart_type] = cleaned_response
        
        state["captions"] = captions
        return state

class ChartAgentPipeline:
    """
    Main pipeline orchestrator using LangGraph-style execution.
    
    Complete Workflow:
    Node A: Topic Generation (within user-specified category)
      ↓
    Node B: Data Fabrication (generate realistic master data)
      ↓
    Node C: Schema Mapping (transform to BAR/SCATTER/PIE formats)
      ↓
    Node D: Caption Generation (ground truth captions)
    
    Note: Category must be specified by user (no random selection).
    """
    
    def __init__(self, llm_client, config: Optional[dict] = None):
        self.config = config or {}
        
        # Initialize all nodes (complete workflow)
        self.node_a = NodeA_TopicAgent(llm_client)
        self.node_b = NodeB_DataFabricator(llm_client)
        self.node_c = NodeC_SchemaMapper(llm_client)
        self.node_d = NodeD_RLCaptioner(llm_client)
    
    def create_initial_state(self) -> PipelineState:
        """Create empty initial state"""
        return PipelineState(
            category_id=0,
            category_name="",
            semantic_concept="",
            topic_description="",
            master_data={},
            chart_entries={},
            captions={},
            generation_id=hashlib.md5(str(datetime.now()).encode()).hexdigest()[:12],
            timestamp=datetime.now().isoformat()
        )
    
    def run(self, category_id: int, constraints: Optional[dict] = None) -> PipelineState:
        """
        Execute full pipeline with user-specified category
        
        Args:
            category_id: Category ID (1-30) from META_CATEGORIES
            constraints: Optional constraints for topic generation
                - avoid_concepts: list[str] - Topics to avoid
                - theme_hint: str - Theme suggestion
                - scale_preference: str - "micro" or "macro"
        
        Returns:
            PipelineState with all generated data
        """
        # Validate category_id
        if not 1 <= category_id <= 30:
            raise ValueError(
                f"Invalid category_id: {category_id}\n"
                f"Must be between 1 and 30.\n"
                f"Use get_available_categories() to see all options."
            )
        
        category_name = META_CATEGORIES[category_id - 1]
        
        # Create initial state
        state = self.create_initial_state()
        
        # Node A: Topic Generation (within specified category)
        state = self.node_a(state, category_id, category_name, constraints)
        
        # Node B: Data Fabrication
        state = self.node_b(state)
        
        # Node C: Schema Mapping
        state = self.node_c(state)
        
        # Node D: Caption Generation
        state = self.node_d(state)
        
        return state
    
    def run_batch(
        self, 
        category_ids: list[int], 
        constraints_list: Optional[list[dict]] = None
    ) -> list[PipelineState]:
        """
        Run pipeline multiple times for batch generation
        
        Args:
            category_ids: List of category IDs (1-30), one per generation
            constraints_list: Optional list of constraints (one per generation)
        
        Returns:
            List of PipelineState objects
        """
        results = []
        constraints_list = constraints_list or [None] * len(category_ids)
        
        for i, (category_id, constraints) in enumerate(zip(category_ids, constraints_list)):
            try:
                state = self.run(category_id, constraints)
                results.append(state)
            except Exception as e:
                print(f"Generation {i} (category {category_id}) failed: {e}")
                continue
        
        return results


# =============================================================================
# SECTION 6: UNIFIED LLM CLIENT
# =============================================================================

# -----------------------------------------------------------------------------
# Provider Parameter Adapters
# -----------------------------------------------------------------------------

from dataclasses import dataclass


@dataclass
class ProviderCapabilities:
    """Define what parameters each provider supports"""
    supports_temperature: bool = True
    supports_max_tokens: bool = True
    supports_max_completion_tokens: bool = False
    supports_response_format: bool = True
    supports_json_mode: bool = True
    
    # Token parameter name to use
    token_param_name: str = "max_tokens"
    
    # Temperature constraints
    min_temperature: float = 0.0
    max_temperature: float = 2.0
    default_temperature: float = 1.0
    
    # Special handling flags
    requires_json_in_prompt: bool = False
    is_reasoning_model: bool = False


# Provider capability definitions
PROVIDER_CAPABILITIES = {
    "openai": ProviderCapabilities(
        supports_max_completion_tokens=True,
        token_param_name="max_completion_tokens",
        supports_response_format=True,
        supports_json_mode=True,
    ),
    "gemini": ProviderCapabilities(
        supports_temperature=True,
        supports_max_tokens=True,
        token_param_name="max_tokens",
        supports_response_format=False,  # Gemini via OpenAI API may not support this
        requires_json_in_prompt=True,
    ),
    "gemini-native": ProviderCapabilities(
        # Gemini native SDK uses different API structure
        supports_temperature=True,
        supports_max_tokens=True,
        token_param_name="max_tokens",
        supports_response_format=False,
        requires_json_in_prompt=True,
    ),
    "azure": ProviderCapabilities(
        supports_max_tokens=True,
        token_param_name="max_tokens",
        supports_response_format=True,
        supports_json_mode=True,
    ),
    "custom": ProviderCapabilities(
        # Conservative defaults for unknown providers
        supports_temperature=True,
        supports_max_tokens=True,
        token_param_name="max_tokens",
        supports_response_format=False,
        requires_json_in_prompt=True,
    ),
}


# Model-specific overrides (for models with special requirements)
MODEL_OVERRIDES = {
    # OpenAI reasoning models have strict parameter limitations
    "o1": ProviderCapabilities(
        supports_temperature=False,  # o1 models don't support temperature
        supports_max_completion_tokens=True,
        token_param_name="max_completion_tokens",
        supports_response_format=False,
        is_reasoning_model=True,
    ),
    "o3": ProviderCapabilities(
        supports_temperature=False,
        supports_max_completion_tokens=True,
        token_param_name="max_completion_tokens",
        supports_response_format=False,
        is_reasoning_model=True,
    ),
    "gpt-5": ProviderCapabilities(
        supports_temperature=False,  # gpt-5 does not support custom temperature
        supports_max_completion_tokens=True,
        token_param_name="max_completion_tokens",
        supports_response_format=False,
        is_reasoning_model=True,
    ),
}


def get_provider_capabilities(provider: str, model: str) -> ProviderCapabilities:
    """
    Get capability configuration for a specific provider and model.
    
    Checks model-specific overrides first, then falls back to provider defaults.
    """
    # Check for model-specific overrides
    model_lower = model.lower()
    for model_pattern, capabilities in MODEL_OVERRIDES.items():
        if model_pattern in model_lower:
            return capabilities
    
    # Fall back to provider default
    return PROVIDER_CAPABILITIES.get(provider, PROVIDER_CAPABILITIES["custom"])


class ParameterAdapter:
    """
    Adapts API call parameters to match provider capabilities.
    
    This class ensures that only supported parameters are included in API calls,
    avoiding the need for retry-based error handling.
    """
    
    def __init__(self, provider: str, model: str):
        self.provider = provider
        self.model = model
        self.capabilities = get_provider_capabilities(provider, model)
    
    def adapt_parameters(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        response_format: str = "json"
    ) -> tuple[dict, list[dict]]:
        """
        Adapt parameters to match provider capabilities.
        
        Returns:
            (kwargs, modified_messages): API call kwargs and potentially modified messages
        """
        kwargs = {
            "model": self.model,
            "messages": messages,
        }
        
        modified_messages = messages.copy()
        
        # Add temperature if supported
        if self.capabilities.supports_temperature:
            # Clamp temperature to supported range
            clamped_temp = max(
                self.capabilities.min_temperature,
                min(temperature, self.capabilities.max_temperature)
            )
            kwargs["temperature"] = clamped_temp
        
        # Add token limit parameter
        if self.capabilities.supports_max_tokens:
            kwargs[self.capabilities.token_param_name] = max_tokens
        
        # Handle JSON response format
        if response_format == "json":
            if self.capabilities.supports_json_mode and self.capabilities.supports_response_format:
                # Provider supports native JSON mode
                kwargs["response_format"] = {"type": "json_object"}
            elif self.capabilities.requires_json_in_prompt:
                # Add JSON instruction to prompt
                modified_messages = messages.copy()
                modified_messages[-1] = modified_messages[-1].copy()
                modified_messages[-1]["content"] += (
                    "\n\nRespond with valid JSON only, no markdown formatting."
                )
        
        return kwargs, modified_messages


# -----------------------------------------------------------------------------
# Unified LLM Client
# -----------------------------------------------------------------------------

class LLMClient:
    """
    Unified LLM client supporting multiple providers with proper parameter adaptation.
    
    Supported providers:
    - OpenAI: GPT-4, GPT-3.5-turbo, o1, etc.
    - Gemini: gemini-1.5-pro, gemini-2.0-flash, etc. (via OpenAI SDK)
    - Gemini Native: Using google-genai SDK
    - Azure OpenAI: Azure-hosted OpenAI models
    - Custom: Any OpenAI API-compatible service
    
    Usage:
        # OpenAI
        client = LLMClient(api_key="sk-...", model="gpt-4", provider="openai")
        
        # Gemini (via OpenAI API)
        client = LLMClient(
            api_key="your-gemini-key", 
            model="gemini-2.0-flash-lite",
            provider="gemini"
        )
        
        # Gemini (native SDK)
        client = LLMClient(
            api_key="your-gemini-key",
            model="gemini-2.0-flash-lite", 
            provider="gemini-native"
        )
    """
    
    def __init__(
        self, 
        api_key: str, 
        model: str = "gemini-2.0-flash-lite",
        base_url: Optional[str] = None,
        provider: str = "auto"
    ):
        """
        Initialize LLM client with automatic parameter adaptation.
        
        Args:
            api_key: API key for the provider
            model: Model name
            base_url: Custom API endpoint URL (optional)
            provider: Provider type ("auto", "openai", "gemini", "gemini-native", "azure", "custom")
        """
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self._client = None
        self._native_client = None
        
        # Auto-detect provider from model name if needed
        if provider == "auto":
            # FIXME：If model name contains "gemini", now will go to gemini-native, might use Gemini via OpenAI API in the future
            if "gemini" in model.lower():
                self.provider = "gemini-native"  # Default to native SDK
            elif "gpt" in model.lower() or "o1" in model.lower() or "o3" in model.lower():
                self.provider = "openai"
            elif "claude" in model.lower():
                self.provider = "openai"  # Claude via compatibility layer
            else:
                self.provider = "custom"
        else:
            self.provider = provider
        
        # Initialize parameter adapter
        self.adapter = ParameterAdapter(self.provider, self.model)
        
        # Set base URL based on provider
        if self.provider == "gemini":
            # Gemini via OpenAI SDK
            if not self.base_url:
                self.base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
        elif self.provider == "gemini-native":
            # Native Gemini SDK doesn't use base_url
            self.base_url = None
        elif self.provider == "openai" and not self.base_url:
            self.base_url = "https://api.openai.com/v1"
    
    def _ensure_client(self):
        """Lazy initialization of API client"""
        if self.provider == "gemini-native":
            # Use native Gemini SDK
            if self._native_client is None:
                try:
                    from google import genai
                    self._native_client = genai.Client(api_key=self.api_key)
                except ImportError:
                    raise ImportError(
                        "Please install google-genai for native Gemini support: "
                        "pip install google-genai"
                    )
        else:
            # Use OpenAI SDK for all other providers
            if self._client is None:
                try:
                    from openai import OpenAI
                    self._client = OpenAI(
                        api_key=self.api_key,
                        base_url=self.base_url
                    )
                except ImportError:
                    raise ImportError(
                        "Please install openai SDK: pip install openai>=1.0.0"
                    )
    
    def generate(
        self, 
        system: str, 
        user: str, 
        temperature: float = 0.7,
        max_tokens: int = 4096, 
        response_format: str = "json"
    ) -> str:
        """
        Generate text response using the configured LLM.
        
        Parameters are automatically adapted to match provider capabilities.
        
        Args:
            system: System prompt
            user: User prompt
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum response length
            response_format: "json" or "text"
        
        Returns:
            Generated text response
        """
        self._ensure_client()
        
        if self.provider == "gemini-native":
            # Use Gemini native SDK
            full_prompt = f"{system}\n\n---\n\n{user}"
            
            # Prepare generation config
            generation_config = {}
            if self.adapter.capabilities.supports_temperature:
                generation_config["temperature"] = temperature
            if self.adapter.capabilities.supports_max_tokens:
                generation_config["max_output_tokens"] = max_tokens
            
            # Add JSON instruction if needed
            if response_format == "json" and self.adapter.capabilities.requires_json_in_prompt:
                full_prompt += "\n\nRespond with valid JSON only, no markdown formatting."
            
            response = self._native_client.models.generate_content(
                model=self.model,
                contents=full_prompt,
                config=generation_config
            )
            
            return response.text
        else:
            # Use OpenAI SDK (for OpenAI, Gemini via OpenAI API, Azure, etc.)
            messages = [
                {"role": "system", "content": system},
                {"role": "user", "content": user}
            ]
            
            # Use parameter adapter to get correct kwargs
            kwargs, modified_messages = self.adapter.adapt_parameters(
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                response_format=response_format
            )
            
            # Update kwargs with modified messages
            kwargs["messages"] = modified_messages
            
            # Single API call with properly adapted parameters (no retry needed)
            response = self._client.chat.completions.create(**kwargs)
            return response.choices[0].message.content
    
    def generate_json(self, system: str, user: str, **kwargs) -> dict:
        """Generate and parse JSON response"""
        response = self.generate(system, user, response_format="json", **kwargs)
        
        # Clean response (remove potential markdown code blocks)
        cleaned = response.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        
        try:
            return json.loads(cleaned.strip())
        except json.JSONDecodeError as e:
            # Provide detailed error information
            raise ValueError(
                f"Failed to parse JSON response from {self.provider} "
                f"(model: {self.model}). Error: {e}\n"
                f"Response preview: {cleaned[:500]}"
            )


# 为了向后兼容，保留 GeminiClient 作为别名
class GeminiClient(LLMClient):
    """
    向后兼容的 Gemini 客户端
    
    使用 Gemini 原生 SDK（google-genai）
    """
    def __init__(self, api_key: str, model: str = "gemini-2.0-flash-lite"):
        super().__init__(
            api_key=api_key,
            model=model,
            provider="gemini-native"
        )


# =============================================================================
# SECTION 7: UTILITY FUNCTIONS
# =============================================================================

def generate_unique_id(prefix: str = "gen") -> str:
    """Generate unique ID for tracking generations"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    random_suffix = hashlib.md5(str(random.random()).encode()).hexdigest()[:6]
    return f"{prefix}_{timestamp}_{random_suffix}"


def validate_category(category: str) -> bool:
    """Check if category is in valid taxonomy"""
    return category in META_CATEGORIES


def get_category_by_id(category_id: int) -> Optional[str]:
    """Get category name by ID (1-30)"""
    if 1 <= category_id <= 30:
        return META_CATEGORIES[category_id - 1]
    return None


def get_available_categories() -> list[str]:
    """
    Get list of all available categories for manual topic selection.
    
    Returns:
        List of 30 predefined category strings
    
    Example:
        >>> categories = get_available_categories()
        >>> print(categories[0])
        "1 - Media & Entertainment"
        >>> 
        >>> # Use with pipeline
        >>> pipeline.run(category=categories[0])
    """
    return META_CATEGORIES.copy()


def print_available_categories():
    """
    Print all available categories in a formatted list.
    
    Useful for interactive category selection.
    """
    print("可用的 30 个主题类别:")
    print("=" * 60)
    for i, category in enumerate(META_CATEGORIES, 1):
        print(f"{i:2d}. {category}")
    print("=" * 60)
    print("\n使用方法:")
    print("  # 使用类别编号 (1-30)")
    print("  pipeline.run(category_id=1)  # Media & Entertainment")
    print("  ")
    print("  # 批量生成，指定多个类别")
    print("  pipeline.run_batch(category_ids=[1, 4, 10, 15])")
    print("  ")
    print("  # 在 example_runner.py 中使用")
    print("  python example_runner.py --category 1 --count 5")


def format_for_metadata_file(chart_type: str, func_id: str, category: str, entry: dict) -> str:
    """Format a single entry for insertion into metadata.py"""
    entry_str = json.dumps(entry, indent=12)
    # Adjust indentation for nested structure
    lines = entry_str.split('\n')
    formatted_lines = [lines[0]] + ['        ' + line for line in lines[1:]]
    return '\n'.join(formatted_lines)


if __name__ == "__main__":
    # Example usage demonstration
    print("ChartAgentVAGEN Pipeline Architecture")
    print("=" * 50)
    print(f"Categories: {len(META_CATEGORIES)}")
    print(f"Chart Types: {[ct.value for ct in ChartType]}")
    print("\nTo use this pipeline:")
    print("1. Initialize LLMClient or GeminiClient with your API key")
    print("2. Create ChartAgentPipeline instance")
    print("3. Call pipeline.run() or pipeline.run_batch()")
    print("\nSupported LLM providers:")
    print("- OpenAI (GPT-4, GPT-3.5)")
    print("- Google Gemini (via native SDK or OpenAI-compatible API)")
    print("- Azure OpenAI")
    print("- Custom endpoints (any OpenAI-compatible service)")
