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

# Example usage of datalad export-dtool

If not in an existing datalad folder, create one with a testfile

    datalad create testdir && cd testdir && echo "test" > testfile.txt

add the data to git-annex

    datalad save

then proceed to extract datalad to dtool with

    cd .. && datalad export-dtool -n dtool-test -d testdir

# Example usage of Datalad export to dtool

You can check out our testrun at

    https://github.com/livMatS/datalad-dtool/blob/dd8813c58576bdc47a7f20ac95a648746fdf4a71/examples/test_readonly_git-annex-remote-dtool

to mimik a run you can create a dtool directory

    dtool create another-test

populate with data e.g.

    cd another-test/data && echo "another-test" > test_file.txt

then we need to freeze the dataset and get the MD5Hash

    dtool freeze another-test

After these steps we can create the directory for the Datalad to populate from dtool. At the current time, we manually create a git and git annex repository to mimik a Datalad dataset and populate it using an git-annex-specialRemote

    


# Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) if you are interested in internals or
contributing to the project.
