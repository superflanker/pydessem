from pydessem.io_loader import load_case

def test_yaml_load():
    data = load_case("examples/case_tiny.yaml")
    assert "params" in data and "sets" in data
