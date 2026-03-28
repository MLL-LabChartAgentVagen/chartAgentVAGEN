"""
Smoke tests for pipeline/core/ salvaged modules.

Run from the pipeline/ directory:
    python -m core.tests.test_core_imports
"""


def test_utils():
    from core.utils import (
        META_CATEGORIES, generate_unique_id,
        validate_category, get_category_by_id, get_available_categories,
    )
    assert len(META_CATEGORIES) == 30, f"Expected 30 categories, got {len(META_CATEGORIES)}"
    uid = generate_unique_id("test")
    assert uid.startswith("test_"), f"Unexpected ID prefix: {uid}"
    assert get_category_by_id(1) == "1 - Media & Entertainment"
    assert get_category_by_id(0) is None
    assert get_category_by_id(31) is None
    assert validate_category("1 - Media & Entertainment")
    assert not validate_category("nonexistent")
    assert len(get_available_categories()) == 30
    print("✓ utils OK")


def test_llm_client():
    from core.llm_client import (
        LLMClient, GeminiClient, ParameterAdapter,
        ProviderCapabilities, get_provider_capabilities,
        PROVIDER_CAPABILITIES, MODEL_OVERRIDES,
    )
    # Check provider capabilities lookup
    caps = get_provider_capabilities("openai", "gpt-4")
    assert caps.supports_temperature is True
    assert caps.token_param_name == "max_completion_tokens"

    # Reasoning model override
    caps_o1 = get_provider_capabilities("openai", "o1-preview")
    assert caps_o1.supports_temperature is False
    assert caps_o1.is_reasoning_model is True

    # ParameterAdapter smoke test
    adapter = ParameterAdapter("openai", "gpt-4")
    msgs = [{"role": "user", "content": "hello"}]
    kwargs, modified = adapter.adapt_parameters(msgs, temperature=0.5, max_tokens=1024)
    assert kwargs["model"] == "gpt-4"
    assert kwargs["temperature"] == 0.5
    assert "max_completion_tokens" in kwargs

    # GeminiClient is subclass of LLMClient
    assert issubclass(GeminiClient, LLMClient)
    print("✓ llm_client OK")


def test_topic_agent():
    from core.topic_agent import NodeA_TopicAgent, PROMPT_NODE_A_TOPIC_AGENT
    assert "{category_name}" in PROMPT_NODE_A_TOPIC_AGENT
    assert "{category_id}" in PROMPT_NODE_A_TOPIC_AGENT

    # Instantiate with a mock LLM (no API call)
    agent = NodeA_TopicAgent(llm_client=None)
    assert agent.diversity_tracker["used_concepts"] == []

    # Test prompt generation
    sys_prompt = agent.get_system_prompt(1, "1 - Media & Entertainment")
    assert "Media & Entertainment" in sys_prompt

    user_prompt = agent.get_user_prompt()
    assert "unique topic" in user_prompt.lower()

    # Test validator
    good_response = {
        "semantic_concept": "Test Concept",
        "topic_description": "A test",
        "suggested_entities": [f"e{i}" for i in range(8)],
        "suggested_metrics": ["m1", "m2"],
        "domain_context": "context",
    }
    valid, errors = agent.validate_output(good_response, "1 - Media & Entertainment")
    assert valid, f"Expected valid, got errors: {errors}"

    bad_response = {"semantic_concept": "Test"}
    valid, errors = agent.validate_output(bad_response, "1 - Media & Entertainment")
    assert not valid
    print("✓ topic_agent OK")


def test_pipeline_runner():
    from core.pipeline_runner import (
        ChartAgentPipelineRunner, PROVIDER_CONFIGS,
        infer_provider_from_model, DEFAULT_PROVIDER,
    )
    assert "openai" in PROVIDER_CONFIGS
    assert "gemini" in PROVIDER_CONFIGS
    assert infer_provider_from_model("gpt-4o") == "openai"
    assert infer_provider_from_model("gemini-2.0-flash") == "gemini"
    assert DEFAULT_PROVIDER == "openai"
    print("✓ pipeline_runner OK")


def test_basic_operators():
    import pandas as pd
    from core.basic_operators import Filter, Project, GroupBy, Sort, Limit, Chain

    df = pd.DataFrame({
        "name": ["Alice", "Bob", "Carol", "Dave"],
        "score": [90, 80, 95, 70],
        "dept": ["eng", "eng", "sales", "sales"],
    })

    # Filter(column, condition_callable)
    result = Filter("score", lambda x: x > 80).apply(df)
    assert len(result) == 2

    # Project
    result = Project(["name", "score"]).apply(df)
    assert list(result.columns) == ["name", "score"]

    # Sort
    result = Sort("score", ascending=False).apply(df)
    assert result.iloc[0]["name"] == "Carol"

    # Limit
    result = Limit(2).apply(df)
    assert len(result) == 2

    # Chain
    chain = Chain([Filter("score", lambda x: x > 70), Sort("score"), Limit(2)])
    result = chain.apply(df)
    assert len(result) == 2
    print("✓ basic_operators OK")


def test_master_table():
    import pandas as pd
    from core.master_table import MasterTable

    df = pd.DataFrame({
        "entity": ["A", "B", "C"],
        "value": [10, 20, 30],
    })
    mt = MasterTable(df)
    assert len(mt.df) == 3
    csv_str = mt.to_csv()
    assert "entity" in csv_str
    print("✓ master_table OK")


if __name__ == "__main__":
    test_utils()
    test_llm_client()
    test_topic_agent()
    test_pipeline_runner()
    test_basic_operators()
    test_master_table()
    print("\n🎉 All 6 modules verified successfully!")
