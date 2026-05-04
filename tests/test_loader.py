def test_load_cert_dataset(tmp_path):
    file1 = tmp_path / "logon.csv"
    file2 = tmp_path / "file.csv"

    file1.write_text("a\n1\n2")
    file2.write_text("b\n3\n4")

    paths = {
        "logon": file1,
        "file": file2
    }

    data = load_cert_dataset(paths)

    assert "logon" in data
    assert "file" in data
    assert len(data["logon"]) == 2