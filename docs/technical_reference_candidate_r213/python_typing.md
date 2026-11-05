# Python annotations and typing.cast
Sources:
https://docs.python.org/3.14/library/typing.html
https://docs.python.org/3.14/library/annotations.html

Python does not enforce annotations at runtime. typing.cast returns its input unchanged and performs no runtime type check or conversion. Static type checkers can report incompatible calls, but runtime validation requires explicit code or a runtime validation library.

