# DataLad dtool extension

[![crippled-filesystems](https://github.com/livMatS/datalad-dtool/workflows/crippled-filesystems/badge.svg)](https://github.com/livMatS/datalad-dtool/actions?query=workflow%3Acrippled-filesystems) [![docs](https://github.com/livMatS/datalad-dtool/workflows/docs/badge.svg)](https://github.com/datalad/datalad-extension-template/actions?query=workflow%3Adocs)

This repository has been created during the [distribits 2024 hackathon](https://github.com/distribits/distribits-2024-hackathon).

The challange has been posed as https://github.com/distribits/distribits-2024-hackathon/tree/14013438ad833878de26dcbd02d2dc29a9b4a40e/datalad-dtool-interoperability and discussed at https://github.com/distribits/distribits-2024-hackathon/issues/10.

It suggests a simple extension to DataLad that creates a dtool dataset from a 
DataLad dataset.

Since

* dtool datasets have UUIDs, and DataLad datsets as well, and
* dtool datasets are immutable, while DataLad datasets are versioned.

we can export a dtool dataset as a "snapshot" of a versioned datalad dataset, 
with the unique mapping

    dtool dataset UUID <-> (datalad dataset UUID, commit)

This is done with the

    datalad export-dtool

command. For detailed usage information, see `datalad export-dtool --help`

## Example usage of datalad export-dtool

Create a minimal datalad dataset with a testfile

    datalad create testdir
    cd testdir
    echo "test" > testfile.txt

and add the data to git-annex

    datalad save

Then proceed to extract datalad to dtool with

    cd ..
    datalad export-dtool -n dtool-test -d testdir

## Example usage of Datalad export to dtool

Create a dtool dataset

    dtool create another-test

and populate it with data, e.g.

    cd another-test/data
    echo "another-test" > test_file.txt

Then, we freeze the dataset

    cd ..
    dtool freeze another-test

and get the path. Create a datalad dataset if not already done

    datalad create my-datalad-dataset

Then import the dtool-dataset to datalad with

    datalad import-dtool --dataset my-datalad-dataset --path dtool-import another-test

Check that dtool-dataset is still viable

    dtool ls my-datalad-dataset/another-test

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) if you are interested in internals or
contributing to the project.
