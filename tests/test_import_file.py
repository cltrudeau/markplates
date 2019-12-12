import markplates

def process(tmp_path, lines):
    """ Utility to create a fake file and process a template. """
    file_name = "fake_source.py"
    source_file = tmp_path / file_name
    source_file.write_text("\n".join(lines))

    template = tmp_path / "t_import.mdt"
    template.write_text(
        '{{ set_path("%s") }}{{ import_source("%s", ["1-$"]) }}'
        % (tmp_path, file_name)
    )
    return markplates.process_template(template)

def test_import_full(tmp_path, counting_lines):
    lines = counting_lines(3)
    # expect all lines except the first
    expected_result = "".join(lines[1:]).rstrip()

    file_name = "fake_source.py"
    source_file = tmp_path / file_name
    source_file.write_text("".join(lines))
    template = tmp_path / "t_import.mdt"
    template.write_text(
        '{{ set_path("%s") }}{{ import_source("%s") }}' % (tmp_path, file_name)
    )
    fred = markplates.process_template(template)
    assert fred == expected_result


def test_import_partial(tmp_path, counting_lines):
    lines = counting_lines(5)
    # expect all lines except the first two
    expected_result = "".join(lines[2:]).rstrip()

    file_name = "fake_source.py"
    source_file = tmp_path / file_name
    source_file.write_text("".join(lines))
    template = tmp_path / "t_import.mdt"
    template.write_text(
        '{{ set_path("%s") }}{{ import_source("%s", ["3-5"]) }}'
        % (tmp_path, file_name)
    )
    fred = markplates.process_template(template)
    assert fred == expected_result


def test_reduce_double_lines_after_import(tmp_path):
    # for RP articles, we want to remove the double blank lines after import
    # or between functions.  Ensure that these are removed.
    lines = [
        "import markplates",
        "",
        "",
        "def test_import_full(tmp_path, counting_lines):",
        "    lines = counting_lines(3)",
        "    # expect all lines except the first with \n after all except the",
        "    expected_result = "".join(lines[1:]).rstrip()",
        "",
        "    file_name = 'fake_source.py'",
    ]
    expected_result = lines.copy()
    del expected_result[2]
    expected_result = "\n".join(expected_result)
    fred = process(tmp_path, lines)
    assert fred == expected_result

    # leading blank line failed initial implementation
    lines = [ "", "", "", ]
    expected_result = ""
    fred = process(tmp_path, lines)
    assert fred == expected_result

    # test more than two blanks
    lines = [
        "import markplates",
        "",
        "",
        "",
        "",
        "",
        "",
        "import markplates",
    ]
    expected_result = [
        "import markplates",
        "",
        "import markplates",
    ]
    expected_result = "\n".join(expected_result)
    fred = process(tmp_path, lines)
    assert fred == expected_result

def test_left_justify(tmp_path):
    # for RP articles, we want to have all code blocks left justified even if
    # they are pulled from inside a class def.
    lines = [ "0", " 1", "  2", "   3", ]
    expected_result = lines.copy()
    expected_result = "\n".join(expected_result)
    fred = process(tmp_path, lines)
    assert fred == expected_result

    # remove a leading space
    lines = [ " 1", "  2", "   3", ]
    expected_result = [ "1", " 2", "  3", ]
    expected_result = "\n".join(expected_result)
    fred = process(tmp_path, lines)
    assert fred == expected_result

    # remove several leading spaces
    lines = [ "      1", "    2", "        3", ]
    expected_result  = [ "  1", "2", "    3", ]
    expected_result = "\n".join(expected_result)
    fred = process(tmp_path, lines)
    assert fred == expected_result

    # left most line does  not need to be first
    lines = [ "  2", " middle", "   3", ]
    expected_result  = [ " 2", "middle", "  3", ]
    expected_result = "\n".join(expected_result)
    fred = process(tmp_path, lines)
    assert fred == expected_result

    # blank line doesn't count
    lines = [ " 1", "  2", "", "   3", ]
    expected_result = [ "1", " 2", "", "  3", ]
    expected_result = "\n".join(expected_result)
    fred = process(tmp_path, lines)
    assert fred == expected_result
