"""Black-box checks against independently constructed teaching-format records."""
import pathlib
import struct
import subprocess
import sys
import tempfile

binary = str(pathlib.Path(sys.argv[1]).resolve())
def run(*args):
    return subprocess.run([binary, *map(str, args)], capture_output=True, text=True, timeout=15)
def frame(event=1, payload=b'\x34\x12', seq=1, version=1, level=2):
    return struct.pack('<2sBBHHII', b'LG', version, level, len(payload), event, seq, 1000) + payload
with tempfile.TemporaryDirectory() as directory:
    root = pathlib.Path(directory)
    def check(name, data, success, text=''):
        path = root / (name + '.bin')
        path.write_bytes(data)
        result = run('decode', path)
        assert (result.returncode == 0) == success, (name, result)
        assert text in result.stdout + result.stderr, (name, result)
    assert run('self-test').returncode == 0
    assert 'dropped=2' in run('ring').stdout
    sample = root / 'sample.bin'
    assert run('generate', sample).returncode == 0
    assert sample.read_bytes() == frame() + struct.pack('<2sBBHHII', b'LG', 1, 2, 1, 2, 2, 1010) + b'\x01'
    check('good', frame(), True, 'value=4660')
    check('coalesced', frame() + frame(seq=2), True, 'seq=2')
    check('empty', b'', True)
    check('unknown', frame(event=99, payload=b'\x00\xff'), True, 'UNKNOWN payload=00ff')
    check('maximum', frame(event=99, payload=bytes(range(32))), True, 'len=32')
    check('zero', frame(event=99, payload=b''), True, 'len=0')
    for end in range(1, len(frame())):
        check('truncated-' + str(end), frame()[:end], False, 'truncated')
    check('version', frame(version=2), False, 'invalid')
    check('level', frame(level=4), False, 'invalid')
    check('magic', b'XX' + frame()[2:], False, 'invalid')
    check('length', frame(event=99, payload=bytes(33)), False, 'invalid')
    check('schema', frame(event=1, payload=b'\x01'), False, 'invalid')
    check('state', frame(event=2, payload=b'\x02'), False, 'invalid')
    check('tail', frame() + b'L', False, 'truncated')
    check('wrap', frame(seq=0xffffffff) + frame(seq=0), True, 'seq=0')
    check('long-stream', frame() * 1000, True)
print('integration: PASS (fixtures, boundaries, malformed data, stream, sequence wrap)')
