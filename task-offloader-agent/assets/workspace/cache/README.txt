How to download a tokenizer.json for the model you are using
=============================================================

The `inference.tokenizer` profile key points to a HuggingFace tokenizer file.
Providing it gives exact token counts so the budget is enforced precisely instead
of estimated at 3 chars/token (which is conservative but not exact).

Step-by-step
------------

1. Find the HuggingFace model card that matches the base model you put in
   `inference.model` (e.g. `qwen2.5-coder:7b` → `Qwen/Qwen2.5-Coder-7B`).

2. Download `tokenizer.json` from the model's Files tab:
   https://huggingface.co/<org>/<model>/blob/main/tokenizer.json

   Or use the huggingface-hub CLI:
     pip install huggingface-hub
     huggingface-cli download Qwen/Qwen2.5-Coder-7B tokenizer.json \
       --local-dir .task-offloader/cache/

3. Set the path in profile.toml (relative to the profile file):
     tokenizer = "cache/tokenizer.json"

4. Add the tokenizer to your workspace .gitignore if it is large (≈ 7 MB):
     .task-offloader/cache/

Common base model → HuggingFace repo map
-----------------------------------------
| Ollama model tag      | HuggingFace repo                         |
|-----------------------|------------------------------------------|
| qwen2.5-coder:7b      | Qwen/Qwen2.5-Coder-7B                    |
| qwen2.5-coder:14b     | Qwen/Qwen2.5-Coder-14B                   |
| codellama:7b          | meta-llama/CodeLlama-7b-hf               |
| deepseek-coder:6.7b   | deepseek-ai/deepseek-coder-6.7b-base     |
| starcoder2:7b         | bigcode/starcoder2-7b                    |

