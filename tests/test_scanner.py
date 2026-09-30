from pathlib import Path
import src.scanner as scanner
from src.scanner import get_unique_path, get_file_hash, categories

def test_unique_path_when_file_dose_not_exist(tmp_path):

    file = Path("report.pdf")

    result = get_unique_path(tmp_path, file)

    assert result == tmp_path / "report.pdf"


def test_unique_path_when_file_exist(tmp_path):

    file = Path("report.pdf")

    existing_file = tmp_path / "report.pdf"
    existing_file.touch()

    result = get_unique_path(tmp_path, file)

    assert result == tmp_path / "report_1.pdf"



def test_unique_path_with_multiple_existng_files(tmp_path):
    file = Path("report.pdf")

    (tmp_path / "report.pdf").touch()
    (tmp_path / "report_1.pdf").touch()

    result = get_unique_path(tmp_path, file)

    assert result == tmp_path /"report_2.pdf"


def test_file_hash(tmp_path):
    file = tmp_path / "tesr.txt"
    file.write_text("Hello Python")

    result = get_file_hash(file)

    assert len(result) == 64



def test_same_content_same_hash(tmp_path):

    file1 = tmp_path / "file1.txt"
    file2 = tmp_path / "file2.txt"

    file1.write_text("Python is easy")
    file2.write_text("Python is easy")

    hash1 = get_file_hash(file1)
    hash2 = get_file_hash(file2)

    assert hash1 == hash2


def different_same_different_same_hash(tmp_path):

    file1 = tmp_path / "file1.txt"
    file2 = tmp_path / "file2.txt"

    file1.write_text("Python is easy")
    file2.write_text("Python is powerful")

    hash1 = get_file_hash(file1)
    hash2 = get_file_hash(file2)

    assert hash1 == hash2


def test_different_content_different_hash(tmp_path):

    file1 = tmp_path / "file1.txt"
    file2 = tmp_path / "file2.txt"

    file1.write_text("Python is easy")
    file2.write_text("Python is powerful")

    hash1 = get_file_hash(file1)
    hash2 = get_file_hash(file2) 

    assert hash1 != hash2  



def test_same_file_same_hash(tmp_path):

    file = tmp_path / "test.txt"
    file.write_text("Smart File Manager")

    hash1 = get_file_hash(file)
    hash2 = get_file_hash(file)

    assert hash1 == hash2
    assert len(hash1) == 64


def test_pdf_category():

    file = Path("report.pdf")

    category = categories.get(file.suffix, "Other")
    assert category == "Documents"



def test_mp3_category():
    file = Path("song.mp3")

    category = categories.get(file.suffix, "Other")

    assert category == "Music"

def test_unknown_extension_category():
    file = Path("photo.xyz")
    category = categories.get(file.suffix, "Other")
    assert category == "Other"

def test_unique_path_preserves_extension(tmp_path):

    file = Path("photo.jpg")
    (tmp_path / "photo.jpg").touch()
    result = get_unique_path(tmp_path, file)
    assert result == tmp_path / "photo_1.jpg"


def test_file_hash_known_file(tmp_path):

    file = tmp_path / "test.txt"
    file.write_text("hello")

    result = get_file_hash(file)

    assert result == "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"


def test_scan_files_dry_run(tmp_path, monkeypatch, capsys):

    test_file = tmp_path / "report.pdf"
    test_file.write_text("Test PDF")

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(scanner, "dry_run", True)

    scanner.scan_files()

    output = capsys.readouterr().out

    assert "report.pdf -> Documents" in output
    assert test_file.exists()


def test_dry_run_does_not_move_file(tmp_path, monkeypatch):

    test_file = tmp_path / "report.pdf"
    test_file.write_text("Test PDF")

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(scanner, "dry_run", True)

    scanner.scan_files()

    assert test_file.exists()

    assert not (tmp_path / "Docements" / "report.pdf").exists()



def test_scan_files_moves_pdf_to_documents(tmp_path, monkeypatch):

    test_file = tmp_path / "report.pdf"
    test_file.write_text("Test PDF")

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(scanner, "dry_run", False)

    scanner.scan_files()

    moved_file = tmp_path / "Documents" / "report.pdf"

    assert moved_file.exists()
    assert not test_file.exists()


