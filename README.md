# Pyparlaclarin

This module includes functionality for reading, creating, and modifying Parla-Clarin XML files.

For instance, you can loop over all paragraphs in a Parla-Clarin file with a simple function:

```python
from pyparlaclarin.read import paragraph_iterator

for paragraph in paragraph_iterator(root):
	print(paragraph)
```

or get all speeches by a speaker

```python
from pyparlaclarin.read import speeches_with_name

for speech in speeches_with_name(root, name="barack_obama_1961"):
	print(speech)
```

Further documentation is available on [GitHub pages](https://welfare-state-analytics.github.io/pyparlaclarin/pyparlaclarin/).