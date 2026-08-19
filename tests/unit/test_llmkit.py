"""The model-calling layer, exercised against a fake provider with no network."""

import json
import subprocess
import sys

import pytest

from llmkit import LLM, Image, Message, Response, Usage
from llmkit.parse import ParseError, extract_json
from llmkit.providers import Provider


class FakeProvider(Provider):
    """Returns canned replies in order and records every request it received."""

    name = "fake"

    def __init__(self, replies: list[str | Exception]) -> None:
        self.replies = list(replies)
        self.calls: list[dict] = []

    def complete(self, *, model, system, messages, max_tokens, effort, schema, extra):
        self.calls.append({"model": model, "system": system, "messages": messages,
                           "max_tokens": max_tokens, "effort": effort, "schema": schema})
        reply = self.replies.pop(0)
        if isinstance(reply, Exception):
            raise reply
        return Response(text=reply, model=model, usage=Usage(10, 20), stop_reason="end_turn")

    def embed(self, texts, model):
        return [[float(len(t)), float(t.count("a"))] for t in texts]


@pytest.fixture
def llm_factory(tmp_path):
    def make(replies, **kw):
        provider = FakeProvider(replies)
        return LLM(model="claude-opus-5", provider=provider,
                   cache_dir=kw.pop("cache_dir", None), **kw), provider
    return make


class TestComplete:
    def test_returns_the_model_text(self, llm_factory):
        llm, _ = llm_factory(["hello"])
        assert llm.complete("be terse", "hi").text == "hello"

    def test_passes_system_and_user_through(self, llm_factory):
        llm, provider = llm_factory(["ok"])
        llm.complete("SYS", "USER")
        call = provider.calls[0]
        assert call["system"] == "SYS"
        assert call["messages"] == [Message("user", "USER")]

    def test_usage_is_reported(self, llm_factory):
        llm, _ = llm_factory(["ok"])
        r = llm.complete("s", "u")
        assert r.usage.input_tokens == 10 and r.usage.output_tokens == 20

    def test_a_refusal_raises_rather_than_returning_empty_text(self, llm_factory):
        llm, provider = llm_factory(["", ""])
        provider.replies = [""]

        def refuse(**kw):
            return Response(text="", model="m", usage=Usage(1, 0), stop_reason="refusal")

        provider.complete = lambda **kw: refuse(**kw)
        from llmkit.types import Refusal

        with pytest.raises(Refusal):
            llm.complete("s", "u")


class TestJsonMode:
    SCHEMA = {"type": "object", "properties": {"title": {"type": "string"}},
              "required": ["title"], "additionalProperties": False}

    def test_parses_a_clean_json_reply(self, llm_factory):
        llm, _ = llm_factory(['{"title": "ER waits"}'])
        assert llm.json("s", "u", schema=self.SCHEMA) == {"title": "ER waits"}

    def test_the_schema_is_handed_to_the_provider(self, llm_factory):
        llm, provider = llm_factory(['{"title": "x"}'])
        llm.json("s", "u", schema=self.SCHEMA)
        assert provider.calls[0]["schema"] == self.SCHEMA

    def test_a_fenced_reply_still_parses(self, llm_factory):
        llm, _ = llm_factory(['```json\n{"title": "x"}\n```'])
        assert llm.json("s", "u", schema=self.SCHEMA) == {"title": "x"}

    def test_a_broken_reply_is_retried_with_the_error_fed_back(self, llm_factory):
        llm, provider = llm_factory(["not json at all", '{"title": "x"}'], max_content_retries=2)
        assert llm.json("s", "u", schema=self.SCHEMA) == {"title": "x"}
        assert len(provider.calls) == 2
        assert "not json at all" in provider.calls[1]["messages"][1].content

    def test_giving_up_raises_with_the_last_text(self, llm_factory):
        llm, _ = llm_factory(["nope", "still nope"], max_content_retries=2)
        with pytest.raises(ParseError) as e:
            llm.json("s", "u", schema=self.SCHEMA)
        assert "still nope" in str(e.value)

    def test_a_missing_required_field_counts_as_a_parse_failure(self, llm_factory):
        llm, provider = llm_factory(['{"other": 1}', '{"title": "x"}'], max_content_retries=2)
        assert llm.json("s", "u", schema=self.SCHEMA)["title"] == "x"
        assert "title" in provider.calls[1]["messages"][1].content


class TestExtractJson:
    def test_bare_object(self):
        assert extract_json('{"a": 1}') == {"a": 1}

    def test_fenced_object(self):
        assert extract_json('text\n```json\n{"a": 1}\n```\nmore') == {"a": 1}

    def test_object_embedded_in_prose(self):
        assert extract_json('Here you go: {"a": [1, 2]} — done') == {"a": [1, 2]}

    def test_no_json_raises(self):
        with pytest.raises(ParseError):
            extract_json("no braces here")

    def test_truncated_json_raises(self):
        with pytest.raises(ParseError):
            extract_json('{"a": 1')


