1.
pytest --tb=short pandas/tests/indexes/multi/test_indexing.py::test_getitem_bool_index_all
pytest --tb=short pandas/tests/indexes/multi/test_indexing.py::test_getitem_bool_index_single

2.
pytest --tb=short pandas/tests/test_base.py::TestIndexOps::test_get_item
pytest --tb=short pandas/tests/test_base.py::TestIndexOps::test_bool_indexing