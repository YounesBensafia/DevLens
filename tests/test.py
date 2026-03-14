from devlens.llm.client import build_payload


def test_build_payload_has_expected_shape():
	payload = build_payload("system message", "user prompt")

	assert payload["model"]
	assert payload["temperature"] >= 0
	assert payload["max_tokens"] > 0
	assert payload["messages"][0]["role"] == "system"
	assert payload["messages"][1]["role"] == "user"