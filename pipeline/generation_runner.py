"""
ChartAgentVAGEN - Complete Working Example
===========================================

This module demonstrates the full pipeline with LLM API integration.

Setup:
    1. Install dependencies: pip install -r requirements.txt
    2. Configure API key in .env file:
       # For Gemini
       GEMINI_API_KEY=your-gemini-key-here
       GEMINI_MODEL=gemini-2.0-flash-lite
       
       # For OpenAI
       OPENAI_API_KEY=your-openai-key-here
       OPENAI_MODEL=gpt-4-turbo

Usage:
    # List all available categories:
    python example_runner.py --list-categories
    
    # Generate 5 samples from category 1 (Media & Entertainment):
    python example_runner.py --category 1 --count 5
    
    # Generate from multiple specific categories:
    python example_runner.py --categories 1,4,10,15
    
    # Use Gemini with specific category:
    python example_runner.py --provider gemini --category 10 --count 3
"""

import json
import os
import random
from datetime import datetime
from typing import Optional

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()  # Load .env file from current directory
except ImportError:
    print("Warning: python-dotenv not installed. Install with: pip install python-dotenv")
    print("Falling back to system environment variables...")

# Import from our pipeline modules
from generation_pipeline import (
    META_CATEGORIES,
    LLMClient, GeminiClient, generate_unique_id,
    PROMPT_NODE_A_TOPIC_AGENT, PROMPT_NODE_B_DATA_FABRICATOR, 
    PROMPT_NODE_C_SCHEMA_MAPPER, PROMPT_NODE_D_RL_CAPTIONER,
    get_available_categories, print_available_categories
)


# =============================================================================
# LLM CONFIGURATION HELPER
# =============================================================================

# Provider configuration mapping
PROVIDER_CONFIGS = {
    "openai": {
        "env_model_key": "OPENAI_MODEL",
        "default_model": "gpt-5-mini-2025-08-07",
        "env_api_key": "OPENAI_API_KEY",
        "model_patterns": ["gpt", "o1"],
    },
    "gemini": {
        "env_model_key": "GEMINI_MODEL",
        "default_model": "gemini-2.0-flash-lite",
        "env_api_key": "GEMINI_API_KEY",
        "model_patterns": ["gemini"],
    },
    "gemini-native": {
        "env_model_key": "GEMINI_MODEL",
        "default_model": "gemini-2.0-flash-lite",
        "env_api_key": "GEMINI_API_KEY",
        "model_patterns": ["gemini"],
    },
    "azure": {
        "env_model_key": "AZURE_OPENAI_MODEL",
        "default_model": "gpt-4o",
        "env_api_key": "AZURE_OPENAI_API_KEY",
        "model_patterns": ["gpt"],
    },
}

# Default provider
DEFAULT_PROVIDER = "openai"


def infer_provider_from_model(model_name: str) -> str:
    """Infer provider from model name"""
    model_lower = model_name.lower()
    
    for provider, config in PROVIDER_CONFIGS.items():
        for pattern in config["model_patterns"]:
            if pattern in model_lower:
                return provider
    
    # If cannot infer, return default provider
    return DEFAULT_PROVIDER


