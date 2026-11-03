# Community Resource Catalogue (CoReCa)

The rapid growth of research infrastructure has led to the development of numerous bioinformatics tools and databases, but information about them remains fragmented across disparate, often outdated cataloging efforts, hindering resource discovery and utilization.

To address this critical gap, the [ELIXIR Microbiome Community](https://elixir-europe.org/communities/microbiome) collaborates with the [Research Software Ecosystem](https://research-software-ecosystem.github.io/) to create MiCoReCa (Microbiome Community Resource Catalogue), a comprehensive, dynamic, open-access catalogue of microbiome-related bioinformatics resources. This resource is now usable by other communities, and are grouped under the CoReCa (Community Resource Catalogue).

CoReCa contain:
- Tools from [Research Software Ecosystem Atlas](https://research-software-ecosystem.github.io/RSEc-Atlas/)
- Workflows from [WorkflowHub](https://workflowhub.eu/)
- Training
- Standards
- Databases

The extraction, filtering and curation are done using the defined keywords in the [`keywords.yml` file](keywords.yml)

## Microbiome Community Resource Catalogue (MiCoReCa)

The inital work was done by the [ELIXIR Microbiome Community](https://elixir-europe.org/communities/microbiome) as they identified early on the issue and offered a solution.

The extraction, filtering and curation are done following the workflow below and using the defined keywords in the [`keywords.yml` file](keywords.yml):

![A workflow diagram illustrating the process for populating the RSEC Atlas, starting with 'Scrapping' resources from Bioconda, WorkflowHub, and Elixir, which yields over 40,000 tools and 1,300 workflows. This pool is reduced by the 'Filtering for Microbiome Resources' step to about 5,000 tools and 600 workflows. After 'Community Curation,' the items are 'Displayed on RSEC Atlas.' A detailed flowchart on the right explains the filtering logic: it sequentially checks if EDAM topics are found, if defined keywords are in the tags, if keywords are in the title, and finally if keywords are in the description. A 'Yes' at any step classifies the item as a 'MiCoCo resource,' while a 'No' at all steps classifies it as 'Not a MiCoCo resource.'](doc/main_figure_poster.png)

# Create a CoReCa for your community
## Prepare files

- Create the metadata folder for your community
    ```
    #Change by indicating the name of your community
    community="biodiversity"
    mkdir communities/${community}
    mkdir communities/${community}/metadata
    ```

- Create the keywords file for you community in the newly created metadata folder

    ```
    vi communities/${community}/metadata/keywords.yml
    ```

Example of a keywords file (from the microbiome community) : 

    ```
    edam:
        topics:
            - Metagenomics
            - Metatranscriptomics
            - Metabarcoding
        operations:
            - Read binning

    keywords:
        - metage.*
        - metabar.*
        - metat.*
        - metap.*
        - plasmid.*
        - binn.*
        - microbiom.*
        - microbiot.*
        - 16S
        - Amplicon
        - profil.*
        - amr
        - antimicrobial.*
        - MAGs

    acronyms:
        - ITS
        - OTU
        - ASV
    ```

## Prepare environment

- Install virtualenv (if not already there)

    ```
    $ python3 -m pip install --user virtualenv
    ```

- Create virtual environment

    ```
    $ python3 -m venv env
    ```

- Activate virtual environment

    ```
    $ source env/bin/activate
    ```

- Install requirements

    ```
    $ python3 -m pip install -r requirements.txt
    ```

## Workflows from WorkflowHub

- Extract all workflows metadata from WorkflowHub as a JSON file

    ```
    $ python bin/extract_workflowhub.py \
        extract \
        --all communities/all/workflowhub/workflows_full.json
    ```

- Filter community workflows based on keywords and EDAM terms
    This step filters workflows on EDAM terms (topics and operations), then on tags, workflow name and finally description based on the keywords provided in `keywords.yml` file.

    ```
    $ python bin/extract_workflowhub.py \
        filter \
        --all communities/all/workflowhub/workflows_full.json \
        --filtered communities/${community}/workflowhub/workflows_filtered.json \
        --tsv-filtered communities/${community}/workflowhub/workflows_filtered.tsv \
        --tags communities/${community}/metadata/keywords.yml \
        --status communities/${community}/workflowhub/workflows_status.tsv
    ```

- Curate workflows based on community curation
    This step curates the filtered workflows, to keep only workflows with a 'TRUE' label in the 'To keep' column of the communities/${community}/workflowhub/workflows_status.tsv file. 

    Update the 'To keep' column of the communities/${community}/workflowhub/workflows_status.tsv file

    ```
    $ python bin/extract_workflowhub.py \
        curate \
        --filtered communities/${community}/workflowhub/workflows_filtered.json \
        --curated communities/${community}/workflowhub/workflows_curated.json \
        --tsv-curated communities/${community}/workflowhub/workflows_curated.tsv \
        --status communities/${community}/workflowhub/workflows_status.tsv
    ```

- Extract tools used in curated workflows as JSON

    ```
    $ python bin/extract_workflowhub.py \
        extract_tools \
        --workflows communities/${community}/workflowhub/workflows_curated.json \
        --tools communities/${community}/workflowhub/tools_from_workflows.json
    ```

## Tools from RSEc

- Extract all metadata from RSEc

    ```
    $ python bin/extract_rsec.py \
        extract \
        --all communities/all/rsec/
    ```

- Filter RSEc tools based on keywords and EDAM terms
    This step filters RSEc tools based on the keywords provided in `keywords.yml` file.

    ```
    $ python bin/extract_rsec.py \
        filter \
        --all communities/all/rsec/ \
        --json communities/${community}/rsec/validated_tools_metadata.json \
        --tsv communities/${community}/rsec/validated_tools_summary.tsv \
        --keywords communities/${community}/metadata/keywords.yml
    ```

## Bioconda

- Extract all bioconda metadata as a JSON file

    ```
    mkdir -p ./tmp

    # download ZIP file *into tmp/*
    wget -O ./tmp/bioconda-recipes.zip https://codeload.github.com/bioconda/bioconda-recipes/zip/master

    # unzip from tmp into tmp/
    unzip ./tmp/bioconda-recipes.zip -d ./tmp/

    # remove the ZIP after extraction
    rm ./tmp/bioconda-recipes.zip

    python bin/bioconda_manager.py \
        extract \
        --bioconda-path ./tmp/bioconda-recipes-master/recipes \
        --all communities/all/bioconda/bioconda_full.json

    rm -r ./tmp
    ```

- Filter bioconda recipies based on keywords and EDAM terms
    This step filters bioconda recepies based on the keywords provided in `keywords.yml` file.

    ```
    $ python bin/bioconda_manager.py \
        filter \
        --all communities/all/bioconda/bioconda_full.json \
        --json-filtered communities/${community}/bioconda/bioconda_filtered.json \
        --tsv-filtered communities/${community}/bioconda/bioconda_filtered.tsv \
        --keywords communities/${community}/metadata/keywords.yml \
        --status communities/${community}/bioconda/bioconda_status.tsv
    ```

- Curate bioconda recipies based on community curation
    This step curates the filtered bioconda recepies, to keep only bioconda recipies with a 'TRUE' label in the 'To keep' column of the communities/${community}/bioconda/bioconda_status.tsv file. 

    Update the 'To keep' column of the communities/${community}/bioconda/bioconda_status.tsv file

    ```
    $ python bin/bioconda_manager.py \
        curate \
        --filtered communities/${community}/bioconda/bioconda_filtered.json \
        --json-curated communities/${community}/bioconda/bioconda_curated.json \
        --tsv-curated communities/${community}/bioconda/bioconda_curated.tsv \
        --status communities/${community}/bioconda/bioconda_status.tsv
    ```

## Run the unit tests locally

```
PYTHONPATH=bin python -m unittest discover -s bin/tests
```

# Contributing

To contribute to the CoReCa Source code:
1. Fork the repository,
2. Create a branch and add your changes
3. Add a unit test for your changes (see [unittests](sources/bin/tests) for examples).  
    **Warning:** new functions now require a unit test to be merged!
4. Make a pull request.

The `unittest` framework will run on your PR. Please fix the tests if required.

Upon review the maintainer will merge your pull request. 
Automatic tests will run on the dev branch. 