class TestCache:
    def test_the_same_request_is_only_sent_once(self, llm_factory, tmp_path):
        llm, provider = llm_factory(["first"], cache_dir=tmp_path)
        assert llm.complete("s", "u").text == "first"
        assert llm.complete("s", "u").text == "first"
        assert len(provider.calls) == 1

    def test_a_different_prompt_is_a_different_entry(self, llm_factory, tmp_path):
        llm, provider = llm_factory(["a", "b"], cache_dir=tmp_path)
        llm.complete("s", "u1")
        llm.complete("s", "u2")
        assert len(provider.calls) == 2

    def test_a_different_model_is_a_different_entry(self, tmp_path):
        provider = FakeProvider(["a", "b"])
        LLM(model="claude-opus-5", provider=provider, cache_dir=tmp_path).complete("s", "u")
        LLM(model="claude-haiku-4-5", provider=provider, cache_dir=tmp_path).complete("s", "u")
        assert len(provider.calls) == 2

    def test_no_cache_dir_means_no_caching(self, llm_factory):
        llm, provider = llm_factory(["a", "b"])
        llm.complete("s", "u")
        llm.complete("s", "u")
        assert len(provider.calls) == 2

    def test_the_cache_survives_a_new_client(self, tmp_path):
        first = FakeProvider(["cached"])
        LLM(model="m", provider=first, cache_dir=tmp_path).complete("s", "u")
        second = FakeProvider([])
        assert LLM(model="m", provider=second, cache_dir=tmp_path).complete("s", "u").text == "cached"
        assert not second.calls


class TestBatch:
    def test_map_keeps_input_order(self, llm_factory):
        llm, _ = llm_factory([f"r{i}" for i in range(5)])
        got = llm.map([("s", f"u{i}") for i in range(5)], workers=1)
        assert [r.text for r in got] == ["r0", "r1", "r2", "r3", "r4"]

    def test_a_failed_item_comes_back_as_none(self, llm_factory):
        llm, _ = llm_factory(["a", RuntimeError("boom"), "c"])
        got = llm.map([("s", "u1"), ("s", "u2"), ("s", "u3")], workers=1)
        assert [r.text if r else None for r in got] == ["a", None, "c"]

    def test_a_schema_makes_every_item_come_back_parsed(self, llm_factory):
        schema = {"type": "object", "properties": {"title": {"type": "string"}},
                  "required": ["title"], "additionalProperties": False}
        llm, provider = llm_factory(['{"title": "a"}', '{"title": "b"}'])
        assert llm.map([("s", "u1"), ("s", "u2")], workers=1, schema=schema) == \
            [{"title": "a"}, {"title": "b"}]
        assert provider.calls[0]["schema"] == schema

    def test_a_schema_batch_retries_one_bad_reply_without_failing_the_rest(self, llm_factory):
        schema = {"type": "object", "properties": {"title": {"type": "string"}},
                  "required": ["title"], "additionalProperties": False}
        llm, _ = llm_factory(["not json", '{"title": "a"}', '{"title": "b"}'],
                             max_content_retries=2)
        assert llm.map([("s", "u1"), ("s", "u2")], workers=1, schema=schema) == \
            [{"title": "a"}, {"title": "b"}]

    def test_images_ride_along_in_a_batch(self, llm_factory):
        llm, provider = llm_factory(["ok"])
        image = Image("image/png", "aGVsbG8=")
        llm.map([("s", "u", (image,))], workers=1)
        assert provider.calls[0]["messages"][0].images == (image,)