def resolve_llm_config(args) -> tuple[str, str, str]:
    """
    Unified LLM configuration resolver. Returns (provider, model, api_key)
    
    Priority logic:
    1. Provider determination:
       - If --provider is specified and not "auto", use specified provider
       - If --model is specified, infer provider from model name
       - Otherwise use default provider (openai)
    
    2. Model determination:
       - If --model is specified, use specified model
       - Otherwise read from environment variable or default config
    
    3. API Key determination:
       - If --api-key is specified, use specified api_key
       - Otherwise read from corresponding provider's environment variable
    """
    
    # Step 1: Determine provider
    if args.provider and args.provider != "auto":
        # Explicitly specified provider (highest priority)
        provider = args.provider
    elif args.model:
        # Infer provider from model name
        provider = infer_provider_from_model(args.model)
    else:
        # Use default provider
        provider = DEFAULT_PROVIDER
    
    # Validate provider support
    if provider not in PROVIDER_CONFIGS and provider != "custom":
        raise ValueError(
            f"Unsupported provider: {provider}\n"
            f"Supported options: {', '.join(list(PROVIDER_CONFIGS.keys()) + ['custom'])}"
        )
    
    # Get provider configuration
    config = PROVIDER_CONFIGS.get(provider, {
        "env_model_key": "MODEL_NAME",
        "default_model": "unknown-model",
        "env_api_key": "API_KEY",
    })
    
    # Step 2: Determine model
    if args.model:
        model = args.model
    else:
        # Read from environment variable or use default
        model = os.environ.get(config["env_model_key"], config["default_model"])
    
    # Step 3: Determine api_key
    if args.api_key:
        api_key = args.api_key
    else:
        api_key = os.environ.get(config["env_api_key"])
    
    return provider, model, api_key


# =============================================================================
# COMPLETE PIPELINE RUNNER
# =============================================================================

