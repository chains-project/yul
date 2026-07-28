# model-validator

Validates JSON data records against a Pydantic model.

## Usage

```bash
uv sync
echo '{"name": "Ada", "email": "ada@example.com", "age": 30}' | uv run model-validator
```

## Testing

```bash
uv run pytest
```