def test_scan_files_handles_collision(tmp_path, monkeypatch):

    test_file = tmp_path / "report.pdf"
    test_file.write_text("New PDF")

    documents = tmp_path / "Documents"
    documents.mkdir()

    existing_file = documents / "report.pdf"
    existing_file.write_text("Old PDF")

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(scanner, "dry_run", False)

    scanner.scan_files()

    moved_file = documents / "report_1.pdf"

    assert existing_file.exists()
    assert moved_file.exists()
    assert not test_file.exists()



def test_scan_files_handles_multiple_collisions(tmp_path, monkeypatch):

    test_file = tmp_path / "report.pdf"
    test_file.write_text("New PDF")

    documents = tmp_path / "Documents"
    documents.mkdir()

    (documents / "report.pdf").write_text("Old PDF")
    (documents / "report_1.pdf").write_text("Another PDF")

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(scanner, "dry_run", False)

    scanner.scan_files()

    moved_file = documents / "report_2.pdf"

    assert moved_file.exists()
    assert (documents / "report.pdf").exists()
    assert (documents / "report_1.pdf").exists()
    assert not test_file.exists()


def test_duplicate_detection(tmp_path, monkeypatch, capsys):

    documents = tmp_path / "Documents"
    documents.mkdir()

    file1 = documents / "report.pdf"
    file2 = documents / "report_copy.pdf"

    file1.write_text("Same PDF content")
    file2.write_text("Same PDF content")

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(scanner, 'dry_run', True)

    scanner.scan_files()

    output = capsys.readouterr().out

    assert "Duplicate: report_copy.pdf" in output
    assert "Same as: report.pdf" in output


def test_different_files_are_not_duplicates(tmp_path, monkeypatch, capsys):

    documents = tmp_path / "Documents"
    documents.mkdir()

    file1 = documents / "report.pdf"
    file2 = documents / "report_copy.pdf"

    file1.write_text("First PDF content")
    file2.write_text("Different PDF content")

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(scanner, 'dry_run', True)    

    scanner.scan_files()

    output = capsys.readouterr().out
    assert "Duplicate:" not in output



def test_move_is_saved_in_history(tmp_path, monkeypatch):

    test_file = tmp_path / "report.pdf"
    test_file.write_text("Test PDF")

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(scanner, "dry_run", False)

    scanner.scan_files()

    cursor = scanner.cursor

    cursor.execute("""
       SELECT original_path, new_path
       FROM move_history
       ORDER BY id DESC
       LIMIT 1
""")

    history = cursor.fetchone()

    assert history is not None
    assert history[0] == "report.pdf"
    assert history[1] == str(Path("Documents") / "report.pdf")



def test_undo_moves_file_back(tmp_path, monkeypatch):

    original_file = tmp_path / "report.pdf"
    original_file.write_text("Test PDF")

    documents = tmp_path / "Documents"
    documents.mkdir()

    moved_file = documents / "report.pdf"
    moved_file.write_text("Test PDF")

    monkeypatch.chdir(tmp_path)

    scanner.cursor.execute("DELETE FROM move_history")
    scanner.cursor.execute("""
        INSERT INTO move_history (original_path, new_path, move_time)
        VALUES (?, ?, datetime('now'))
    """, ("report.pdf", str(Path("Documents") / "report.pdf")))
    scanner.connection.commit()

    # Original file ko temporarily hatao,
    # taake undo usay wapas la sake.
    original_file.unlink()

    scanner.undo_last_move()

    assert original_file.exists()
    assert not moved_file.exists()


def test_undo_removes_history_record(tmp_path, monkeypatch):

    test_file = tmp_path / "report.pdf"
    test_file.write_text("Test PDF")

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(scanner, "dry_run", False)

    scanner.scan_files()

    scanner.undo_last_move()

    cursor = scanner.cursor

    cursor.execute("""
        SELECT original_path, new_path
        FROM move_history
        ORDER BY id DESC
        LIMIT 1
    """)

    history = cursor.fetchone()

    assert history is None
    assert test_file.exists()
    assert not (tmp_path / "Documents" / "report.pdf").exists()
    