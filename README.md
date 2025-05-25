# ACCESS DENIED INC: The First Benchmark Environment for Sensitivity Awareness

## Table of Contents

1. **[Setting up the Environment](#setting-up-the-environment)**
2. **[Project Structure](#project-structure)**
3. **[Generating Mock-Corporate Datasets](#generating-mock-corporate-datasets)**
4. **[Sensitivity Awareness Questionnaires](#sensitivity-awareness-questionnaire)**
5. **[Running and Grading Models](#running-and-grading-models)**
    
    5.1 **[Autograding](#autograding)**

    5.2 **[Manual Grading (Optional)](#manual-grading-optional)**

6. **[Performance Evaluation](#performance-evaluation)**

## Setting up the Environment

To reproduce and repurpose our existing software pipeline, users/researchers need the following software components:
1. **Python 3:** The project currently relies 100% on Python. Therefore, Python must be pre-installed. Python for your operating system (if not already pre-installed) can be downloaded from the following link: https://www.python.org/downloads/
2. **Miniconda:** Within this codebase, virtual Python environments are set up using Conda. Such environments allow us to manage project-relevant packages within a separate Python instance. For more information on Conda, see: https://docs.conda.io/projects/conda/en/latest/user-guide/getting-started.html
3. **C++ Build Tools (Windows only):** If this is your first time working with Python packages such as `numpy`, you may also need to setup Microsoft C++ build tools. Below, you can find (ChatGPT generated!) setup instructions:

    - Go to https://visualstudio.microsoft.com/visual-cpp-build-tools/
    - Download and install.
    - During installation, select "C++ build tools" and include the Windows 10/11 SDK.
    - Restart your terminal or IDE after installation.

Assuming that everything went smoothly, you should now be able to create virtual environments via conda. However, you first need to download the repository via `git clone`:
```bash
git clone https://github.com/DrenFazlija/AccessDeniedInc.git
```

Next, a virtual Python environment must be set up using `conda` and configured with the appropriate Python packages. The Python version used for this project is `3.10.0`.

**1. Create Conda Environment**
```bash 
conda create -n accessdeniedinc python=3.10.0
```

**2. Activate Conda Environment and Install Packages**
```bash
cd AccessDeniedInc # Change to the Repository Directory
conda activate accessdeniedinc
conda install pip # necessary for some conda versions
pip install -r requirements.txt
```

## Project Structure

The repository is organized into the following main directories:

- `acl_2025/`: Contains all the data generated as part of our ACL 2025 Findings paper (questionnaires, model output, grades, etc.)
- `scripts/`: Contains all Python scripts for data processing, model running, and evaluation
  - `adult_transformation.py`: Transforms the Adult dataset into corporate format
  - `questionnaire.py`: Generates sensitivity awareness questionnaires
  - `grade.py`: Handle automated grading
  - `annotate.py`: Facilitates manual annotation
  - `utils.py`: Contains utility functions
  - `results.ipynb`: Summarize the results of all experiments
  - Various API integration scripts (see below)

## Generating Mock-Corporate Datasets

First, researchers need to download the publicly available Adult dataset, as it is the foundation of our synthetic dataset. This can be achieved (for example) via the following `curl` command:

```bash
curl --output adult.tar.gz "ftp://ftp:cs.toronto.edu/pub/neuron/delve/data/tarfiles/adult.tar.gz"
```

Afterwards, please unpack the Adult dataset under the main folder of this repository with the folder name `adult`. 

To generate ACCESS DENIED INC corporate datasets (associated with a seed), we first need to switch to the `scripts` directory. We can then repurpose and transform the Adult dataset via the following command:

```bash
python adult_transformation.py
```

## Sensitivity Awareness Questionnaire
Given a generated mock-corporate dataset, we can now generate `n`-many questionnaire based on the data. Each questionnaire is associated with a single seed and is the generated with the following command:

```bash
python questionnaire.py --seed 0
```

Other parameters, such as number of documents (`DOCS`) and iterations (`ITERATIONS`), are defined as global variables in the script. Please do not adjust them unless you deem it necessary for your setup!

## Running and Grading Models

We first recommend that you create a single file where you store your API keys (however, you can of course manage API keys in which ever way you please). For our scripts below, we simply create a hidden directory `.api_keys` in our main directory with the file `keys.json`.

In the `scripts` directory, you can find some exemplary Python and Slurm scripts with which we ran our experiments. These scripts include code for the following API platforms:

- OpenAI: `openai_api.py` / `openai.sh` (Models: GPT-4 family)
- Huggingface API Service: `huggingface.py` / `hf.sh` (Models: Llama 2 70B, Llama 2 3B, Qwen 32B) 
- OpenRouter: `openrouter_api.py` / `or.sh` (Models: Grok-2, Phi 4)

The repository includes Slurm integration for running experiments on HPC clusters. Each API has an associated `.sh` script that can be submitted to a Slurm scheduler. However, as we were not actively using on-site GPUs, you can alternatively copy the corresponding `python` command and annotate your data directly. Please check the corresponding credentials function in `scripts/utils.py` to see the expected format for the different `get_credentials` calls in each script.

> [!NOTE]
> If one of the above scripts did not produce a batch_output.csv file, then feel to create it via the `get_clean.py` file.

### Autograding
Each of the above code snippets should produce a `batch_output.csv` file in your model-specific inputs directory. To perform *automated* grading, simply pass the corresponding file directory to the `grade.py` file in the `scripts` directory:

```bash
python grade.py <path-to-your-model-output>/batch_output.csv
```

The above command generates two files `auto_graded.csv` which contains all output information including ACCESS DENIED INC. grades and `auto_graded_labels.csv` which just lists each query id with its respective grade.

### Manual Grading (Optional)
Based on the generated `auto_graded.csv` file, one can now perform manually grading via by running the `annotate.py` script:

```bash
python annotate.py --outputs <path-to-your-model-output>/auto_graded.csv
```

## Performance Evaluation
We created a notebook (`scripts/results.ipynb`) to process the automated grades (including entries which were graded with -1, i.e., "requires manual grading"). Feel free to repurpose the code for your needs!

## License
This project is made available under the MIT License. You are free to:
- Use the code for any purpose
- Modify the code to suit your needs
- Distribute your modified versions
- Use the code for commercial purposes

We only ask that you acknowledge the original work by citing our paper when using this code in your research.

## Citation
If you use this code in your research, please cite our paper:
```bibtex
@inproceedings{fazlija2025accessdeniedinc,
      title={ACCESS DENIED INC: The First Benchmark Environment for Sensitivity Awareness},
      author = {Fazlija, Dren and Orlov, Arkadij and Sikdar, Sandipan},
      booktitle={Findings of the Association for Computational Linguistics: ACL 2025},
      year={2025}
}
```