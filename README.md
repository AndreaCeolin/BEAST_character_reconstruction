# Ancestral State Reconstruction using BEAST

This tutorial summarises the steps needed to perform ancestral state reconstruction using BEAST v.1 ([BEAST X](https://beast.community)). Note that BEAST v.2 ([BEAST 2](http://www.beast2.org)) does not support state reconstruction.

## 1. Using BEAUti to Load a .nex File

The BEAST software package comes with a tool, BEAUti, which generates the .xml file needed for the BEAST analysis. The latest version is BEAST X 10.5.

After installing the software, you should be able to open the UI of both BEAST and BEAUti. Since the software relies on Java, you might be prompted to install Java if your OS doesn’t have it.

I tried to use BEAUti 10.5 ([Installation Guide](http://beast.community/installing)) on my MacBook Air (M1, 2020) and clicked on ‘Import Data…’ to import the nexus file attached to this repository, but I encountered the following error:

> "Illegal Argument Exception - Parameter with name, frequencies, is unknown"

This is unexpected, as I have been using this nexus file for years across platforms with no issue.

I downloaded the previous version ([BEAUti v.1.10.4](https://github.com/beast-dev/beast-mcmc/releases/tag/v1.10.4)), and it worked. By clicking on ‘+’ on the BEAUti UI and selecting `table.nex`, the file was successfully loaded.

## 2. Add Settings for Character State Reconstruction

### Partitions
This section summarises the content of the file (it should have **69 Taxa and 94 sites**). Nothing to do here.

### Taxa
Relevant only if you want to reconstruct specific internal nodes instead of just the root of the tree. To do this:

- Click on `+` to add a taxon set.
- Rename the taxon set from `untitled0` to something meaningful (e.g., `Proto-IE`).
- Tick the `Mono` box to ensure a constraint is forced (i.e., all IE languages are placed under the same node). Otherwise, the results might be harder to interpret (e.g., the IE node might include non-IE languages, influencing reconstruction).
- Drag languages from the left panel (**Excluded Taxa**) to the right panel (**Included Taxa**) using the green arrow.

### Tips & Traits
Skip these sections.

### Sites
Use the default settings. You may experiment with:
- **Base frequencies**: Change to `Empirical` or `All Equal` to fix character transition probabilities.
- **Heterogeneity Model**: Use `Gamma` or `Invariant Sites` to manipulate transition probabilities ([Reference](http://www.bioinf.man.ac.uk/resources/phase/manual/node81.html)).

### Clocks
Use the default `Strict clock`. Other options:
- `Uncorrelated relaxed clock` – can be tested to see effects on posterior probability.
- Results can be analyzed using tools like [Tracer](https://beast.community/tracer).

### Trees
You can choose from different tree priors:
- **Constant Size** (default)
- **Yule Process** (recommended alternative)

There are options for selecting starting trees, but they generally do not impact final results.

### States
- Tick `Reconstruct states at all ancestors` for a full tree reconstruction.
- Alternatively, select a specific node at `Reconstruct states at ancestor:` to simplify analysis.
- If you created the Taxon set in `Taxa`, you should see `MRCA(Proto-IE)` as an option.

### Priors & Operators
Skip these sections.

### MCMC
- You can modify the **tree sampling process length** and **character state sampling frequency**, but default settings are reasonable.

### Generate BEAST File
Finally, click on `Generate BEAST File…` to generate the `table.xml` file, which will be used in the BEAST analysis.

## 3. Running the BEAST Analysis

Running the phylogenetic analysis should be as easy as launching BEAST and selecting the `table.xml` file generated in the previous step as the source of the data. However, on my MacBook Air (M1, 2020), I encountered the following error:

> "Fatal exception: No acceptable BEAGLE library plugins found. Make sure that BEAGLE is properly installed or try changing resource requirements"

I followed the instructions at [BEAGLE Installation Guide](https://beast.community/beagle) to install the BEAGLE library, but the error persisted. The only workaround I found was running BEAST from the command line using `/lib/beast.jar` from the BEAST directory:

```sh
java -Djava.library.path=/usr/local/lib -jar beast.jar table.xml
```

Since BEAGLE was installed under `/usr/local/lib`, this was sufficient to trigger the analysis.

## 4. Reconstructed States

The output of the phylogenetic analysis should be:

- `table.trees` – contains the phylogenetic tree and can be used with [FigTree](https://beast.community/figtree).
- `table.log` – can be used with [Tracer](https://beast.community/tracer) to visualize the log-likelihood of the tree and determine whether the settings were appropriate for the dataset.
- `table.table.states.log` – contains the reconstructed states.

### Understanding `table.table.states.log`

This file will have the following format:

```
# BEAST v1.10.4 Prerelease #bc6cbd9
# Generated Sun Feb 09 16:31:59 GMT 2025 [seed=1739118718494]
# table.xml
state	 table
0	    "111010100110010100001111000010001010001110100000110000001100101101001000100011111101110001100"
1000	"101000001010001000110010011101001011000101110100100101101111001011100001000111001110101011110"
...
```

The binary strings represent the states reconstructed at the target node when the tree was sampled during the MCMC run. To make it more human-readable, you can use a simple Python script:

```python
from collections import Counter

dict = Counter()

i = 0
for line in open('table.table.states.log'):
    if i > 3:
        pars = line.split()[-1]
        new_pars = pars[1:].strip('"')
        for index, ch in enumerate(new_pars):
            dict[index] += int(ch)
    i += 1

for item in dict.items():
    # Instead of hard coding the number of samples, we should tie to i, since the number of samples should always be i-4
    print(round(item[1] / float(10001), 3))
```

This will print a list of ratios for each character position, representing the likelihood of a `1` at that particular state.

**Note:** If the taxon set contained only undefined characters (`??????`), those characters are skipped in the analysis. If your taxon set had 90 characters but character `50` was undefined, the final reconstruction will contain only 89 characters. Ensure that you remove `50` from your positional mapping (e.g., `[1,2,3,…,49,51,52,…]`).
