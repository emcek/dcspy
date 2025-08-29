import hashlib
from pathlib import Path

ALGORITHMS = ['sha3_224', 'sha3_512', 'sha3_384', 'sha1', 'sha512', 'sha384',
              'blake2b', 'sha3_256', 'sha256', 'md5', 'sha224', 'blake2s']


def generate(files: list[Path]) -> None:
    with open('./../DIGESTS', 'w+') as f_digests:
        for algo in ALGORITHMS:
            f_digests.write(f'#HASH {algo}\n')
            for file2hash in files:
                with open(file2hash, 'rb') as hash_f:
                    computed_hash = hashlib.file_digest(hash_f, algo).hexdigest()
                f_digests.write(f'{computed_hash} {file2hash.name}\n')


if __name__ == '__main__':
    generate([Path(r'C:\Users\mplichta\Projects\dcspy\tests\resources\dcs_bios_data.json')])
