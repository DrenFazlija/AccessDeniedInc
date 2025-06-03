# ACCESS DENIED INC

[![license badge](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

<p align="center">
  <img src="./images/l3s-logo-c.webp" align="middle" width="200"/>
</p>



### 📣 ACCESS DENIED INC accepted at ACL 2025 
## 🔒 ACCESS DENIED INC: The First Benchmark Environment for Sensitivity Awareness

<p align="center">
  <a href="https://arxiv.org/abs/2506.00964" style="font-size: 24px; text-decoration: none">The Preprint is now Online!</a>
</p>

<p align="center">
  <img src="./images/accessdeniedinc.png" align="middle" width="600"/>
</p>

<p align="center">
  <a href="https://www.linkedin.com/in/drenfazlija">Dren Fazlija</a><sup>1,*</sup>,
  <a href="https://www.linkedin.com/in/arkadijorlov/">Arkadij Orlov</a><sup>2,*</sup>, 
  <a href="https://www.linkedin.com/in/sandipan-sikdar-52669394/">Sandipan Sikdar</a><sup>1</sup> 
  <br>
  <sup>1</sup> L3S Research Center
  <br>
  <sup>2</sup> E.ON Grid Solutions
  <br>
  <sup>*</sup> Equal Contributions
</p>

### Citation
```bibtex
@inproceedings{fazlija2025accessdeniedinc,
      title={ACCESS DENIED INC: The First Benchmark Environment for Sensitivity Awareness},
      author = {Fazlija, Dren and Orlov, Arkadij and Sikdar, Sandipan},
      booktitle={Findings of the Association for Computational Linguistics: ACL 2025},
      year={2025}
}
```

## Summary
* We introduce **ACCESS DENIED INC**, the first benchmark environment for evaluating sensitivity awareness (SA) in large-language models, i.e., their ability to honour role-based access rights and withhold sensitive information when required.
* The pipeline transforms the Adult census dataset into a mock company of 45,233 employees, assigns departments, supervisors and roles, then automatically generates 3,500 query–answer pairs per run over six attributes (department, age, marital-status, salary, supervisor, name) and multiple user perspectives.
* Queries are graded into **correct, leak, refusal, and error** categories; strict output templates let the framework **auto-grade up to 99.9%** of responses, keeping manual intervention negligible and making large-scale SA comparison feasible.
* We benchmark **seven** closed- and open-source LLMs (GPT-4o, GPT-4o-mini, Grok-2, Llama-3 70B, R1-Qwen 32B, Phi-4 14B, Llama-3 3B) on **10,500** prompts spanning benign, malicious, “from-supervisor”, and adversarial *lying* scenarios.
* **Overall SA correctness:** Grok-2 80.50%, GPT-4o 70.72%, Llama-3 70B 60.81%; Grok-2 shows only 0.22% formatting errors, while Llama-3 70B records 38.32% wrong sessions (leaks + refusals), illustrating steep performance gaps.
* **Malicious-request stress-test:** Grok-2 answers safely in **65.48%** cases but still leaks **33.48%**; Llama-3 70B leaks in **74.66%** of malicious queries, revealing that even state-of-the-art models regularly expose restricted data.
* **Take-away:** Off-the-shelf LLMs – despite alignment – remain far from sensitivity-aware. Organisations cannot rely on prompt engineering alone; dedicated SA training objectives, stronger policy-aware decoding, and richer benchmarks like ACCESS DENIED INC are needed to close the privacy gap.

<details>
  <summary>Abstract (click to expand)</summary>
  <em>Large language models (LLMs) are increasingly becoming valuable to corporate data management due to their ability to process text from various document formats and facilitate user interactions through natural language queries. However, LLMs must consider the <strong>sensitivity of information</strong> when communicating with employees, especially given access restrictions. Simple filtering based on user clearance levels can pose both performance and privacy challenges. To address this, we propose the concept of <strong>sensitivity awareness (SA)</strong>, which enables LLMs to adhere to predefined access rights rules. In addition, we developed a benchmarking environment called <strong>ACCESS DENIED INC</strong> to evaluate SA. Our experimental findings reveal significant variations in model behavior, particularly in managing unauthorized data requests while effectively addressing legitimate queries. This work establishes a foundation for benchmarking sensitivity-aware language models and provides insights to enhance privacy-centric AI systems in corporate environments.</em>
</details>