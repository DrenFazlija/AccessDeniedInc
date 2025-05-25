import shutil
from itertools import product, chain
from numpy.random import random, choice, seed as np_seed
import numpy as np
import pandas as pd
import os
import tarfile
from names_dataset import NameDataset
from numpy.random import randint
import gzip

def extract_files(tar_file_path, gz_file_path, output_file_path):
    print("Extracting files from archive...")
    with tarfile.open(tar_file_path, "r:gz") as tar:
        tar.extractall(path="../", filter=lambda x, _: x)

    print("Decompressing data file...")
    with gzip.open(gz_file_path, 'rb') as f_in:
        with open(output_file_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    print("File extraction complete.")

def generate_names(num_names):
    print(f"Generating {num_names} random names...")
    nd = NameDataset()
    fn = nd.get_top_names(20_000, use_first_names=True)
    ln = nd.get_top_names(20_000, use_first_names=False)

    first_names = []
    last_names = []

    for _, d in fn.items():
        d = d.values()
        d = list(chain(*d))
        first_names.extend(list(filter(lambda x: all(ord(c) < 128 for c in x), d)))

    for _, d in ln.items():
        last_names.extend(list(filter(lambda x: all(ord(c) < 128 for c in x), d)))

    names = [(first_names[randint(0, 20_000)], last_names[randint(0, 20_000)]) for _ in range(num_names)]
    print("Name generation complete.")
    return names

def assign_roles(df, leads, depts):
    def roles(x):
        if random() <= 0.05 and x['income'] == '>50K' and len(leads) > 0:
            idx = choice(range(len(leads)))
            dept = leads.pop(idx)
            role = f"{dept} Lead" if dept not in ['COO/CCO', 'CEO', 'CFO'] else dept
        else:
            role = choice(depts)
        return role

    df['position'] = df.apply(roles, axis=1)
    return df

def find_supervisor(df):
    def supervisor(x):
        if x['position'] in ['COO/CCO', 'CEO', 'CFO']:
            return x['first_name'] + ' ' + x['last_name']
        elif x['position'].endswith('Lead'):
            return x['first_name'] + ' ' + x['last_name']
        else:
            return df[df['position'] == x['position'] + ' Lead'].apply(
                lambda x: x['first_name'] + ' ' + x['last_name'], axis=1
            ).iloc[0]

    df['supervisor'] = df.apply(supervisor, axis=1)
    return df

def assign_salaries(df):
    salaries = (30000 + np.random.normal(50_000, 15_000, 20000)).astype(int)
    sals = [s for s in salaries if 35_000 <= s <= 200_000]
    df['income'] = df['income'].apply(lambda x: np.random.choice(sals))
    return df

def pick_role(department, departments_roles_quotas):
    if department.endswith('Lead') or department in ['COO/CCO', 'CEO', 'CFO']:
        return department
    roles = [role['role'] for role in departments_roles_quotas[department]]
    quotas = [role['quota'] for role in departments_roles_quotas[department]]
    total_quota = sum(quotas)
    probabilities = [quota / total_quota for quota in quotas]
    return np.random.choice(roles, p=probabilities)

def main(tar_file_path, gz_file_path, output_file_path, num_names, employees_minimum, departments_roles_quotas, dataset_path='../datasets', seed=None):
    print("Starting data transformation process...")
    if seed is not None:
        print(f"Setting random seed to {seed}")
        np_seed(seed)

    assert os.access(tar_file_path, mode=os.F_OK), f"File not found: '{tar_file_path}'"

    extract_files(tar_file_path, gz_file_path, output_file_path)

    names = generate_names(num_names)

    print("Reading and processing base dataset...")
    columns = ["age", "workclass", "fnlwgt", "education", "educational-num", "marital-status", "occupation", "relationship", "race", "gender", "capital-gain", "capital-loss", "hours-per-week", "native-country", "income"]
    df = pd.read_csv(output_file_path, sep=' ', names=columns, na_values='?', skipinitialspace=True)
    df = df.dropna()

    print("Adding names to dataset...")
    df['first_name'] = [names[i][0] for i in range(min(len(names), len(df)))]
    df['last_name'] = [names[i][1] for i in range(min(len(names), len(df)))]
    df = df[['first_name', 'last_name'] + [c for c in df.columns[:-2]]]

    os.makedirs(dataset_path, exist_ok=True)
    print(f"Saving dataset with names to {dataset_path}/adult_with_names.csv")
    df.to_csv(f'{dataset_path}/adult_with_names.csv', index=False)

    print("Assigning roles to employees...")
    leads = ['Audit', 'Legal', 'HR', 'Renewables', 'Assets', 'COO/CCO', 'Asset Management', 'Internal Infrastructure', 'Corporate IT', 'IT Trading', 'IT', 'Accounting & Finance', 'CFO', 'CEO']
    depts = ['Audit', 'Legal', 'HR', 'Renewables', 'Assets', 'Asset Management', 'Internal Infrastructure', 'Corporate IT', 'IT Trading', 'Accounting & Finance']

    df = assign_roles(df, leads, depts)

    managers = df[df['position'].str.contains('Lead') | df['position'].isin(["CEO", "CFO", "COO/CCO"])]

    print("Saving dataset with positions...")
    if employees_minimum:
        idxs = list(set(managers.index.tolist() + list(range(employees_minimum))))
        df.iloc[idxs].to_csv(f'{dataset_path}/adult_with_position.csv', index=False, encoding='utf-8')
    else:
        df.to_csv(f'{dataset_path}/adult_with_position.csv', index=False, encoding='utf-8')

    print("Assigning supervisors...")
    df = find_supervisor(df)
    print("Saving dataset with supervisors...")
    df.to_csv(f'{dataset_path}/adult_with_supervisor.csv', index=False, encoding='utf-8')

    print("Assigning salaries...")
    df = assign_salaries(df)
    print("Saving dataset with income...")
    df.to_csv(f'{dataset_path}/adult_with_income.csv', index=False)

    print("Creating final dataset with selected columns...")
    df = pd.read_csv(f'{dataset_path}/adult_with_income.csv')
    for c in ["workclass", "fnlwgt", "educational-num", "relationship", "capital-gain", "capital-loss"]:
        df.drop(c, axis=1, inplace=True)

    df.to_csv(f'{dataset_path}/adult_less_columns.csv', index=False)

    print("Adding roles and IDs...")
    df = pd.read_csv(f'{dataset_path}/adult_less_columns.csv')
    df.rename(columns={'position': 'department'}, inplace=True)

    df['role'] = df.apply(lambda x: pick_role(x['department'], departments_roles_quotas), axis=1)
    df['department'] = df['department'].apply(lambda x: x if not x.endswith('Lead') else x[:-5])

    df['id'] = df['first_name'].str[0] + (df.index + 1).astype(str).str.zfill(4)
    assert df['id'].duplicated().sum() == 0
    print("Saving final dataset...")
    df.to_csv(f'{dataset_path}/adult_with_id_roles.csv', index=False)
    print("Data transformation complete!")

if __name__ == "__main__":
    tar_file_path = "../adult.tar.gz"
    gz_file_path = "../adult/Dataset.data.gz"
    output_file_path = "../adult/Dataset.data"
    dataset_path = '../mock_data'
    num_names = 50000
    employees_minimum = None
    departments_roles_quotas = {
        "Renewables": [
            {"role": "Renewable Energy Analyst", "quota": 30},
            {"role": "Solar Technician", "quota": 20},
            {"role": "Wind Turbine Technician", "quota": 10}
        ],
        "Assets": [
            {"role": "Asset Analyst", "quota": 25},
            {"role": "Asset Coordinator", "quota": 20},
            {"role": "Asset Technician", "quota": 13}
        ],
        "Internal Infrastructure": [
            {"role": "Infrastructure Engineer", "quota": 25},
            {"role": "Network Technician", "quota": 20},
            {"role": "System Administrator", "quota": 13}
        ],
        "Corporate IT": [
            {"role": "IT Support Specialist", "quota": 20},
            {"role": "System Analyst", "quota": 20},
            {"role": "Database Administrator", "quota": 15}
        ],
        "HR": [
            {"role": "HR Specialist", "quota": 20},
            {"role": "Recruiter", "quota": 15},
            {"role": "HR Coordinator", "quota": 17}
        ],
        "IT Trading": [
            {"role": "Quantitative Analyst", "quota": 30},
            {"role": "Trading Systems Developer", "quota": 10},
            {"role": "Trading Support Analyst", "quota": 10}
        ],
        "Audit": [
            {"role": "Internal Auditor", "quota": 20},
            {"role": "Compliance Analyst", "quota": 15},
            {"role": "Audit Assistant", "quota": 13}
        ],
        "Asset Management": [
            {"role": "Portfolio Analyst", "quota": 20},
            {"role": "Asset Manager", "quota": 12},
            {"role": "Investment Analyst", "quota": 10}
        ],
        "Legal": [
            {"role": "Legal Assistant", "quota": 15},
            {"role": "Paralegal", "quota": 12},
            {"role": "Contract Specialist", "quota": 12}
        ],
        "Accounting & Finance": [
            {"role": "Financial Analyst", "quota": 15},
            {"role": "Accountant", "quota": 12},
            {"role": "Accounts Payable Specialist", "quota": 9}
        ]
    }
    
    seed = 0

    dataset_path = f'{dataset_path}'

    main(tar_file_path, gz_file_path, output_file_path, num_names, employees_minimum, departments_roles_quotas, dataset_path, seed)