class TestImages:
    """An image rides on a message; the bytes reach the provider, the digest reaches
    the cache key."""

    PNG = Image("image/png", "aGVsbG8=")
    OTHER = Image("image/png", "d29ybGQ=")

    def test_a_message_carries_no_images_by_default(self):
        assert Message("user", "u").images == ()

    def test_an_unknown_media_type_is_refused(self):
        with pytest.raises(ValueError, match="image/tiff"):
            Image("image/tiff", "x")

    def test_from_path_reads_and_encodes(self, tmp_path):
        p = tmp_path / "page.png"
        p.write_bytes(b"hello")
        assert Image.from_path(p) == self.PNG

    def test_complete_puts_the_images_on_the_user_message(self, llm_factory):
        llm, provider = llm_factory(["ok"])
        llm.complete("s", "u", images=[self.PNG])
        assert provider.calls[0]["messages"] == [Message("user", "u", (self.PNG,))]

    def test_json_mode_accepts_images(self, llm_factory):
        llm, provider = llm_factory(['{"title": "x"}'])
        schema = {"type": "object", "properties": {"title": {"type": "string"}},
                  "required": ["title"], "additionalProperties": False}
        assert llm.json("s", "u", schema=schema, images=[self.PNG]) == {"title": "x"}
        assert provider.calls[0]["messages"][0].images == (self.PNG,)

    def test_a_retry_resends_the_images_once_not_twice(self, llm_factory):
        """The correction is a second message; repeating the pixels would bill twice."""
        llm, provider = llm_factory(["not json", '{"title": "x"}'], max_content_retries=2)
        schema = {"type": "object", "properties": {"title": {"type": "string"}},
                  "required": ["title"], "additionalProperties": False}
        llm.json("s", "u", schema=schema, images=[self.PNG])
        retry = provider.calls[1]["messages"]
        assert retry[0].images == (self.PNG,) and retry[1].images == ()

    def test_map_accepts_a_third_element_of_images(self, llm_factory):
        llm, provider = llm_factory(["a", "b"])
        got = llm.map([("s", "u1", [self.PNG]), ("s", "u2")], workers=1)
        assert [r.text for r in got] == ["a", "b"]
        assert provider.calls[0]["messages"][0].images == (self.PNG,)
        assert provider.calls[1]["messages"][0].images == ()

    def test_a_different_image_is_a_different_cache_entry(self, llm_factory, tmp_path):
        llm, provider = llm_factory(["a", "b"], cache_dir=tmp_path)
        llm.complete("s", "u", images=[self.PNG])
        llm.complete("s", "u", images=[self.OTHER])
        assert len(provider.calls) == 2

    def test_the_same_image_hits_the_cache(self, llm_factory, tmp_path):
        llm, provider = llm_factory(["a"], cache_dir=tmp_path)
        llm.complete("s", "u", images=[self.PNG])
        llm.complete("s", "u", images=[self.PNG])
        assert len(provider.calls) == 1

    def test_the_cache_key_holds_the_digest_and_not_the_bytes(self, llm_factory, tmp_path):
        llm, _ = llm_factory(["a"], cache_dir=tmp_path)
        llm.complete("s", "u", images=[self.PNG])
        written = next(tmp_path.glob("*.json")).read_text()
        assert self.PNG.digest in written and self.PNG.data not in written

    def test_the_request_body_puts_the_image_block_before_the_text(self):
        from llmkit.providers import AnthropicProvider

        body = AnthropicProvider.build_request(
            model="m", system="S", messages=[Message("user", "U", (self.PNG,))],
            max_tokens=8, effort=None, schema=None, extra={})
        blocks = body["messages"][0]["content"]
        assert [b["type"] for b in blocks] == ["image", "text"]
        assert blocks[0]["source"] == {"type": "base64", "media_type": "image/png",
                                       "data": "aGVsbG8="}

    def test_a_text_only_message_stays_a_plain_string(self):
        from llmkit.providers import AnthropicProvider

        body = AnthropicProvider.build_request(
            model="m", system="S", messages=[Message("user", "U")],
            max_tokens=8, effort=None, schema=None, extra={})
        assert body["messages"][0]["content"] == "U"


class TestLexicalJudge:
    """The similarity the deduper falls back to when no embedding is injected. It
    needs no service and no model, so the numbers below are what the configured
    thresholds are calibrated against."""

    def test_a_text_is_identical_to_itself(self):
        from llmkit.embed import cosine, lexical

        assert cosine(*lexical(["ICU bed turnover"] * 2)) == pytest.approx(1.0)

    def test_a_reworded_name_stays_close(self):
        from llmkit.embed import cosine, lexical

        assert cosine(*lexical(["ICU bed turnover analysis", "ICU bed turnover"])) > 0.65

    def test_an_unrelated_name_is_far(self):
        from llmkit.embed import cosine, lexical

        assert cosine(*lexical(["ICU bed turnover", "Retail promotion uplift"])) < 0.3

    def test_names_separate_far_more_widely_than_prose(self):
        """Why the scenario check compares titles: on a paragraph the margin is thin."""
        from llmkit.embed import cosine, lexical

        near = cosine(*lexical(["ICU bed turnover", "ICU bed turnover rate"]))
        far = cosine(*lexical(["ICU bed turnover", "Retail promotion uplift"]))
        assert near - far > 0.5

    def test_the_same_text_hashes_the_same_across_processes(self):
        code = ("import sys; sys.path.insert(0, 'src'); from llmkit.embed import lexical; "
                "print(sum(lexical(['ICU bed turnover'])[0]))")
        runs = {subprocess.run([sys.executable, "-c", code], capture_output=True,
                               text=True).stdout for _ in range(2)}
        assert len(runs) == 1


