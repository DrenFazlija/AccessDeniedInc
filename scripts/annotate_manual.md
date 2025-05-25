# Annotation Manual

1. Create questionnaire.
2. Run one of the API scripts. Nova_l3s_api, whatever.
3. These scripts all auto-grade (call grade.py). The auto-graded file is called `auto_graded.csv` for which a `auto_graded_labels.csv` exists.
4. With the auto-graded file (not the labels!), call for example `python annotate.py --outputs ../experiments/baseline_english/gemma2_9b-instruct-fp16/auto_graded.csv`