class ChartAgentPipelineRunner:
    """
    Complete pipeline runner that integrates all nodes.
    
    Uses the ChartAgentPipeline orchestrator which coordinates:
    - NodeA_TopicAgent (generates topic within user-specified category)
    - NodeB_DataFabricator (generates realistic master data)
    - NodeC_SchemaMapper (transforms to BAR/SCATTER/PIE formats)
    - NodeD_RLCaptioner (generates ground truth captions)
    
    Complete workflow with Node A integrated for topic diversity control.
    """
    
    def __init__(self, llm_client, verbose: bool = True):
        self.llm = llm_client
        self.verbose = verbose
        
        # Initialize the pipeline with all Node classes
        from generation_pipeline import ChartAgentPipeline
        self.pipeline = ChartAgentPipeline(llm_client)
    
    def log(self, message: str):
        if self.verbose:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
    
    def run_single(self, category_id: int, constraints: Optional[dict] = None) -> dict:
        """
        Run the complete pipeline once with specified category.
        
        Uses step-by-step execution with real-time logging to show progress
        and timing for each node.
        
        Args:
            category_id: Category ID (1-30) from META_CATEGORIES
            constraints: Optional constraints for topic generation
        
        Returns:
            Complete pipeline output with all chart types and captions
        """
        import time
        
        generation_id = generate_unique_id("gen")
        pipeline_start = time.time()
        self.log(f"Starting generation {generation_id}")
        
        # Validate category_id
        if not 1 <= category_id <= 30:
            raise ValueError(f"Invalid category_id: {category_id}. Must be between 1 and 30.")
        
        category_name = META_CATEGORIES[category_id - 1]
        self.log(f"Category: {category_name}")
        
        # Initialize pipeline state
        state = self.pipeline.create_initial_state()
        
        # ===== Node A: Topic Generation =====
        self.log(f"  → Node A: Generating topic concept...")
        node_start = time.time()
        state = self.pipeline.node_a(state, category_id, category_name, constraints)
        node_time = time.time() - node_start
        self.log(f"  ✓ Node A completed in {node_time:.1f}s")
        self.log(f"    Concept: {state['semantic_concept']}")
        
        # ===== Node B: Data Fabrication =====
        self.log(f"  → Node B: Fabricating master data...")
        node_start = time.time()
        state = self.pipeline.node_b(state)
        node_time = time.time() - node_start
        master_data = state.get("master_data", {})
        self.log(f"  ✓ Node B completed in {node_time:.1f}s")
        self.log(f"    Entities: {len(master_data.get('entities', []))}")
        self.log(f"    Distribution: {master_data.get('statistical_properties', {}).get('distribution_type', 'unknown')}")
        
        # ===== Node C: Schema Mapping =====
        self.log(f"  → Node C: Mapping to chart schemas...")
        node_start = time.time()
        state = self.pipeline.node_c(state)
        node_time = time.time() - node_start
        self.log(f"  ✓ Node C completed in {node_time:.1f}s")
        self.log(f"    Schemas: {list(state.get('chart_entries', {}).keys())}")
        
        # ===== Node D: Caption Generation =====
        self.log(f"  → Node D: Generating captions...")
        node_start = time.time()
        state = self.pipeline.node_d(state)
        node_time = time.time() - node_start
        captions = state.get("captions", {})
        self.log(f"  ✓ Node D completed in {node_time:.1f}s")
        if captions:
            self.log(f"    Generated {len(captions)} captions")
        
        # Pipeline completion summary
        total_time = time.time() - pipeline_start
        self.log(f"  ✓ Pipeline completed in {total_time:.1f}s total")
        
        return {
            "category_id": state.get("category_id"),
            "category_name": state.get("category_name"),
            "semantic_concept": state.get("semantic_concept"),
            "topic_description": state.get("topic_description"),
            "master_data": state.get("master_data"),
            "chart_entries": state.get("chart_entries"),
            "captions": state.get("captions")
        }
    
    def run_batch(
        self, 
        category_ids: list[int],
        constraints_list: Optional[list[dict]] = None
    ) -> list[dict]:
        """
        Run pipeline multiple times with automatic topic diversity control.
        
        Args:
            category_ids: List of category IDs (1-30), one per generation
            constraints_list: Optional list of constraints (one per generation)
        
        Returns:
            List of pipeline outputs
        """
        results = []
        count = len(category_ids)
        constraints_list = constraints_list or [None] * count
        
        for i, (category_id, constraints) in enumerate(zip(category_ids, constraints_list)):
            self.log(f"\n{'='*50}")
            self.log(f"Generation {i+1}/{count}")
            self.log('='*50)
            
            try:
                result = self.run_single(category_id, constraints)
                results.append(result)
            except Exception as e:
                self.log(f"ERROR: Generation failed: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        return results
    
    def save_results(self, results: list[dict], output_path: str):
        """Save results to JSON file"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        self.log(f"Saved {len(results)} generations to {output_path}")


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="ChartAgentVAGEN Data Generation Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate 5 samples from category 1 (Media & Entertainment)
  python example_runner.py --category 1 --count 5
  
  # Generate from multiple categories
  python example_runner.py --categories 1,4,10,15
  
  # List all available categories
  python example_runner.py --list-categories
  
  # Use Gemini with specific category
  python example_runner.py --provider gemini --category 10 --count 3
  
  # Generate multiple samples from same category
  python example_runner.py --category 4 --count 10
        """
    )
    
    parser.add_argument(
        "--api-key",
        help="API key (or set GEMINI_API_KEY/OPENAI_API_KEY env var)"
    )
    
    parser.add_argument(
        "--model", "-m",
        help="Model to use (auto-detect provider from model name if not specified)",
    )
    
    parser.add_argument(
        "--provider", "-p",
        help="LLM provider (default: openai)",
        choices=["auto", "openai", "gemini", "gemini-native", "azure", "custom"],
        default="openai"
    )
    
    parser.add_argument(
        "--base-url",
        help="Custom API base URL (for self-hosted models or proxies)"
    )
    
    parser.add_argument(
        "--category", "-c",
        type=int,
        help="Category ID (1-30). Required unless using --categories or --list-categories"
    )
    
    parser.add_argument(
        "--categories",
        help="Comma-separated category IDs (e.g., '1,4,10,15'). Overrides --category and --count"
    )
    
    parser.add_argument(
        "--count", "-n",
        type=int,
        default=1,
        help="Number of generations from the specified category (default: 1). Only used with --category"
    )
    
    parser.add_argument(
        "--list-categories",
        action="store_true",
        help="List all available categories and exit"
    )
    
    parser.add_argument(
        "--output", "-o",
        default="generated_metadata.json",
        help="Output JSON file path"
    )
    
    parser.add_argument(
        "--seed",
        type=int,
        help="Random seed for reproducibility"
    )
    
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress verbose output"
    )
    
    args = parser.parse_args()
    
    # Handle --list-categories
    if args.list_categories:
        print_available_categories()
        return
    
    # Build category_ids list
    category_ids = []
    
    if args.categories:
        # Parse comma-separated category IDs
        try:
            category_ids = [int(x.strip()) for x in args.categories.split(',')]
            # Validate all category IDs
            for cid in category_ids:
                if not 1 <= cid <= 30:
                    print(f"ERROR: Invalid category ID: {cid}")
                    print("       Category IDs must be between 1 and 30")
                    print("       Use --list-categories to see all available categories")
                    return
        except ValueError:
            print("ERROR: Invalid --categories format")
            print("       Use comma-separated integers: --categories 1,4,10,15")
            return
    elif args.category:
        # Validate category ID
        if not 1 <= args.category <= 30:
            print(f"ERROR: Invalid category ID: {args.category}")
            print("       Category IDs must be between 1 and 30")
            print("       Use --list-categories to see all available categories")
            return
        # Repeat category for count times
        category_ids = [args.category] * args.count
    else:
        # No category specified
        print("ERROR: No category specified!")
        print("       Use --category <ID> or --categories <ID1,ID2,...>")
        print("       Use --list-categories to see all available categories")
        print("")
        print("Examples:")
        print("  python example_runner.py --category 1 --count 5")
        print("  python example_runner.py --categories 1,4,10,15")
        return
    
    # Set random seed
    if args.seed is not None:
        random.seed(args.seed)
    
    # Unified LLM configuration resolution
    try:
        provider, model, api_key = resolve_llm_config(args)
    except ValueError as e:
        print(f"ERROR: {e}")
        return
    
    # Check API key
    if not api_key:
        config = PROVIDER_CONFIGS.get(provider, {})
        env_key_name = config.get('env_api_key', 'API_KEY')
        
        print("ERROR: API key not found!")
        print(f"       Provider '{provider}' requires: {env_key_name}")
        print("")
        print("       Set it in one of these ways:")
        print("       1. Use --api-key command line argument")
        print(f"       2. Set {env_key_name} in .env file or environment variable")
        print("")
        print("       Example .env file:")
        print(f"       {env_key_name}=your-key-here")
        print("")
        print("       Common configurations:")
        print("       OPENAI_API_KEY=sk-...")
        print("       GEMINI_API_KEY=...")
        return
    
    # Create LLM client
    print(f"Initializing LLM client...")
    print(f"  Provider: {provider}")
    print(f"  Model: {model}")
    if args.base_url:
        print(f"  Base URL: {args.base_url}")
    
    llm = LLMClient(
        api_key=api_key,
        model=model,
        provider=provider,
        base_url=args.base_url
    )
    
    print(f"  Detected provider: {llm.provider}")
    print("")
    
    # Print category information
    if not args.quiet:
        print(f"Generating {len(category_ids)} sample(s):")
        category_counts = {}
        for cid in category_ids:
            cat_name = META_CATEGORIES[cid - 1]
            category_counts[cat_name] = category_counts.get(cat_name, 0) + 1
        
        for cat_name, count in category_counts.items():
            print(f"  - {cat_name}: {count} sample(s)")
        print("")
    
    # Run pipeline
    runner = ChartAgentPipelineRunner(llm, verbose=not args.quiet)
    results = runner.run_batch(category_ids)
    
    # Save results
    runner.save_results(results, args.output)
    
    # Print summary
    print(f"\n{'='*50}")
    print("GENERATION COMPLETE")
    print(f"{'='*50}")
    print(f"Total generations: {len(results)}")
    print(f"Output file: {args.output}")
    
    # Category distribution
    categories = [r["category_name"] for r in results]
    unique_cats = set(categories)
    print(f"Unique categories: {len(unique_cats)}")
    
    # Chart types
    total_charts = sum(len(r.get("chart_entries", {})) for r in results)
    print(f"Total chart schemas: {total_charts}")


if __name__ == "__main__":
    main()