class TestDedupe:
    def test_the_default_judge_catches_a_repeat_with_nothing_injected(self):
        from llmkit.embed import Deduper

        d = Deduper(threshold=0.75)
        assert d.add("ICU bed turnover") and not d.add("ICU bed turnover")
        assert d.add("Quarterly freight cost by lane") and len(d) == 2

    def test_a_near_duplicate_is_caught(self):
        from llmkit.embed import Deduper

        d = Deduper(embed=lambda texts: [[1.0, 0.0] if "cat" in t else [0.0, 1.0] for t in texts],
                    threshold=0.85)
        d.add("a cat sat")
        assert d.is_duplicate("another cat")
        assert not d.is_duplicate("a dog ran")

    def test_add_returns_whether_it_was_new(self):
        from llmkit.embed import Deduper

        d = Deduper(embed=lambda texts: [[1.0, 0.0]] * len(texts), threshold=0.9)
        assert d.add("first")
        assert not d.add("second")
        assert len(d) == 1

    def test_it_persists_across_runs(self, tmp_path):
        from llmkit.embed import Deduper

        embed = lambda texts: [[1.0, 0.0]] * len(texts)
        d = Deduper(embed=embed, threshold=0.9, path=tmp_path / "seen.json")
        d.add("first")
        assert not Deduper(embed=embed, threshold=0.9, path=tmp_path / "seen.json").add("again")

    def test_an_empty_deduper_never_reports_a_duplicate(self):
        from llmkit.embed import Deduper

        assert not Deduper(embed=lambda t: [[1.0]] * len(t)).is_duplicate("anything")


class TestAnthropicProviderShape:
    """Check the request shape offline, without sending anything."""

    def test_request_carries_no_removed_sampling_params(self):
        from llmkit.providers import AnthropicProvider

        body = AnthropicProvider.build_request(
            model="claude-opus-5", system="S",
            messages=[Message("user", "U")], max_tokens=8000,
            effort="high", schema={"type": "object", "additionalProperties": False}, extra={})
        assert "temperature" not in body and "top_p" not in body and "top_k" not in body
        assert "budget_tokens" not in json.dumps(body)

    def test_effort_goes_inside_output_config(self):
        from llmkit.providers import AnthropicProvider

        body = AnthropicProvider.build_request(
            model="claude-opus-5", system="S", messages=[Message("user", "U")],
            max_tokens=8000, effort="high", schema=None, extra={})
        assert body["output_config"]["effort"] == "high"

    def test_a_schema_becomes_output_config_format(self):
        from llmkit.providers import AnthropicProvider

        schema = {"type": "object", "additionalProperties": False}
        body = AnthropicProvider.build_request(
            model="claude-opus-5", system="S", messages=[Message("user", "U")],
            max_tokens=8000, effort=None, schema=schema, extra={})
        assert body["output_config"]["format"] == {"type": "json_schema", "schema": schema}

    def test_fields_the_installed_sdk_does_not_type_go_through_extra_body(self):
        """Newer request parameters have no keyword on an older SDK, but `extra_body`
        is merged into the body untouched, so one split works against either."""
        from llmkit.providers import AnthropicProvider

        body = AnthropicProvider.build_request(
            model="claude-opus-5", system="S", messages=[Message("user", "U")],
            max_tokens=8000, effort="high", schema=None, extra={})
        kwargs, extra_body = AnthropicProvider.split_body(body)
        assert set(kwargs) == {"model", "max_tokens", "messages", "system"}
        assert extra_body == {"output_config": {"effort": "high"}}

    def test_an_object_that_does_not_close_itself_is_caught_before_the_request(self):
        """The service refuses such a schema, naming only the innermost field."""
        from llmkit.providers import AnthropicProvider
        from llmkit.types import LLMError

        schema = {"type": "object", "additionalProperties": False,
                  "properties": {"items": {"type": "array", "items": {"type": "object"}}}}
        with pytest.raises(LLMError, match=r"schema\.items\[\]"):
            AnthropicProvider.build_request(
                model="m", system="S", messages=[Message("user", "U")],
                max_tokens=8, effort=None, schema=schema, extra={})

    def test_a_body_with_only_known_fields_needs_no_extra_body(self):
        from llmkit.providers import AnthropicProvider

        kwargs, extra_body = AnthropicProvider.split_body(
            {"model": "m", "max_tokens": 8, "messages": []})
        assert extra_body is None and kwargs["model"] == "m"

    def test_the_default_model_is_the_current_opus(self):
        import llmkit

        assert llmkit.DEFAULT_MODEL == "claude-opus-5"
