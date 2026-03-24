from argparse import ArgumentParser
from hashlib import file_digest
from pathlib import Path

ALGORITHMS = ['sha3_224', 'sha3_512', 'sha3_384', 'sha1', 'sha512', 'sha384',
              'blake2b', 'sha3_256', 'sha256', 'md5', 'sha224', 'blake2s']


def generate(files: list[Path], output: Path, algorithms:list[str]) -> None:
    """
    Generate hashes for list of files.

    :param files: List of Path objects
    :param output: Path to output file
    :param algorithms: List of hash algorithms to use
    """
    with open(output, 'w+') as f_digests:
        for algo in algorithms:
            f_digests.write(f'#HASH {algo}\n')
            for file2hash in files:
                with open(file2hash, 'rb') as hash_f:
                    computed_hash = file_digest(hash_f, algo).hexdigest()
                    print(f'computed: {algo} for {file2hash.name}')
                f_digests.write(f'{computed_hash} {file2hash.name}\n')


if __name__ == '__main__':
    parser = ArgumentParser(description='Generate hashes for files.')
    parser.add_argument('files', nargs='+', type=Path, help='List of files to hash')
    parser.add_argument('-o', '--output', type=Path, default=Path('./DIGESTS'), help='Output file for digests')
    parser.add_argument('-a', '--algorithms', nargs='+', default=ALGORITHMS, choices=ALGORITHMS,
                        help='List of hash algorithms to use')
    args = parser.parse_args()
    generate(args.files, args.output, args.algorithms)
